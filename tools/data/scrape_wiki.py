"""
Fetches the Wikipedia and Wikidata material behind Curieosity's pages, for every substance
in the game (and every locked preview) and every topic of the curriculum.

For each substance it finds the English Wikipedia article, by the link the content gives
it, then by its CAS number or PubChem record on Wikidata, then by its name. It keeps every
candidate article it finds, so gen_pages.py can check each against the substance's formula
before using it. From each article it keeps:

    the whole article as plain text, with its section headings
    the infobox (Chembox, Infobox element, Drugbox ...) as wikitext: the measured values
    the revision and its date, for the attribution under the text
    the Wikidata item's chemical statements (formula, melting and boiling points with their
    units, density, solubility, flash point, discoverer, discovery date ...), which are CC0

For each curriculum topic (tools/data/curriculum.py) it keeps the whole article too, and for
a wider pool of chemistry articles (the links of "Outline of chemistry" and a few
categories) only the lead, so the curriculum can grow without another full run.

Everything is cached as it arrives (library/wiki/cache.sqlite), so the run can be stopped and
started again, and a later run only fetches what is new. At the end it writes one file,
library/wiki/pages.jsonl.xz, that tools/data/gen_pages.py builds the pages from.

    python tools/data/scrape_wiki.py                 fetch what isn't cached, then export
    python tools/data/scrape_wiki.py --limit 25      a short trial: the first 25 substances
    python tools/data/scrape_wiki.py --export-only   write the export from the cache
    python tools/data/scrape_wiki.py --refresh       fetch everything again

It uses only Python's standard library. Requests go one at a time, with the User-Agent and
maxlag Wikimedia ask of bots; a full first run is several thousand requests and takes about
half an hour to an hour.
"""
import argparse
import gzip
import http.client
import json
import lzma
import os
import re
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "library" / "wiki"
DB = OUT / "cache.sqlite"
EXPORT = OUT / "pages.jsonl.xz"
DATA = ROOT / "assets" / "data"

UA = ("CurieosityContentBot/1.0 (https://github.com/TyJK/Curieosity; free educational "
      "chemistry game; one request at a time) python-urllib")
WP = "en.wikipedia.org"
WD = "www.wikidata.org"
SPARQL = "query.wikidata.org"
MIN_GAP = 0.1   # seconds between requests

# The Wikidata statements kept for a substance.
PROPS = {
    "P274": "formula", "P231": "cas", "P662": "pubchem_cid", "P2101": "melting_point",
    "P2102": "boiling_point", "P2054": "density", "P2177": "solubility", "P2128": "flash_point",
    "P2199": "autoignition", "P2119": "vapor_pressure", "P3078": "enthalpy_of_formation",
    "P2993": "logp", "P1117": "pka", "P2240": "ld50", "P61": "discoverer",
    "P575": "discovered", "P138": "named_after", "P366": "use", "P31": "instance_of",
    "P279": "subclass_of", "P18": "image", "P117": "structure_image", "P2067": "mass",
    "P1086": "atomic_number", "P2275": "who_name",
}
# items whose labels are worth fetching (people, uses, classes)
LABELLED = {"P61", "P138", "P366", "P31", "P279"}

# A wider pool of chemistry articles: their leads only.
POOL_PAGES = ["Outline of chemistry", "Glossary of chemistry terms", "Outline of organic chemistry",
              "List of chemical laws"]
POOL_CATEGORIES = [
    "Chemical laws", "Gas laws", "Name reactions", "Chemical processes", "Industrial processes",
    "Laboratory equipment", "Laboratory glassware", "Metallurgical processes",
    "History of chemistry", "Alchemy", "Chemical reactions", "Separation processes",
    "Equilibrium chemistry", "Chemical kinetics", "Acid–base chemistry", "Electrochemistry",
    "Chemical bonding", "Organic reactions", "Polymerization reactions", "Catalysis",
    "Discoverers of chemical elements",
]

INFOBOX = re.compile(r"\{\{\s*(Chembox|Infobox element|Infobox drug|Drugbox|Infobox mineral|"
                     r"Infobox chemical|Infobox [a-z ]*compound|Infobox food|Infobox plant|"
                     r"Speciesbox|Taxobox|Infobox [A-Za-z ]+)\b", re.I)


# --------------------------------------------------------------------------------------
# Network
# --------------------------------------------------------------------------------------
class Net:
    """One request at a time over kept-alive connections; retries with backoff."""

    def __init__(self, log=print):
        self.conns = {}
        self.last = 0.0
        self.count = 0
        self.log = log
        self.proxy = any(os.environ.get(k) for k in ("HTTPS_PROXY", "https_proxy"))
        self.lag_noted = False

    def _send(self, host, path, body, headers):
        if self.proxy:
            req = urllib.request.Request(f"https://{host}{path}", data=body, headers=headers)
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.status, dict(r.headers), r.read()
        c = self.conns.get(host)
        if c is None:
            c = self.conns[host] = http.client.HTTPSConnection(host, timeout=90)
        c.request("POST" if body is not None else "GET", path, body=body, headers=headers)
        r = c.getresponse()
        return r.status, dict(r.getheaders()), r.read()

    def call(self, host, path, params, post=True, accept="application/json"):
        params = dict(params)
        err = None
        for attempt in range(8):
            headers = {"User-Agent": UA, "Accept-Encoding": "gzip", "Accept": accept}
            enc = urllib.parse.urlencode(params)
            body, url = None, path
            if post:
                body = enc.encode()
                headers["Content-Type"] = "application/x-www-form-urlencoded"
            else:
                url = f"{path}?{enc}"
            gap = MIN_GAP - (time.time() - self.last)
            if gap > 0:
                time.sleep(gap)
            try:
                status, rh, raw = self._send(host, url, body, headers)
            except urllib.error.HTTPError as e:
                status, rh, raw = e.code, dict(e.headers), e.read()
            except (http.client.HTTPException, OSError) as e:
                self.conns.pop(host, None)
                err = e
                time.sleep(min(60, 2 ** attempt))
                continue
            self.last = time.time()
            self.count += 1
            rh = {k.lower(): v for k, v in rh.items()}
            if rh.get("content-encoding") == "gzip":
                raw = gzip.decompress(raw)
            if status in (429, 500, 502, 503, 504):
                wait = float(rh.get("retry-after") or 0) or min(120, 5 * 2 ** attempt)
                self.log(f"  {host} answered {status}; waiting {wait:.0f} s")
                time.sleep(wait)
                err = f"HTTP {status}"
                continue
            if status != 200:
                raise RuntimeError(f"{host}{path[:80]}: HTTP {status}: {raw[:300]!r}")
            j = json.loads(raw)
            if isinstance(j, dict) and "error" in j:
                code = j["error"].get("code")
                if code == "maxlag":
                    # replicas behind (Wikidata often is, for hours): wait a little, then
                    # read anyway; maxlag only matters for bots that write
                    if attempt >= 1:
                        params.pop("maxlag", None)
                        if not self.lag_noted:
                            self.lag_noted = True
                            self.log(f"  {host} is lagging; reading without waiting for it")
                    else:
                        time.sleep(float(rh.get("retry-after") or 5))
                    err = "maxlag"
                    continue
                raise RuntimeError(f"{host}: API error {code}: {j['error'].get('info')}")
            return j
        raise RuntimeError(f"{host}{path[:80]}: gave up after 8 tries ({err})")

    def wp(self, **params):
        p = {"format": "json", "formatversion": "2", "maxlag": "5"}
        p.update({k: v for k, v in params.items() if v is not None})
        return self.call(WP, "/w/api.php", p)

    def wd(self, **params):
        # reads only: no maxlag (Wikidata's includes its query service's lag, often minutes)
        p = {"format": "json"}
        p.update(params)
        return self.call(WD, "/w/api.php", p)

    def sparql(self, query):
        return self.call(SPARQL, "/sparql", {"query": query}, post=True,
                         accept="application/sparql-results+json")


# --------------------------------------------------------------------------------------
# Cache
# --------------------------------------------------------------------------------------
class Cache:
    def __init__(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path))
        self.db.execute("CREATE TABLE IF NOT EXISTS kv (kind TEXT, key TEXT, value TEXT, "
                        "PRIMARY KEY (kind, key))")
        self.pending = 0

    def get(self, kind, key):
        r = self.db.execute("SELECT value FROM kv WHERE kind=? AND key=?", (kind, str(key))).fetchone()
        return json.loads(r[0]) if r else None

    def has(self, kind, key):
        return self.db.execute("SELECT 1 FROM kv WHERE kind=? AND key=?", (kind, str(key))).fetchone() is not None

    def put(self, kind, key, value):
        self.db.execute("INSERT OR REPLACE INTO kv VALUES (?,?,?)", (kind, str(key), json.dumps(value, ensure_ascii=False)))
        self.pending += 1
        if self.pending >= 50:
            self.commit()

    def all(self, kind):
        for k, v in self.db.execute("SELECT key, value FROM kv WHERE kind=?", (kind,)):
            yield k, json.loads(v)

    def clear(self, kinds):
        for k in kinds:
            self.db.execute("DELETE FROM kv WHERE kind=?", (k,))
        self.commit()

    def commit(self):
        self.db.commit()
        self.pending = 0


# --------------------------------------------------------------------------------------
# What to fetch
# --------------------------------------------------------------------------------------
def parse_link(w):
    """('title', T) | ('curid', N) | ('cid', N) | ('pcname', name) | None for a content link."""
    if not w:
        return None
    if not w.startswith("http"):
        return ("title", urllib.parse.unquote(w).replace("_", " ").split("#")[0])
    u = urllib.parse.urlparse(w)
    if "wikipedia.org" in u.netloc:
        q = urllib.parse.parse_qs(u.query)
        if "curid" in q:
            return ("curid", int(q["curid"][0]))
        if u.path.startswith("/wiki/"):
            t = urllib.parse.unquote(u.path[6:]).replace("_", " ")
            return ("title", t) if t else None
        return None
    if "pubchem.ncbi.nlm.nih.gov" in u.netloc:
        m = re.match(r"^/(?:compound|element)/(.+)$", u.path)
        if not m:
            return None
        v = urllib.parse.unquote(m.group(1))
        if u.path.startswith("/element/"):
            return None
        return ("cid", int(v)) if v.isdigit() else ("pcname", v)
    return None


def library_links():
    """id -> [links] from the packed library (assets/data/substances.ron)."""
    out, cur = {}, None
    path = DATA / "substances.ron"
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^ {12}id: (\d+),", line)
        if m:
            cur = int(m.group(1))
        elif cur is not None and line.startswith("            references: "):
            out[cur] = re.findall(r'"(https?://[^"]+)"', line)
    return out


def written_ids():
    """The substance ids the game ships (in play, and the locked previews)."""
    text = (DATA / "authored_substances.ron").read_text(encoding="utf-8")
    return {int(x) for x in re.findall(r"^ {4}(\d+): \(", text, re.M)}


def substance_targets():
    sys.path.insert(0, str(HERE))
    import authored_content as C
    canon = sys.modules["authored_canon"].CANON
    cas_of = {}
    for cas, key in canon.items():
        if re.match(r"^\d+-\d\d-\d$", cas):
            cas_of.setdefault(key, cas)
    try:
        import authored_placeholders as P
        for row in P.DATA:
            if re.match(r"^\d+-\d\d-\d$", row[0]):
                cas_of.setdefault(row[1], row[0])
    except ImportError:
        pass
    ids = written_ids()
    libl = library_links()
    idmap = json.loads((HERE / "authored_ids.json").read_text(encoding="utf-8"))
    out = []
    for key, s in C.SUBSTANCES.items():
        sid = s.id or (idmap.get(key) or {}).get("id")
        if sid not in ids:
            continue
        links = []
        own = parse_link(s.wiki)
        if own:
            links.append(("own",) + own)
        for url in libl.get(sid, []):
            p = parse_link(url)
            if p:
                links.append(("library",) + p)
        out.append({"id": sid, "key": key, "name": s.name, "formula": s.formula,
                    "stage": s.stage, "cas": cas_of.get(key), "links": links})
    return out


def reaction_links():
    text = (DATA / "authored_reactions.ron").read_text(encoding="utf-8")
    out = set()
    for url in re.findall(r'"(https://en\.wikipedia\.org/[^"]+)"', text):
        p = parse_link(url)
        if p:
            out.add(p)
    return sorted(out, key=str)


# --------------------------------------------------------------------------------------
# Resolving links to pages
# --------------------------------------------------------------------------------------
def chunks(xs, n):
    xs = list(xs)
    for i in range(0, len(xs), n):
        yield xs[i:i + n]


def page_info(p):
    pp = p.get("pageprops") or {}
    return {"pageid": p.get("pageid"), "title": p.get("title"), "missing": bool(p.get("missing") or p.get("invalid")),
            "wikibase": pp.get("wikibase_item"), "shortdesc": pp.get("wikibase-shortdesc"),
            "disambiguation": "disambiguation" in pp}


def resolve_titles(net, cache, titles, log):
    """Cache 'title' -> page info (following normalisation and redirects)."""
    todo = sorted({t for t in titles if t and not cache.has("title", t)})
    for n, batch in enumerate(chunks(todo, 50)):
        j = net.wp(action="query", titles="|".join(batch), redirects="1", prop="pageprops",
                   ppprop="wikibase_item|disambiguation|wikibase-shortdesc")
        q = j.get("query", {})
        hop = {}
        for k in ("normalized", "redirects"):
            for x in q.get(k, []):
                hop[x["from"]] = x["to"]
        by_title = {p["title"]: page_info(p) for p in q.get("pages", [])}
        for t in batch:
            cur, seen = t, set()
            while cur in hop and cur not in seen:
                seen.add(cur)
                cur = hop[cur]
            cache.put("title", t, by_title.get(cur, {"missing": True, "title": cur}))
        if n % 10 == 9:
            log(f"  titles {min(len(todo), (n + 1) * 50)}/{len(todo)}")
    cache.commit()


def resolve_curids(net, cache, ids, log):
    todo = sorted({i for i in ids if not cache.has("curid", i)})
    for batch in chunks(todo, 50):
        j = net.wp(action="query", pageids="|".join(map(str, batch)), prop="pageprops",
                   ppprop="wikibase_item|disambiguation|wikibase-shortdesc")
        got = {p.get("pageid"): page_info(p) for p in j.get("query", {}).get("pages", [])}
        for i in batch:
            cache.put("curid", i, got.get(i, {"missing": True}))
    cache.commit()


def resolve_wikidata(net, cache, kind, values, log):
    """kind 'cas' (P231) or 'cid' (P662): value -> [(item, enwiki title or None)]."""
    prop = {"cas": "P231", "cid": "P662"}[kind]
    todo = sorted({str(v) for v in values if v and not cache.has(kind, v)})
    for n, batch in enumerate(chunks(todo, 150)):
        vals = " ".join(json.dumps(v) for v in batch)
        query = ("SELECT ?v ?item ?article WHERE { VALUES ?v { " + vals + " } ?item wdt:" + prop +
                 " ?v . OPTIONAL { ?article schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> . } }")
        j = net.sparql(query)
        found = {}
        for b in j.get("results", {}).get("bindings", []):
            v = b["v"]["value"]
            item = b["item"]["value"].rsplit("/", 1)[-1]
            art = b.get("article", {}).get("value")
            title = urllib.parse.unquote(art.split("/wiki/", 1)[1]).replace("_", " ") if art else None
            found.setdefault(v, [])
            if [item, title] not in found[v]:
                found[v].append([item, title])
        for v in batch:
            cache.put(kind, v, found.get(v, []))
        log(f"  {kind.upper()} on Wikidata {min(len(todo), (n + 1) * 150)}/{len(todo)}")
    cache.commit()


def candidates(t, cache):
    """Every article found for a substance: [(how, pageid, title)], best first, no repeats."""
    out, seen = [], set()

    def add(how, info):
        if info and not info.get("missing") and info.get("pageid") and info["pageid"] not in seen:
            seen.add(info["pageid"])
            out.append({"how": how, "pageid": info["pageid"], "title": info["title"],
                        "disambiguation": info.get("disambiguation", False)})

    for src, kind, val in t["links"]:
        if kind == "title":
            add(src + "-title", cache.get("title", val))
        elif kind == "curid":
            add(src + "-curid", cache.get("curid", val))
    if t.get("cas"):
        for item, title in cache.get("cas", t["cas"]) or []:
            if title:
                add("cas", cache.get("title", title))
    for src, kind, val in t["links"]:
        if kind == "cid":
            for item, title in cache.get("cid", str(val)) or []:
                if title:
                    add("pubchem", cache.get("title", title))
    for src, kind, val in t["links"]:
        if kind == "pcname":
            add("pubchem-name", cache.get("title", val))
    if not out:
        add("name", cache.get("title", t["name"].replace("#", "")))
    return out


# --------------------------------------------------------------------------------------
# Fetching articles
# --------------------------------------------------------------------------------------
def infoboxes(wikitext):
    """The infobox templates of an article's wikitext, whole (nested templates included)."""
    out = []
    for m in INFOBOX.finditer(wikitext or ""):
        if any(a <= m.start() < b for a, b, _ in out):
            continue
        i, depth = m.start(), 0
        while i < len(wikitext):
            if wikitext.startswith("{{", i):
                depth += 1
                i += 2
            elif wikitext.startswith("}}", i):
                depth -= 1
                i += 2
                if depth == 0:
                    break
            else:
                i += 1
        out.append((m.start(), i, wikitext[m.start():i]))
        if len(out) >= 3:
            break
    return [x for _, _, x in out]


def fetch_full(net, cache, pageids, log, label):
    todo = [p for p in sorted(set(pageids)) if not cache.has("page", p)]
    t0 = time.time()
    for n, pid in enumerate(todo):
        j = net.wp(action="query", pageids=str(pid), prop="extracts|revisions|pageprops",
                   explaintext="1", exsectionformat="wiki", rvprop="ids|timestamp|content",
                   rvslots="main", ppprop="wikibase_item|disambiguation|wikibase-shortdesc")
        pages = j.get("query", {}).get("pages", [])
        if not pages or pages[0].get("missing"):
            cache.put("page", pid, {"pageid": pid, "missing": True})
            continue
        p = pages[0]
        rev = (p.get("revisions") or [{}])[0]
        text = ((rev.get("slots") or {}).get("main") or {}).get("content") or ""
        info = page_info(p)
        info.update({"revid": rev.get("revid"), "timestamp": rev.get("timestamp"), "full": True,
                     "text": p.get("extract") or "", "infobox": infoboxes(text)})
        cache.put("page", pid, info)
        if n % 50 == 49 or n == len(todo) - 1:
            rate = (time.time() - t0) / (n + 1)
            left = rate * (len(todo) - n - 1) / 60
            log(f"  {label}: {n + 1}/{len(todo)} articles, about {left:.0f} min left")
    cache.commit()


BARE_INFOBOX = re.compile(r"^\{\{\s*(Infobox [^|{}]+?)\s*\}\}$", re.I)


def fetch_templates(net, cache, log):
    """Element articles carry only {{Infobox hydrogen}}: the values live in the template. Cache
    the wikitext of every such template."""
    names = set()
    for _, p in cache.all("page"):
        for box in p.get("infobox") or []:
            m = BARE_INFOBOX.match(box.strip())
            if m:
                names.add("Template:" + m.group(1)[0].upper() + m.group(1)[1:])
    todo = sorted(n for n in names if not cache.has("template", n))
    for batch in chunks(todo, 50):
        j = net.wp(action="query", titles="|".join(batch), prop="revisions", rvprop="content", rvslots="main",
                   redirects="1")
        q = j.get("query", {})
        hop = {x["from"]: x["to"] for k in ("normalized", "redirects") for x in q.get(k, [])}
        got = {}
        for p in q.get("pages", []):
            rev = (p.get("revisions") or [{}])[0]
            got[p["title"]] = ((rev.get("slots") or {}).get("main") or {}).get("content")
        for n in batch:
            cache.put("template", n, {"title": n, "wikitext": got.get(hop.get(n, n))})
    cache.commit()
    if todo:
        log(f"  {len(todo)} infobox templates")


def fetch_leads(net, cache, pageids, log):
    todo = [p for p in sorted(set(pageids)) if not cache.has("page", p) and not cache.has("lead", p)]
    for n, batch in enumerate(chunks(todo, 20)):
        params = dict(action="query", pageids="|".join(map(str, batch)), prop="extracts|pageprops|revisions",
                      exintro="1", explaintext="1", exlimit="20", rvprop="ids|timestamp",
                      ppprop="wikibase_item|disambiguation|wikibase-shortdesc")
        got = {}
        while True:
            j = net.wp(**params)
            for p in j.get("query", {}).get("pages", []):
                g = got.setdefault(p["pageid"], page_info(p))
                if p.get("extract"):
                    g["text"] = p["extract"]
                rev = (p.get("revisions") or [{}])[0]
                if rev.get("revid"):
                    g["revid"], g["timestamp"] = rev["revid"], rev.get("timestamp")
            if "continue" not in j:
                break
            params.update(j["continue"])
        for pid in batch:
            g = got.get(pid, {"pageid": pid, "missing": True})
            g["full"] = False
            cache.put("lead", pid, g)
        if n % 10 == 9:
            log(f"  leads {min(len(todo), (n + 1) * 20)}/{len(todo)}")
    cache.commit()


def pool_titles(net, cache, log):
    """Titles in the wider pool: the links of POOL_PAGES and the members of POOL_CATEGORIES."""
    for page in POOL_PAGES:
        if cache.has("pool", page):
            continue
        titles, params = [], dict(action="query", titles=page, prop="links", plnamespace="0", pllimit="max")
        while True:
            j = net.wp(**params)
            for p in j.get("query", {}).get("pages", []):
                titles += [x["title"] for x in p.get("links", [])]
            if "continue" not in j:
                break
            params.update(j["continue"])
        cache.put("pool", page, titles)
    for cat in POOL_CATEGORIES:
        key = "Category:" + cat
        if cache.has("pool", key):
            continue
        titles, params = [], dict(action="query", list="categorymembers", cmtitle=key, cmnamespace="0",
                                  cmlimit="max")
        while True:
            j = net.wp(**params)
            titles += [x["title"] for x in j.get("query", {}).get("categorymembers", [])]
            if "continue" not in j:
                break
            params.update(j["continue"])
        cache.put("pool", key, titles)
    cache.commit()
    out = {}
    for src, titles in cache.all("pool"):
        for t in titles:
            out.setdefault(t, src)
    return out


# --------------------------------------------------------------------------------------
# Wikidata statements
# --------------------------------------------------------------------------------------
def simplify(snak):
    dv = (snak or {}).get("datavalue")
    if not dv:
        return None
    v, t = dv.get("value"), dv.get("type")
    if t == "quantity":
        unit = v.get("unit", "1").rsplit("/", 1)[-1]
        out = {"amount": float(v["amount"]), "unit": unit}
        for k in ("lowerBound", "upperBound"):
            if k in v:
                out[k[:5]] = float(v[k])
        return out
    if t == "wikibase-entityid":
        return v.get("id")
    if t == "time":
        return v.get("time")
    if t == "monolingualtext":
        return v.get("text")
    return v


def statements(entity):
    out = {}
    for pid, name in PROPS.items():
        for c in entity.get("claims", {}).get(pid, []):
            if c.get("rank") == "deprecated":
                continue
            val = simplify(c.get("mainsnak"))
            if val is None:
                continue
            q = {}
            for qp, qs in (c.get("qualifiers") or {}).items():
                vals = [simplify(s) for s in qs]
                vals = [x for x in vals if x is not None]
                if vals:
                    q[qp] = vals
            st = {"value": val}
            if q:
                st["q"] = q
            if c.get("rank") == "preferred":
                st["preferred"] = True
            if c.get("references"):
                st["sourced"] = True
            out.setdefault(name, []).append(st)
    return out


def fetch_entities(net, cache, qids, log):
    todo = sorted({q for q in qids if q and not cache.has("entity", q)})
    for n, batch in enumerate(chunks(todo, 50)):
        j = net.wd(action="wbgetentities", ids="|".join(batch), props="claims|labels|descriptions",
                   languages="en")
        for q in batch:
            e = j.get("entities", {}).get(q) or {}
            cache.put("entity", q, {
                "qid": q, "label": ((e.get("labels") or {}).get("en") or {}).get("value"),
                "description": ((e.get("descriptions") or {}).get("en") or {}).get("value"),
                "claims": statements(e)})
        if n % 10 == 9:
            log(f"  Wikidata items {min(len(todo), (n + 1) * 50)}/{len(todo)}")
    cache.commit()


def fetch_labels(net, cache, qids, log):
    todo = sorted({q for q in qids if q and re.match(r"^Q\d+$", q) and not cache.has("label", q)})
    for batch in chunks(todo, 50):
        j = net.wd(action="wbgetentities", ids="|".join(batch), props="labels|descriptions", languages="en")
        for q in batch:
            e = j.get("entities", {}).get(q) or {}
            cache.put("label", q, {"label": ((e.get("labels") or {}).get("en") or {}).get("value"),
                                   "description": ((e.get("descriptions") or {}).get("en") or {}).get("value")})
    cache.commit()


# --------------------------------------------------------------------------------------
# The run
# --------------------------------------------------------------------------------------
def run(args, net=None, cache=None, log=print):
    cache = cache or Cache(DB)
    net = net or Net(log)
    if args.refresh:
        cache.clear(["title", "curid", "cas", "cid", "page", "lead", "entity", "label", "pool", "template"])
    subs = substance_targets()
    subs.sort(key=lambda t: (bool(t["stage"]), t["id"]))
    if args.limit:
        subs = subs[:args.limit]
    import curriculum
    topics = curriculum.TOPICS
    if args.limit:
        topics = dict(list(topics.items())[:10])
    rlinks = [] if args.limit else reaction_links()
    log(f"{len(subs)} substances ({sum(1 for t in subs if t['stage'])} locked previews), "
        f"{len(topics)} curriculum topics, {len(rlinks)} articles the reactions cite")

    if not args.export_only:
        log("1/6 Following the links the content gives")
        titles = {v for t in subs for _, k, v in t["links"] if k in ("title", "pcname")}
        titles |= {t["name"].replace("#", "") for t in subs}
        titles |= {title for _, _, title in topics.values()}
        titles |= {v for k, v in rlinks if k == "title"}
        resolve_titles(net, cache, titles, log)
        resolve_curids(net, cache, {v for t in subs for _, k, v in t["links"] if k == "curid"} |
                       {v for k, v in rlinks if k == "curid"}, log)

        log("2/6 Finding articles by CAS number and PubChem record on Wikidata")
        resolve_wikidata(net, cache, "cas", {t["cas"] for t in subs if t["cas"]}, log)
        resolve_wikidata(net, cache, "cid", {str(v) for t in subs for _, k, v in t["links"] if k == "cid"}, log)
        found = set()
        for t in subs:
            for item, title in (cache.get("cas", t["cas"]) or []) if t["cas"] else []:
                found.add(title)
            for _, k, v in t["links"]:
                if k == "cid":
                    for item, title in cache.get("cid", str(v)) or []:
                        found.add(title)
        resolve_titles(net, cache, {x for x in found if x}, log)

        log("3/6 Fetching the substances' articles")
        sub_pages = {c["pageid"] for t in subs for c in candidates(t, cache) if not c["disambiguation"]}
        fetch_full(net, cache, sub_pages, log, "substances")

        log("4/6 Fetching the curriculum's articles")
        topic_pages = set()
        for _, _, title in topics.values():
            info = cache.get("title", title) or {}
            if info.get("pageid") and not info.get("missing"):
                topic_pages.add(info["pageid"])
        fetch_full(net, cache, topic_pages, log, "topics")
        fetch_templates(net, cache, log)

        if not args.limit:
            log("5/6 Fetching the leads of the wider pool and the articles the reactions cite")
            pool = pool_titles(net, cache, log)
            resolve_titles(net, cache, set(pool), log)
            lead_pages = set()
            for t in list(pool) + [v for k, v in rlinks if k == "title"]:
                info = cache.get("title", t) or {}
                if info.get("pageid"):
                    lead_pages.add(info["pageid"])
            for k, v in rlinks:
                if k == "curid":
                    info = cache.get("curid", v) or {}
                    if info.get("pageid"):
                        lead_pages.add(info["pageid"])
            fetch_leads(net, cache, lead_pages, log)

        log("6/6 Fetching the Wikidata statements")
        qids = set()
        for _, p in cache.all("page"):
            if p.get("wikibase"):
                qids.add(p["wikibase"])
        for t in subs:
            for item, _ in (cache.get("cas", t["cas"]) or []) if t["cas"] else []:
                qids.add(item)
        fetch_entities(net, cache, qids, log)
        ref = set()
        for _, e in cache.all("entity"):
            for name, sts in e["claims"].items():
                pid = next(k for k, v in PROPS.items() if v == name)
                if pid in LABELLED:
                    ref |= {s["value"] for s in sts if isinstance(s["value"], str)}
                for s in sts:
                    v = s["value"]
                    if isinstance(v, dict) and v.get("unit", "1") != "1":
                        ref.add(v["unit"])
        fetch_labels(net, cache, ref, log)
        log(f"  {net.count} requests this run")

    return export(cache, subs, topics, rlinks, log)


def export(cache, subs, topics, rlinks, log):
    EXPORT.parent.mkdir(parents=True, exist_ok=True)
    tmp = EXPORT.with_suffix(".tmp")
    counts = {"substances": 0, "with article": 0, "no article": 0, "topics": 0, "topic misses": 0}
    misses = []
    with lzma.open(tmp, "wt", encoding="utf-8", preset=9) as f:
        def w(rec):
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

        w({"type": "meta", "made": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "tool": "scrape_wiki.py 1"})
        for t in subs:
            c = candidates(t, cache)
            counts["substances"] += 1
            counts["with article" if c else "no article"] += 1
            if not c:
                misses.append(f"substance {t['id']} {t['name']} ({t['formula']}, CAS {t['cas']})")
            w({"type": "substance", "id": t["id"], "key": t["key"], "name": t["name"], "formula": t["formula"],
               "stage": t["stage"], "cas": t["cas"], "links": t["links"], "candidates": c,
               "cas_items": cache.get("cas", t["cas"]) if t["cas"] else None})
        for key, (unit, kind, title) in topics.items():
            info = cache.get("title", title) or {}
            counts["topics"] += 1
            if info.get("missing") or not info.get("pageid"):
                counts["topic misses"] += 1
                misses.append(f"topic {key}: no article titled {title!r}")
            w({"type": "topic", "key": key, "unit": unit, "kind": kind, "asked": title,
               "pageid": info.get("pageid"), "title": info.get("title"),
               "disambiguation": info.get("disambiguation", False)})
        for k, v in rlinks:
            info = cache.get(k, v) or {}
            w({"type": "reaction_link", "kind": k, "value": v, "pageid": info.get("pageid"), "title": info.get("title")})
        for src, titles in cache.all("pool"):
            w({"type": "pool", "source": src,
               "pages": [(cache.get("title", t) or {}).get("pageid") for t in titles]})
        n_full = n_lead = 0
        for _, p in cache.all("page"):
            n_full += 1
            w(dict(p, type="page"))
        for pid, p in cache.all("lead"):
            if not cache.has("page", pid):
                n_lead += 1
                w(dict(p, type="page"))
        for _, e in cache.all("entity"):
            w(dict(e, type="entity"))
        for q, l in cache.all("label"):
            w(dict(l, type="label", qid=q))
        for _, t in cache.all("template"):
            w(dict(t, type="template"))
    tmp.replace(EXPORT)
    report = OUT / "report.txt"
    report.write_text("\n".join(f"{k}: {v}" for k, v in counts.items()) + "\n\n" + "\n".join(misses) + "\n",
                      encoding="utf-8")
    mb = EXPORT.stat().st_size / 1e6
    log("")
    log(f"Substances: {counts['substances']}, with an article: {counts['with article']}, "
        f"none found: {counts['no article']}")
    log(f"Topics: {counts['topics']}, not found: {counts['topic misses']}")
    log(f"Articles: {n_full} whole, {n_lead} leads")
    log(f"Wrote {EXPORT} ({mb:.1f} MB) and {report}")
    log("Upload pages.jsonl.xz to Claude.")
    return counts


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--limit", type=int, default=0, help="only the first N substances (a trial run)")
    ap.add_argument("--export-only", action="store_true", help="write the export from the cache")
    ap.add_argument("--refresh", action="store_true", help="forget the cache and fetch everything again")
    args = ap.parse_args()
    t0 = time.time()
    cache = Cache(DB)
    try:
        run(args, cache=cache)
    except KeyboardInterrupt:
        cache.commit()
        print("\nStopped. Everything fetched so far is cached; run it again to carry on.")
        sys.exit(1)
    except Exception:
        cache.commit()
        print("\nThe run stopped on an error (below). Everything fetched so far is cached; run it again to carry on.")
        raise
    print(f"Done in {(time.time() - t0) / 60:.1f} min.")


if __name__ == "__main__":
    main()
