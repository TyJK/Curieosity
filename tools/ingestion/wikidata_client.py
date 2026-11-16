import requests
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Wikidata")

class WikidataClient:
    SPARQL_URL = "https://query.wikidata.org/sparql"

    def get_history(self, name: str, inchikey: str = None, cas_rn: str = None) -> Dict[str, Any]:
        """
        Fetches History AND Physics (MP/Density) if available.
        """
        best_result = {}

        # 1. Try InChIKey
        if inchikey:
            res = self._query_by_property("P235", inchikey, "InChIKey")
            if self._is_good_result(res): return res
            if res: best_result = res

        # 2. Try CAS RN
        if cas_rn:
            res = self._query_by_property("P231", cas_rn, "CAS RN")
            if self._is_good_result(res): return res
            if res and not best_result: best_result = res

        # 3. Fallback to Name
        if name:
            res = self._query_by_name(name)
            if self._is_good_result(res): return res
            if res and not best_result: best_result = res

        return best_result

    def _is_good_result(self, res):
        return res.get("discoverer") or res.get("melting_point")

    def _query_by_property(self, prop_id: str, value: str, label: str) -> Dict[str, Any]:
        # P2101 = Melting Point, P2054 = Density
        query = f"""
        SELECT ?item ?itemLabel ?discovererLabel ?discoveryDate ?inceptionDate ?mp ?dens WHERE {{
          ?item wdt:{prop_id} "{value}" .
          OPTIONAL {{ ?item wdt:P61 ?discoverer . }}
          OPTIONAL {{ ?item wdt:P575 ?discoveryDate . }}
          OPTIONAL {{ ?item wdt:P571 ?inceptionDate . }}
          OPTIONAL {{ ?item wdt:P2101 ?mp . }}
          OPTIONAL {{ ?item wdt:P2054 ?dens . }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT 1
        """
        return self._run_query(query, label)

    def _query_by_name(self, name: str) -> Dict[str, Any]:
        query = f"""
        SELECT ?item ?itemLabel ?discovererLabel ?discoveryDate ?inceptionDate ?mp ?dens WHERE {{
          ?item rdfs:label "{name}"@en .
          {{ ?item wdt:P31/wdt:P279* wd:Q11173 . }} UNION {{ ?item wdt:P31/wdt:P279* wd:Q11344 . }}
          OPTIONAL {{ ?item wdt:P61 ?discoverer . }}
          OPTIONAL {{ ?item wdt:P575 ?discoveryDate . }}
          OPTIONAL {{ ?item wdt:P571 ?inceptionDate . }}
          OPTIONAL {{ ?item wdt:P2101 ?mp . }}
          OPTIONAL {{ ?item wdt:P2054 ?dens . }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT 1
        """
        return self._run_query(query, f"Name '{name}'")

    def _run_query(self, sparql: str, context_label: str) -> Dict[str, Any]:
        try:
            resp = requests.get(self.SPARQL_URL, params={'query': sparql, 'format': 'json'})
            resp.raise_for_status()
            data = resp.json()
            bindings = data.get("results", {}).get("bindings", [])
            if not bindings: return {}

            hit = bindings[0]
            year = hit.get("discoveryDate", {}).get("value")
            if not year: year = hit.get("inceptionDate", {}).get("value")
            if year and "T" in year: year = year.split("T")[0]

            return {
                "discoverer": hit.get("discovererLabel", {}).get("value"),
                "year": year,
                "wikidata_url": hit.get("item", {}).get("value"),
                # Extract Physics
                "melting_point": hit.get("mp", {}).get("value"),
                "density": hit.get("dens", {}).get("value")
            }
        except Exception: return {}