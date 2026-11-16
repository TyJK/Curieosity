import csv
import json
import os
import time
import logging
from typing import Dict, Any, List

# Import your toolchain
from inspect_full_compound import CompoundInspector
from synthesize_compound_schema import SchemaSynthesizer
from cas_client import CasClient

# --- Configuration ---
INPUT_CSV = "tools/data/master_compound_list.csv"
OUTPUT_DIR = "tools/data/full_compounds"
MASTER_FILE = "tools/data/inorganic_library.json"
FAILURE_LOG = "tools/data/ingestion_failures.csv"
SLEEP_BETWEEN_CALLS = 1.0 # Reduced for retry, but respectable

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tools/data/batch_ingest_recovery.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("BatchOrchestrator")

class BatchOrchestrator:
    def __init__(self):
        self.inspector = CompoundInspector()
        self.cas_client = CasClient()
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def get_existing_ids(self) -> set:
        existing = set()
        for filename in os.listdir(OUTPUT_DIR):
            if filename.endswith(".json") and filename != "temp_processing.json":
                cas_rn = filename.replace(".json", "")
                existing.add(cas_rn)
        return existing

    def resolve_structure_robust(self, row: Dict[str, str]) -> str:
        """
        Robust resolver for Recovery Mode.
        Prioritizes CAS API -> CSV SMILES -> CSV Name -> Cleaned Name.
        """
        cas_rn = row.get("CAS", "").strip()
        name = row.get("NAME", "").strip()

        # 1. CAS API (Best source)
        if cas_rn:
            try:
                details = self.cas_client.get_details(cas_rn)
                smiles = details.get("canonicalSmile")
                if smiles: return smiles

                # If CAS has a specific name, use that over CSV name
                cas_name = details.get("name")
                if cas_name: return cas_name
            except Exception:
                pass

        # 2. CSV SMILES
        if row.get("SMILES"): return row["SMILES"]

        # 3. CSV Name
        if name: return name

        # 4. Fallback: Clean the name? (e.g. remove " solution")
        if name and " solution" in name.lower():
            return name.lower().replace(" solution", "").strip()

        return "Unknown"

    def parse_csv_list(self, raw_str: str) -> List[str]:
        if not raw_str: return []
        clean_str = raw_str.split("[source")[0]
        return [x.strip() for x in clean_str.split(";") if x.strip()]

    def enrich_record(self, final_data: Dict[str, Any], row: Dict[str, Any]):
        if "game_data" not in final_data: final_data["game_data"] = {}

        # Industrial Data
        final_data["game_data"]["industrial"] = {
            "production_volume_lbs": row.get("PRODUCTION_VOLUME_LBS", "Unknown"),
            "production_year": row.get("PRODUCTION_VOLUME_2019", "Unknown"),
            "industrial_site_count": row.get("INDUSTRIAL_SITE_COUNT", "Unknown"),
            "is_recycled": row.get("RECYCLED") == "Yes"
        }

        # Context Lists
        if "context_lists" not in final_data: final_data["context_lists"] = {}

        csv_sectors = self.parse_csv_list(row.get("INDUSTRIAL_SECTORS"))
        csv_functions = self.parse_csv_list(row.get("INDUSTRIAL_FUNCTIONS"))
        csv_consumer = self.parse_csv_list(row.get("CONSUMER_FUNCTIONS"))

        current_uses = set(final_data["context_lists"].get("industrial_uses", []))
        current_uses.update(csv_sectors)
        current_uses.update(csv_functions)

        final_data["context_lists"]["industrial_uses"] = sorted(list(current_uses))
        final_data["context_lists"]["consumer_uses"] = sorted(csv_consumer)

        # Provenance
        if "meta" not in final_data: final_data["meta"] = {}
        final_data["meta"]["csv_source_data"] = row

    def log_failure(self, row: Dict, reason: str):
        file_exists = os.path.isfile(FAILURE_LOG)
        with open(FAILURE_LOG, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["CAS", "NAME", "REASON"])
            writer.writerow([row.get("CAS"), row.get("NAME"), reason])

    def run_recovery(self):
        """
        Runs ONLY on items that do NOT exist in the output directory.
        Uses relaxed validation.
        """
        logger.info("Starting RECOVERY Ingestion...")
        done_ids = self.get_existing_ids()
        logger.info(f"Existing records: {len(done_ids)}")

        processed_count = 0
        failure_count = 0

        with open(INPUT_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader) # Read all to memory to show progress

        total_rows = len(rows)
        logger.info(f"Total input rows: {total_rows}")

        for i, row in enumerate(rows):
            cas_rn = row.get("CAS", "Unknown").strip()
            name = row.get("NAME", "Unknown").strip()

            if not cas_rn or cas_rn == "Unknown":
                continue # Can't save without ID

            # Skip if already done
            if cas_rn in done_ids:
                continue

            logger.info(f"RECOVERY Attempt {i+1}/{total_rows}: {name} ({cas_rn})")

            try:
                # A. Resolve
                search_term = self.resolve_structure_robust(row)
                if not search_term or search_term == "Unknown":
                    self.log_failure(row, "Could not resolve valid search term")
                    failure_count += 1
                    continue

                # B. Inspect (With known CAS force)
                raw_record = self.inspector.inspect(search_term, known_cas_rn=cas_rn)

                # Check if inspection actually found anything useful
                # If strictly empty, synthesiser might produce a skeleton. That's okay for recovery.

                # C. Synthesize
                temp_path = os.path.join(OUTPUT_DIR, "temp_rec.json")
                with open(temp_path, 'w') as tf: json.dump(raw_record, tf)

                synthesizer = SchemaSynthesizer(temp_path)
                synthesizer.synthesize()

                # D. Validate Result
                # If name is "Unknown" AND SMILES is missing, it's a ghost record.
                ident = synthesizer.final_data.get("identity", {})
                if (not ident.get("name") or ident.get("name") == "Unknown") and not ident.get("smiles"):
                    # Final ditch: Force the CSV name if Synthesis failed to find one
                    synthesizer.final_data["identity"]["name"] = name
                    synthesizer.provenance["name"] = {"value_source": "CSV Recovery", "confirmed_by": []}

                # E. Enrich
                self.enrich_record(synthesizer.final_data, row)

                # F. Save
                safe_filename = f"{cas_rn}.json"
                out_path = os.path.join(OUTPUT_DIR, safe_filename)
                synthesizer.save(out_path)

                processed_count += 1
                time.sleep(SLEEP_BETWEEN_CALLS)

            except Exception as e:
                logger.error(f"CRITICAL FAIL on {name}: {e}")
                self.log_failure(row, str(e))
                failure_count += 1

        logger.info(f"Recovery Complete. Recovered: {processed_count}. Failed: {failure_count}")

if __name__ == "__main__":
    orchestrator = BatchOrchestrator()
    orchestrator.run_recovery()