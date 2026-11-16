import os
import json
import requests
import logging
import sys
import time
import concurrent.futures
from multiprocessing import cpu_count
from tqdm import tqdm

# Setup paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from ord_client import OrdClient
    from ingest_reactions import ReactionIngestor
    from ord_schema.proto import dataset_pb2
    from ord_schema import message_helpers
    from rdkit import Chem
    from rdkit import RDLogger
except ImportError:
    print("❌ Error: Missing dependencies.")
    sys.exit(1)

RDLogger.DisableLog('rdApp.*')

# --- CONFIGURATION ---
COMPOUNDS_DIR = "./tools/data/18_final_canon_compounds"
OUTPUT_DIR = "./tools/data/reaction_dataset"
TEMP_DIR = "./tools/data/ord_temp"
LOG_DIR = "./tools/logs"
HISTORY_FILE = os.path.join(LOG_DIR, "processed_datasets.txt")
GITHUB_API_BASE = "https://api.github.com/repos/open-reaction-database/ord-data/contents/data"

# Auto-detect CPUs (Leave 1 free for system)
MAX_WORKERS = max(1, cpu_count() - 1)

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(level=logging.ERROR, format='%(asctime)s | %(message)s')
logger = logging.getLogger("ParallelIngest")

# --- FORENSIC HISTORY LOGIC (Ported from v5) ---
def rebuild_history_from_disk():
    """Scans existing reaction JSONs to find which source datasets are fully ingested."""
    print("🕵️  Forensic Scan: Checking existing reaction files for source metadata...")

    if not os.path.exists(OUTPUT_DIR):
        return set()

    found_sources = set()
    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".json")]

    # We scan the actual output to see what we have already finished
    # Sampling 10% of files for speed vs accuracy trade-off?
    # No, for correctness we must scan all. It's fast on SSD (metadata is at end of file).
    for f in tqdm(files, desc="Scanning Output"):
        try:
            with open(os.path.join(OUTPUT_DIR, f), 'r', encoding='utf-8') as h:
                data = json.load(h)
                src = data.get("_metadata", {}).get("source_dataset")
                if src:
                    found_sources.add(src)
        except: pass

    # Update the history file so we don't have to scan again next time
    with open(HISTORY_FILE, 'w') as f:
        for src in sorted(list(found_sources)):
            f.write(f"{src}\n")

    print(f"✅ Recovered {len(found_sources)} completed datasets from disk.")
    return found_sources

def load_history():
    """Loads history from file. If missing/empty, triggers forensic scan."""
    if os.path.exists(HISTORY_FILE) and os.path.getsize(HISTORY_FILE) > 0:
        with open(HISTORY_FILE, 'r') as f:
            return set(line.strip() for line in f if line.strip())

    # If text file is missing, rebuild it from the actual data folder
    return rebuild_history_from_disk()

def append_history(filename):
    """Thread-safe append (mostly, since only main thread calls this)."""
    with open(HISTORY_FILE, 'a') as f:
        f.write(f"{filename}\n")

# --- WORKER LOGIC ---
worker_targets = None
worker_ingestor = None

def init_worker(targets):
    """Initializes the worker process with the target set and ingestor."""
    global worker_targets, worker_ingestor
    worker_targets = targets
    worker_ingestor = ReactionIngestor()

def canonicalize(smiles):
    if not smiles: return None
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol: return Chem.MolToSmiles(mol, canonical=True, isomericSmiles=False)
    except: pass
    return smiles

def load_targets():
    print(f"📂 Loading targets from {COMPOUNDS_DIR}...")
    targets = set()
    files = [f for f in os.listdir(COMPOUNDS_DIR) if f.endswith(".json")]
    for f in tqdm(files, desc="Indexing"):
        try:
            with open(os.path.join(COMPOUNDS_DIR, f), 'r', encoding='utf-8') as h:
                data = json.load(h)
                smi = data.get("identity", {}).get("smiles") or data.get("compound", {}).get("identity", {}).get("smiles")
                if smi:
                    targets.add(smi)
                    c = canonicalize(smi)
                    if c: targets.add(c)
        except: pass
    return targets

def get_download_urls():
    print("🕸️  Crawling ORD API...")
    urls = []
    try:
        resp = requests.get(GITHUB_API_BASE)
        if resp.status_code == 403: return []
        folders = [i['name'] for i in resp.json() if i['type'] == 'dir']

        for folder in tqdm(folders, desc="Scanning Directories"):
            r = requests.get(f"{GITHUB_API_BASE}/{folder}")
            if r.status_code == 200:
                for f in r.json():
                    if f['name'].endswith('.pb.gz') and f.get("download_url"):
                        lfs_url = f"https://media.githubusercontent.com/media/open-reaction-database/ord-data/main/data/{folder}/{f['name']}"
                        urls.append(lfs_url)
    except: pass
    return urls

def process_single_dataset(url):
    filename = url.split("/")[-1]
    # Unique temp file for this process to avoid collisions
    temp_path = os.path.join(TEMP_DIR, f"{os.getpid()}_{filename}")
    hits = 0

    try:
        if not os.path.exists(temp_path):
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(temp_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

        with open(temp_path, 'rb') as f:
            if f.read(2) != b'\x1f\x8b':
                os.remove(temp_path)
                return (filename, 0, "Invalid GZIP")

        dataset = message_helpers.load_message(temp_path, dataset_pb2.Dataset)
        local_targets = worker_targets

        for reaction in dataset.reactions:
            is_match = False

            def check(ids):
                for i in ids:
                    if i.type == 2:
                        if i.value in local_targets: return True
                        if len(i.value) < 400:
                            c = canonicalize(i.value)
                            if c and c in local_targets: return True
                return False

            for inp in reaction.inputs.values():
                for comp in inp.components:
                    if check(comp.identifiers): is_match = True; break
                if is_match: break

            if is_match:
                try:
                    raw = {
                        "reactionId": reaction.reaction_id,
                        "inputs": {}, "outcomes": [], "conditions": {}, "notes": {}
                    }
                    if reaction.notes.procedure_details: raw["notes"]["procedure"] = reaction.notes.procedure_details
                    if reaction.conditions.temperature.setpoint.value:
                        raw["conditions"]["temperature"] = {"value": reaction.conditions.temperature.setpoint.value}

                    for k, v in reaction.inputs.items():
                        comps = []
                        for c in v.components:
                            ids = [{"type": "SMILES", "value": x.value} for x in c.identifiers if x.type == 2]
                            if ids: comps.append({"identifiers": ids})
                        if comps: raw["inputs"][k] = {"components": comps}

                    for o in reaction.outcomes:
                        prods = []
                        oy = 0.0
                        for p in o.products:
                            ids = [{"type": "SMILES", "value": x.value} for x in p.identifiers if x.type == 2]
                            if ids: prods.append({"identifiers": ids})
                            for m in p.measurements:
                                if m.type == 3 and m.percentage.value: oy = m.percentage.value
                        out_d = {"products": prods}
                        if oy > 0: out_d["yield_percent"] = oy
                        raw["outcomes"].append(out_d)

                    final, _ = worker_ingestor.process(raw)
                    final["_metadata"]["source_dataset"] = filename

                    with open(os.path.join(OUTPUT_DIR, f"rxn_{reaction.reaction_id}.json"), 'w') as f:
                        json.dump(final, f, indent=2)
                    hits += 1
                except: pass

    except Exception as e:
        return (filename, 0, str(e))

    if os.path.exists(temp_path):
        os.remove(temp_path)

    return (filename, hits, "OK")

def run():
    print(f"🚀 STARTING PARALLEL INGESTION ({MAX_WORKERS} Workers)")
    print("==========================================")

    targets = load_targets()
    if not targets: return

    all_urls = get_download_urls()
    if not all_urls: return

    # --- FORENSIC RESUMPTION ---
    history = load_history()
    pending_urls = [u for u in all_urls if u.split('/')[-1] not in history]

    print(f"\n📊 STATUS: {len(history)} files processed previously.")
    print(f"⚡ QUEUE:   {len(pending_urls)} datasets remaining.")

    if not pending_urls:
        print("✅ No new datasets to process. You are up to date.")
        return

    total_captured = 0

    try:
        with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS, initializer=init_worker, initargs=(targets,)) as executor:
            future_to_url = {executor.submit(process_single_dataset, url): url for url in pending_urls}

            with tqdm(total=len(pending_urls), desc="Processing Datasets") as pbar:
                for future in concurrent.futures.as_completed(future_to_url):
                    fname, hits, status = future.result()

                    if status == "OK":
                        total_captured += hits
                        append_history(fname)
                        pbar.set_postfix_str(f"Last: {fname} (+{hits})")
                    else:
                        pbar.set_postfix_str(f"Error: {fname} ({status})")

                    pbar.update(1)
    except KeyboardInterrupt:
        print("\n🛑 PAUSED by User.")
        sys.exit(0)

    print("\n" + "="*50)
    print(f"🏁 ALL DONE.")
    print(f"   Total Captured This Session: {total_captured}")
    print("="*50)

if __name__ == "__main__":
    run()