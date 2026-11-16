import logging
import sys
import os
import time

# Ensure we can import from the root
sys.path.append(os.getcwd())

from inspect_full_compound import CompoundInspector
from synthesize_compound_schema import DataRefinery

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("PhysicsDebug")

# Test Cases designed to break the old regex
TARGETS = [
    ("57-55-6", "Propylene glycol"), # HAD BUG: "-60" -> -60.0 K
    ("74-82-8", "Methane"),          # Range test: "452-518" (Autoignition?)
    ("64-17-5", "Ethanol"),          # Control: Standard
    ("7782-44-7", "Oxygen"),         # Low Temp: "-218.4 C"
    ("109-66-0", "Pentane")          # Simple alkane
]

def debug_physics(cas_rn, name):
    print(f"\n{'='*80}")
    print(f"🧪 PHYSICS CHECK: {name} ({cas_rn})")
    print(f"{'='*80}")

    inspector = CompoundInspector()
    # Fetch live data to ensure we are testing the current PubChem response
    raw_record = inspector.inspect(name, known_cas_rn=cas_rn)

    # Extract Raw Props
    props = raw_record.get("identity", {}).get("pubchem_context", {}).get("experimental_properties", {})
    raw_mp = props.get("melting_point")
    raw_bp = props.get("boiling_point")

    print(f"  [Raw Strings]")
    print(f"    Melting Point: '{raw_mp}'")
    print(f"    Boiling Point: '{raw_bp}'")

    # Test Calculations
    refinery = DataRefinery()

    calc_mp = refinery.normalize_temperature(raw_mp)
    calc_bp = refinery.normalize_temperature(raw_bp)

    print(f"  [Calculated Kelvin]")
    print(f"    MP: {calc_mp} K")
    print(f"    BP: {calc_bp} K")

    # Verdicts
    if calc_mp is not None:
        if calc_mp < 0:
            print("    ❌ FAIL: Melting Point is Negative Kelvin!")
        elif raw_mp and "-" in raw_mp and calc_mp > 0:
            print("    ✅ PASS: Negative Celsius successfully converted to Positive Kelvin.")
        else:
            print("    ✅ PASS: Valid Positive Kelvin.")

    if calc_bp is not None:
        if calc_bp < 0:
            print("    ❌ FAIL: Boiling Point is Negative Kelvin!")
        else:
            print("    ✅ PASS: Valid Positive Kelvin.")

if __name__ == "__main__":
    for cas, name in TARGETS:
        try:
            debug_physics(cas, name)
            time.sleep(1)
        except Exception as e:
            print(f"CRASH: {e}")
            import traceback
            traceback.print_exc()