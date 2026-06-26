#!/usr/bin/env python3
"""
Sonoluminescence Paper Spider
==============================
Hunts papers from arXiv, PubMed, and Semantic Scholar.
Auto-sorts into foundational / modern / frontier by year.
Saves metadata as JSON + human-readable notes.

Usage:
  python3 fetch_arxiv.py                       # full hunt
  python3 fetch_arxiv.py --query "ROS cavitation"  # custom search
  python3 fetch_arxiv.py --id 2311.03305       # specific arXiv ID
  python3 fetch_arxiv.py --list                # show all saved papers
"""

import os, sys, json, time, argparse, textwrap
import urllib.request, urllib.parse, urllib.error
from datetime import datetime
from pathlib import Path

BASE   = Path.home() / "sonoluminescence"
PAPERS = BASE / "03_papers"
FOUND  = PAPERS / "foundational"
MODERN = PAPERS / "modern"
FRONT  = PAPERS / "frontier"
NOTES  = PAPERS / "notes"
INDEX  = PAPERS / "index.json"

for d in [FOUND, MODERN, FRONT, NOTES]:
    d.mkdir(parents=True, exist_ok=True)

def classify_era(year):
    if not year:       return "modern",      MODERN
    if year < 2000:    return "foundational", FOUND
    if year <= 2020:   return "modern",      MODERN
    return "frontier", FRONT

def load_index():
    return json.loads(INDEX.read_text()) if INDEX.exists() else {}

def save_index(idx):
    INDEX.write_text(json.dumps(idx, indent=2))

def fetch_url(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent":"SLSpider/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8")

def safe(s, n=None):
    if not s: return ""
    s = s.replace("\n"," ").replace("  "," ").strip()
    return s[:n] if n else s

def write_note(p, folder):
    safe_id = p["id"].replace("/","_").replace(":","_")
    path = NOTES / f"{safe_id}.md"
    path.write_text(f"""# {p.get('title','?')}

## Metadata
- **Source**  : {p.get('source','?')}
- **ID**      : {p.get('id','?')}
- **Authors** : {p.get('authors','?')}
- **Year**    : {p.get('year','?')}
- **Era**     : {folder.name}
- **DOI**     : {p.get('doi','N/A')}
- **URL**     : {p.get('url','N/A')}
- **Fetched** : {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Abstract
{p.get('abstract','No abstract available.')}

## My Notes


## Key Equations


## Relevance to SDT
<!-- How does this connect to sonodynamic cancer therapy? -->

## Questions Raised

""")
    return path

def save_paper(paper, index):
    pid = paper["id"]
    if pid in index:
        return False, "already indexed"
    era, folder = classify_era(paper.get("year"))
    paper["era"] = era
    note = write_note(paper, folder)
    index[pid] = {
        "title"  : paper.get("title",""),
        "authors": paper.get("authors",""),
        "year"   : paper.get("year"),
        "era"    : era,
        "source" : paper.get("source",""),
        "url"    : paper.get("url",""),
        "pdf_url": paper.get("pdf_url",""),
        "doi"    : paper.get("doi",""),
        "note"   : str(note),
        "saved"  : datetime.now().strftime("%Y-%m-%d"),
    }
    return True, str(note)

def print_paper(p, info=None):
    era = p.get('era','?').upper()
    print(f"\n{'─'*60}")
    print(f"  [{era}] {p.get('title','?')[:65]}")
    print(f"  Authors : {p.get('authors','?')[:70]}")
    print(f"  Year    : {p.get('year','?')}  |  Source: {p.get('source','?')}")
    if p.get('url'):   print(f"  URL     : {p['url']}")
    if p.get('abstract'):
        ab = p['abstract'][:300] + ("..." if len(p['abstract'])>300 else "")
        print(f"  Abstract: {ab}")
    if info: print(f"  → Saved : {info}")

# ── arXiv ──────────────────────────────────────────────────
def parse_arxiv_xml(xml):
    import re
    papers = []
    for entry in xml.split("<entry>")[1:]:
        def tag(t):
            s,e = entry.find(f"<{t}>"), entry.find(f"</{t}>")
            return entry[s+len(t)+2:e].strip() if s!=-1 and e!=-1 else ""
        raw_id = tag("id")
        aid = raw_id.split("/abs/")[-1].strip() if "/abs/" in raw_id else raw_id
        pub = tag("published")
        year = int(pub[:4]) if pub and len(pub)>=4 else None
        authors = ", ".join(re.findall(r"<name>(.*?)</name>", entry))
        papers.append({
            "id":aid, "title":safe(tag("title")),
            "authors":safe(authors), "abstract":safe(tag("summary")),
            "year":year, "source":"arxiv",
            "url":f"https://arxiv.org/abs/{aid}",
            "pdf_url":f"https://arxiv.org/pdf/{aid}", "doi":"",
        })
    return papers

def search_arxiv(query, n=8):
    print(f"  🔍 arXiv: {query}")
    enc = urllib.parse.quote(query)
    url = f"https://export.arxiv.org/api/query?search_query=all:{enc}&max_results={n}&sortBy=relevance"
    try:
        return parse_arxiv_xml(fetch_url(url))
    except Exception as e:
        print(f"     ⚠ {e}"); return []

def fetch_arxiv_id(aid):
    print(f"  🔍 arXiv ID: {aid}")
    url = f"https://export.arxiv.org/api/query?id_list={aid}"
    try:
        results = parse_arxiv_xml(fetch_url(url))
        return results[0] if results else None
    except Exception as e:
        print(f"     ⚠ {e}"); return None

# ── Semantic Scholar ───────────────────────────────────────
def search_semantic(query, n=6):
    print(f"  🔍 Semantic Scholar: {query}")
    enc = urllib.parse.quote(query)
    url = (f"https://api.semanticscholar.org/graph/v1/paper/search"
           f"?query={enc}&limit={n}"
           f"&fields=title,authors,year,abstract,externalIds,openAccessPdf,url")
    try:
        data = json.loads(fetch_url(url)).get("data",[])
    except Exception as e:
        print(f"     ⚠ {e}"); return []
    papers = []
    for item in data:
        authors = ", ".join(a.get("name","") for a in item.get("authors",[])[:5])
        ext = item.get("externalIds",{})
        pdf = item.get("openAccessPdf") or {}
        papers.append({
            "id":item.get("paperId",""), "title":safe(item.get("title","")),
            "authors":safe(authors), "abstract":safe(item.get("abstract","")),
            "year":item.get("year"), "source":"semantic_scholar",
            "url":item.get("url",""), "doi":ext.get("DOI",""),
            "pdf_url":pdf.get("url","") if isinstance(pdf,dict) else "",
        })
    return papers

# ── PubMed ─────────────────────────────────────────────────
def search_pubmed(query, n=6):
    print(f"  🔍 PubMed: {query}")
    enc = urllib.parse.quote(query)
    try:
        ids = json.loads(fetch_url(
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            f"?db=pubmed&term={enc}&retmax={n}&retmode=json"
        )).get("esearchresult",{}).get("idlist",[])
        if not ids: return []
        data = json.loads(fetch_url(
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            f"?db=pubmed&id={','.join(ids)}&retmode=json"
        )).get("result",{})
    except Exception as e:
        print(f"     ⚠ {e}"); return []
    papers = []
    for pmid in ids:
        item = data.get(pmid,{})
        authors = ", ".join(a.get("name","") for a in item.get("authors",[])[:5])
        pub = item.get("pubdate","")
        year = int(pub[:4]) if pub and pub[:4].isdigit() else None
        papers.append({
            "id":f"pmid:{pmid}", "title":safe(item.get("title","")),
            "authors":safe(authors), "abstract":"",
            "year":year, "source":"pubmed",
            "url":f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "pdf_url":"", "doi":item.get("elocationid","").replace("doi: ",""),
        })
    return papers

# ── Query list ─────────────────────────────────────────────
QUERIES = {
    "arxiv": [
        "sonoluminescence bubble dynamics",
        "single bubble sonoluminescence plasma",
        "acoustic cavitation Rayleigh-Plesset",
        "sonodynamic therapy cancer ultrasound",
        "sonoluminescence quantum photon statistics",
        "cavitation ROS reactive oxygen species tumor",
        "Keller-Miksis bubble collapse simulation",
        "sonochemistry hydroxyl radical generation",
    ],
    "semantic": [
        "sonoluminescence review bubble collapse",
        "sonodynamic therapy sonosensitizer mechanism",
        "single bubble sonoluminescence emission spectrum",
        "ultrasound cancer therapy reactive oxygen",
    ],
    "pubmed": [
        "sonodynamic therapy cancer apoptosis",
        "ultrasound cavitation tumor ROS",
        "sonosensitizer porphyrin ultrasound",
    ],
}

# ── Main ───────────────────────────────────────────────────
def run(custom_query=None, arxiv_id=None, list_only=False):
    index = load_index()

    if list_only:
        if not index:
            print("\n📭 Nothing indexed yet. Run the spider first.\n")
            return
        by_era = {"foundational":[], "modern":[], "frontier":[]}
        for pid,p in index.items():
            by_era.get(p.get("era","modern"), by_era["modern"]).append(p)
        print(f"\n📚 Total indexed: {len(index)}\n")
        for era, papers in by_era.items():
            if not papers: continue
            print(f"\n── {era.upper()} ({len(papers)}) {'─'*38}")
            for p in sorted(papers, key=lambda x: x.get("year") or 0):
                print(f"  [{p.get('year','?')}] {p.get('title','?')[:65]}")
                print(f"         {p.get('source','?')} | {p.get('url','')[:55]}")
        return

    if arxiv_id:
        p = fetch_arxiv_id(arxiv_id)
        if p:
            saved, info = save_paper(p, index)
            print_paper(p, info)
            save_index(index)
        return

    if custom_query:
        all_papers = (search_arxiv(custom_query, 6) +
                      search_semantic(custom_query, 5) +
                      search_pubmed(custom_query, 5))
    else:
        print("\n🕷  Full spider starting...\n")
        all_papers = []
        for q in QUERIES["arxiv"]:
            all_papers += search_arxiv(q, 5); time.sleep(1)
        for q in QUERIES["semantic"]:
            all_papers += search_semantic(q, 4); time.sleep(0.5)
        for q in QUERIES["pubmed"]:
            all_papers += search_pubmed(q, 4); time.sleep(0.5)

    # deduplicate
    seen, unique = set(), []
    for p in all_papers:
        t = p.get("title","").lower()[:60]
        if t and t not in seen:
            seen.add(t); unique.append(p)

    print(f"\n📄 Saving {len(unique)} unique papers...\n")
    new = 0
    for p in unique:
        saved, info = save_paper(p, index)
        if saved:
            new += 1
            print_paper(p, info)

    save_index(index)
    print(f"\n{'═'*60}")
    print(f"  ✅ Done — {new} new papers | {len(index)} total indexed")
    print(f"  Notes  → 03_papers/notes/")
    print(f"  Index  → 03_papers/index.json")
    print(f"  List   → python3 fetch_arxiv.py --list")
    print(f"{'═'*60}\n")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="SL Paper Spider")
    ap.add_argument("--query","-q", help="Custom search query")
    ap.add_argument("--id",   "-i", help="Fetch specific arXiv ID")
    ap.add_argument("--list", "-l", action="store_true")
    args = ap.parse_args()
    run(custom_query=args.query, arxiv_id=args.id, list_only=args.list)
