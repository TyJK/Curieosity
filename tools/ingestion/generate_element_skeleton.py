import json
import os
import logging
import math
from typing import Dict, Any, Optional, List
from tqdm import tqdm
from mendeleev import element as get_element_by_id

# --- CONFIGURATION ---
OUTPUT_DIR = os.path.normpath("./tools/data/00_element_skeleton")
LOG_DIR = "./tools/logs"

# --- LOGGING ---
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/element_skeleton.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ElementSkeletonGen")

class ElementSkeletonGenerator:
    """
    Scaffolds the Canon Element JSON files using Mendeleev 1.1.0 data.
    """

    # Unit multipliers to Seconds
    TIME_UNITS = {
        's': 1, 'sec': 1, 'seconds': 1,
        'ms': 1e-3, 'us': 1e-6, 'ns': 1e-9, 'ps': 1e-12,
        'm': 60, 'min': 60, 'minute': 60,
        'h': 3600, 'hour': 3600,
        'd': 86400, 'day': 86400,
        'y': 31557600, 'yr': 31557600, 'year': 31557600, 'years': 31557600
    }

    # Manual map for the "Celebrity Isotopes" to give them a head start
    FAMOUS_ISOTOPES = {
        "1H": "Protium", "2H": "Deuterium", "3H": "Tritium",
        "14C": "Radiocarbon", "235U": "Uranium-235", "238U": "Uranium-238",
        "60Co": "Cobalt-60", "99Tc": "Technetium-99m", "131I": "Iodine-131"
    }

    def __init__(self):
        self.stats = {
            "processed": 0,
            "isotopes_found": 0,
            "errors": 0
        }

    def _safe_get(self, value: Any, default: Any = None) -> Any:
        if value is None: return default
        try:
            if isinstance(value, float) and math.isnan(value): return default
        except: pass
        return value

    def _convert_half_life(self, value, unit) -> tuple[Optional[str], Optional[float]]:
        if value is None: return "Stable", None
        clean_unit = str(unit).lower().strip() if unit else "s"
        seconds = None
        multiplier = self.TIME_UNITS.get(clean_unit)
        if multiplier: seconds = float(value) * multiplier

        formatted = f"{value} {unit}" if unit else f"{value} s"
        if seconds:
            if seconds > 3.154e7: formatted = f"{seconds/3.154e7:.2e} years"
            elif seconds < 1e-4: formatted = f"{seconds:.2e} s"
        return formatted, seconds

    def _parse_electron_config(self, el) -> Dict[str, Any]:
        econf_str = self._safe_get(getattr(el, 'econf', ""), "")
        valence = econf_str
        if "]" in econf_str: valence = econf_str.split("]")[-1].strip()
        return {
            "shorthand": econf_str,
            "full": "TODO: Calculation from Z required",
            "valence_shell": valence,
            "semantic_filling": {}
        }

    def generate_element(self, atomic_number: int):
        try:
            el = get_element_by_id(atomic_number)
        except Exception as e:
            logger.error(f"Failed to fetch Z={atomic_number}: {e}")
            self.stats["errors"] += 1
            return

        data = {
            "identity": {
                "name": getattr(el, 'name', ""),
                "symbol": getattr(el, 'symbol', ""),
                "atomic_number": getattr(el, 'atomic_number', 0),
                "group": self._safe_get(getattr(el, 'group_id', None)),
                "period": self._safe_get(getattr(el, 'period', None)),
                "block": self._safe_get(getattr(el, 'block', None)),
                "standard_atomic_weight": self._safe_get(getattr(el, 'atomic_weight', getattr(el, 'mass', None))),
                "ground_state_term_symbol": self._safe_get(getattr(el, 'conf_term', None), "Unknown"),
                "cas_rn": self._safe_get(getattr(el, 'cas', None), "")
            },
            "narratives": {
                "general_overview": "",
                "quantum_behavior": "",
                "nuclear_stability": "",
                "biological_role": "",
                "discovery_story": ""
            },
            "quantum_mechanics": {
                "electron_configuration": self._parse_electron_config(el),
                "ionization_energies_kj_mol": [
                    ie * 96.485 for ie in (getattr(el, 'ionenergies', {}).values() if getattr(el, 'ionenergies', None) else [])
                ],
                "electron_affinity_kj_mol": (getattr(el, 'electron_affinity', 0) * 96.485) if getattr(el, 'electron_affinity', None) else 0.0,
                "electronegativity": {
                    "pauling": self._safe_get(getattr(el, 'en_pauling', None)),
                    "allen": self._safe_get(getattr(el, 'en_allen', None)),
                    "mulliken": self._safe_get(getattr(el, 'en_mulliken', None))
                },
                "atomic_radii_pm": {
                    "calculated": self._safe_get(getattr(el, 'atomic_radius', None)),
                    "van_der_waals": self._safe_get(getattr(el, 'vdw_radius', None)),
                    "covalent_single": self._safe_get(getattr(el, 'covalent_radius_bragg', None)),
                    "covalent_triple": self._safe_get(getattr(el, 'covalent_radius_cordero', None)),
                    "metallic": self._safe_get(getattr(el, 'metallic_radius', None))
                },
                "magnetic_properties": {
                    "magnetic_ordering": "Unknown",
                    "molar_magnetic_susceptibility": self._safe_get(getattr(el, 'mass_magnetic_susceptibility', None))
                }
            },
            "nuclear_data": {
                "isotopes": []
            },
            "media": {
                "images": {
                    "icon_symbol": f"assets/elements/icons/{el.atomic_number}_{el.symbol}.svg",
                    "atom_2d_shell": f"assets/elements/shells/{el.atomic_number}_{el.symbol}_shell.svg",
                    "emission_spectrum_visible": f"assets/elements/spectra/{el.atomic_number}_{el.symbol}_visible.png"
                },
                "models_3d": {
                    "standard_state_lattice": "TODO",
                    "orbital_visualization": "TODO"
                }
            },
            "allotropes": [],
            "discovery": {
                "discoverer": self._safe_get(getattr(el, 'discoverers', None)),
                "year": self._safe_get(getattr(el, 'discovery_year', None)),
                "location": self._safe_get(getattr(el, 'discovery_location', None)),
                "discovery_story": ""
            }
        }

        # --- ISOTOPE PROCESSING ---
        isotopes = getattr(el, 'isotopes', [])
        if isotopes:
            sorted_iso = sorted(isotopes, key=lambda x: x.mass_number)

            for iso in sorted_iso:
                hl = getattr(iso, 'half_life', None)
                hl_unit = getattr(iso, 'half_life_unit', None)
                is_radioactive = getattr(iso, 'is_radioactive', None)
                abundance = getattr(iso, 'abundance', None)

                hl_fmt, hl_sec = self._convert_half_life(hl, hl_unit)
                is_stable = (is_radioactive is False) or (hl is None)

                # Check for "Celebrity" status
                iso_symbol = f"{getattr(iso, 'mass_number', 0)}{el.symbol}"
                common_name = self.FAMOUS_ISOTOPES.get(iso_symbol, None)

                iso_entry = {
                    "mass_number": getattr(iso, 'mass_number', 0),
                    "symbol": iso_symbol,
                    "common_name": common_name, # NEW FIELD
                    "is_stable": is_stable,
                    "half_life_formatted": hl_fmt,
                    "half_life_seconds": hl_sec,
                    "decay_modes": [],
                    "abundance_percent": abundance * 100 if abundance else 0.0,
                    "nuclear_spin": self._safe_get(getattr(iso, 'spin', None)),
                    "binding_energy_per_nucleon_mev": self._safe_get(getattr(iso, 'binding_energy', None)),
                    "narrative": "", # NEW FIELD
                    "uses": [] # NEW FIELD
                }

                data["nuclear_data"]["isotopes"].append(iso_entry)
                self.stats["isotopes_found"] += 1

        filename = f"{el.atomic_number}.json"
        with open(os.path.join(OUTPUT_DIR, filename), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        self.stats["processed"] += 1

    def run(self):
        logger.info("🚀 Starting Element Skeleton Generation v2 (with Isotope Narratives)...")
        for z in tqdm(range(1, 119), desc="Scaffolding Elements"):
            self.generate_element(z)
        logger.info("DONE. Stats:")
        for k, v in self.stats.items(): logger.info(f"  {k:<20}: {v}")

if __name__ == "__main__":
    gen = ElementSkeletonGenerator()
    gen.run()