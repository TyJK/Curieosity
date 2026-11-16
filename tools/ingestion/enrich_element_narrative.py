import json
import os
import logging
import re
import requests
import time
from bs4 import BeautifulSoup
from tqdm import tqdm

# --- CONFIGURATION ---
INPUT_DIR = os.path.normpath("./tools/data/00_element_skeleton")
OUTPUT_DIR = os.path.normpath("./tools/data/01_element_enriched")
LOG_DIR = "./tools/logs"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[logging.FileHandler(f"{LOG_DIR}/element_enrichment.log", mode='w', encoding='utf-8')]
)
logger = logging.getLogger("AutoEnricher")

class AutoElementEnricher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CurieosityBot/19.0 (HTML+AutoDiscover)'
        })
        self.api_url = "https://en.wikipedia.org/w/api.php"
        self.stats = {
            "processed": 0, "narratives_filled": 0, "isotopes_deep_dived": 0, "isotopes_mined": 0, "errors": 0
        }

    def fetch_wiki_html(self, title):
        """Fetches parsed HTML content for robust extraction."""
        params = {
            "action": "parse", "page": title, "prop": "text|sections|headhtml",
            "format": "json", "redirects": 1
        }
        try:
            resp = self.session.get(self.api_url, params=params, timeout=5)
            data = resp.json()

            error = data.get("error")
            if error: return None, None, None

            parse = data.get("parse", {})
            html = parse.get("text", {}).get("*", "")
            final_title = parse.get("title", "")

            return html, final_title, parse.get("sections", [])
        except: return None, None, None

    def get_summary_from_html(self, soup):
        """Extracts the first few paragraphs (Intro) from HTML soup."""
        paragraphs = []
        # In Wiki HTML, the summary is usually the first few <p> tags before the first <h2> (TOC)
        for child in soup.find_all(['p', 'h2']):
            if child.name == 'h2': break # Stop at first section
            if child.name == 'p':
                text = re.sub(r'\[.*?\]', '', child.get_text()).strip() # Clean [1]
                if len(text) > 50: paragraphs.append(text)

        return "\n\n".join(paragraphs[:2]) # First 2 paragraphs

    def extract_section_html(self, soup, keywords):
        """Finds a section by <h2> header containing keyword and extracts text until next header."""
        target_h2 = None
        for h2 in soup.find_all('h2'):
            header_text = h2.get_text().lower()
            if any(kw.lower() in header_text for kw in keywords):
                target_h2 = h2
                break

        if not target_h2: return None

        content = []
        curr = target_h2.next_sibling
        while curr:
            if curr.name == 'h2': break # Stop at next main section
            if curr.name == 'p':
                text = re.sub(r'\[.*?\]', '', curr.get_text()).strip()
                if len(text) > 20: content.append(text)
            curr = curr.next_sibling

        return " ".join(content)

    def extract_uses_list(self, soup):
        """Scrapes 'Uses' or 'Applications' for list items."""
        keywords = ["Uses", "Applications", "Medical use", "Industrial use"]
        target_h2 = None
        for h2 in soup.find_all('h2'):
            if any(kw.lower() in h2.get_text().lower() for kw in keywords):
                target_h2 = h2
                break

        uses = []
        if not target_h2: return uses

        curr = target_h2.next_sibling
        while curr:
            if curr.name == 'h2': break

            # Check for List Items <ul><li>
            if curr.name == 'ul':
                for li in curr.find_all('li'):
                    text = re.sub(r'\[.*?\]', '', li.get_text()).strip()
                    if 10 < len(text) < 300: uses.append(text)

            # Check for Paragraphs (fallback)
            if curr.name == 'p' and not uses:
                text = re.sub(r'\[.*?\]', '', curr.get_text()).strip()
                # Split sentences
                sentences = text.split('. ')
                for s in sentences[:3]:
                    if len(s) > 15: uses.append(s.strip('.'))

            curr = curr.next_sibling

        return uses[:8]

    def mine_isotopes_text(self, soup, element_name, symbol, isotopes):
        """Scans the entire page text for isotope mentions."""
        # Focus on "Isotopes" section first
        iso_section_text = self.extract_section_html(soup, ["Isotopes", "Nuclear"])
        full_text = soup.get_text()
        search_blob = iso_section_text if iso_section_text else full_text

        enriched = 0
        for iso in isotopes:
            if iso.get("narrative"): continue # Skip if already deep dived

            mass = iso["mass_number"]
            # Search patterns: "C-14", "Carbon-14", "14C"
            patterns = [rf"\b{symbol}-{mass}\b", rf"\b{element_name}-{mass}\b", rf"\b{mass}{symbol}\b"]
            regex = "|".join(patterns)

            # Find snippet
            match = re.search(rf"([^.]*?(?:{regex})[^.]*\.)", search_blob, re.IGNORECASE)
            if match:
                text = re.sub(r'\[.*?\]', '', match.group(1)).strip()
                if len(text) > 30:
                    iso["narrative"] = text
                    enriched += 1
        return enriched

    def process_file(self, filename):
        try:
            filepath = os.path.join(INPUT_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f: data = json.load(f)

            ident = data["identity"]
            narratives = data["narratives"]
            isotopes = data.get("nuclear_data", {}).get("isotopes", [])

            name = ident["name"]
            symbol = ident["symbol"]

            # --- 1. ENRICH ELEMENT (Main Page) ---
            html, final_title, _ = self.fetch_wiki_html(name)

            if html:
                soup = BeautifulSoup(html, 'html.parser')

                # A. Summary
                narratives["general_overview"] = self.get_summary_from_html(soup)

                # B. History
                hist = self.extract_section_html(soup, ["History", "Discovery", "Synthesis"])
                if hist: narratives["discovery_story"] = hist[:1200] + "..."

                # C. Biology
                bio = self.extract_section_html(soup, ["Biological", "Biology", "Occurrence", "Toxicity"])
                if bio: narratives["biological_role"] = bio[:1000] + "..."

                if hist or bio: self.stats["narratives_filled"] += 1

            # --- 2. ISOTOPE DISCOVERY (The "Redirect Detective") ---
            deep_dive_count = 0

            for iso in isotopes:
                mass = iso["mass_number"]

                # A. Construct the "Guess" URL (e.g. "Carbon-14")
                query_title = f"{name}-{mass}"

                # B. Fetch it to see where it lands
                iso_html, iso_title, _ = self.fetch_wiki_html(query_title)

                if iso_html:
                    # C. Check Filter: Is this a "Celebrity" page?
                    # - It shouldn't be the Main Element page (e.g. "Iron-56" -> "Iron")
                    # - It shouldn't be a List (e.g. "Carbon-12" -> "Isotopes of Carbon")

                    is_main_page = (iso_title.lower() == name.lower())
                    is_list_page = ("isotopes of" in iso_title.lower())

                    if not is_main_page and not is_list_page:
                        # IT'S A MATCH! (e.g. "Deuterium", "Technetium-99m", "Carbon-14")
                        iso_soup = BeautifulSoup(iso_html, 'html.parser')

                        # Narrative = Intro of that page
                        intro = self.get_summary_from_html(iso_soup)
                        if intro:
                            iso["narrative"] = intro
                            iso["common_name"] = iso_title # Update common name (e.g. "Deuterium")

                            # Uses = "Uses" section of that page
                            uses = self.extract_uses_list(iso_soup)
                            if uses: iso["uses"] = uses

                            deep_dive_count += 1
                            tqdm.write(f"  ✨ Found Celebrity: {query_title} -> {iso_title}")

            self.stats["isotopes_deep_dived"] += deep_dive_count

            # --- 3. FALLBACK MINING ---
            # Use the Main Element Page soup to find mentions of boring isotopes
            if html:
                mined = self.mine_isotopes_text(soup, name, symbol, isotopes)
                self.stats["isotopes_mined"] += mined

            # Log
            has_story = bool(narratives.get("discovery_story"))
            tqdm.write(f"✅ {name:<15} | Story: {'YES' if has_story else 'NO'} | DeepDive: {deep_dive_count} | Mined: {self.stats['isotopes_mined']}")

            with open(os.path.join(OUTPUT_DIR, filename), 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            self.stats["processed"] += 1

        except Exception as e:
            self.stats["errors"] += 1
            tqdm.write(f"❌ Error {filename}: {e}")

    def run(self):
        files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
        print(f"🚀 Starting Auto-Discovery Enrichment on {len(files)} files...")

        for f in tqdm(files):
            self.process_file(f)

        print("DONE. Stats:")
        for k, v in self.stats.items(): print(f"  {k}: {v}")

if __name__ == "__main__":
    AutoElementEnricher().run()