import logging
import sys
import os
import time

# Ensure we can import from the root
sys.path.append(os.getcwd())

from inspect_full_compound import CompoundInspector
from tools.ingestion.cas_client import CasClient
from synthesize_compound_schema import DataRefinery

# Configure logging to capture the Inspector's internal logic
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("MultiDebug")

# --- The Rogues Gallery ---
TARGETS = [
    # 1. The Success Case (Control)
    ("10034-99-8", "Magnesium sulfate heptahydrate"),

    # 2. Another Hydrate (Tests regex flexibility for comma separation)
    ("10035-04-8", "Calcium chloride, dihydrate"),

    # 3. A Common Salt (Tests if it falls back to the Acid or Base correctly)
    ("10043-01-3", "Aluminum sulfate"),

    # 4. A Volatile/Unstable Oxide (Tests Name Fallback for N2O5)
    ("10102-03-1", "Nitrogen oxide (N2O5)"),

    # 5. A Standard Industrial Chemical (Should just work via Name Fallback if Structure fails)
    ("7722-84-1", "Hydrogen peroxide"),

    # 6. An Inorganic Acid (Tests if formula/name matching holds up)
    ("10193-36-9", "Silicic acid (H4SiO4)"),

    # 7. An Element (Tests if the new CAS priority finds the right record)
    ("7429-91-6", "Dysprosium")
]

def debug_target(cas_rn, name):
    print(f"\n{'='*80}")
    print(f"🕵️‍♀️ DIAGNOSING: {name} ({cas_rn})")
    print(f"{'='*80}")

    # 1. Resolve Search Term (Mimic Batch Orchestrator)
    cas_client = CasClient()
    cas_data = cas_client.get_details(cas_rn)
    search_term = cas_data.get("canonicalSmile", name)
    print(f"[1] Search Term from CAS: {search_term}")

    # 2. Inspect
    print(f"[2] Running Inspector...")
    inspector = CompoundInspector()

    # Verify code version (Simple check)
    import inspect
    src = inspect.getsource(inspector.inspect)
    if "Early CAS Lookup" not in src and "EARLY CAS LOOKUP" not in src:
        print("🚨 WARNING: Inspector code might not be updated! Checking anyway...")

    start = time.time()
    raw_record = inspector.inspect(search_term, known_cas_rn=cas_rn)
    duration = time.time() - start

    # 3. Analyze Data
    ctx = raw_record.get("identity", {}).get("pubchem_context", {})
    props = ctx.get("experimental_properties", {})

    mp = props.get("melting_point")
    density = props.get("density")

    # 4. Result
    print(f"\n[3] Results ({duration:.2f}s):")
    print(f"    - Resolved Name: {raw_record.get('meta', {}).get('resolved_name')}")
    print(f"    - MP (Raw):      {mp}")
    print(f"    - Density (Raw): {density}")

    refinery = DataRefinery()
    if mp:
        clean_mp = refinery.normalize_temperature(mp)
        print(f"    - MP (Clean):    {clean_mp} K")
    else:
        print(f"    - MP (Clean):    None")

    if mp or density:
        print("    ✅ SUCCESS: Physics Data Found.")
    else:
        print("    ❌ FAILURE: Still missing physics.")

def run_suite():
    print(f"Starting Diagnostic Suite on {len(TARGETS)} targets...")
    for cas, name in TARGETS:
        try:
            debug_target(cas, name)
            # Short sleep to prevent rate limiting affecting the test results
            time.sleep(2)
        except Exception as e:
            print(f"    🔥 CRASH: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    run_suite()