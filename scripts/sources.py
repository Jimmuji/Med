"""
Medical AI / Health Tech data source fetchers.
All free, no auth needed. Returns list of dicts: {title, url, summary, source}
"""

import re
import requests
import feedparser
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode


# ── Helpers ──────────────────────────────────────────────────────────────────

def clean_text(html: str) -> str:
    """Strip HTML tags and normalize whitespace."""
    text = re.sub(r"<[^>]+>", " ", html or "")
    return re.sub(r"\s+", " ", text).strip()


def normalize_url(url: str) -> str:
    """Remove UTM and tracking parameters from URLs."""
    if not url:
        return url
    parsed = urlparse(url)
    qs = {k: v for k, v in parse_qs(parsed.query).items()
          if not k.lower().startswith(("utm_", "ref", "source", "mc_"))}
    clean = parsed._replace(query=urlencode(qs, doseq=True))
    return urlunparse(clean)


def dedupe_items(items: list) -> list:
    """Remove duplicate items by URL and title similarity."""
    seen_urls, seen_titles, out = set(), set(), []
    for item in items:
        url = normalize_url(item.get("url", ""))
        title = item.get("title", "").strip().lower()[:80]
        if url in seen_urls or title in seen_titles:
            continue
        seen_urls.add(url)
        seen_titles.add(title)
        item["url"] = url
        out.append(item)
    return out


def importance_hint(item: dict) -> int:
    """Score 1-5 based on source and content signals."""
    score = 3
    title = (item.get("title") or "").lower()
    summary = (item.get("summary") or "").lower()
    text = title + " " + summary

    high_signals = ["fda", "approval", "approved", "clinical trial", "phase 3",
                    "breakthrough", "launch", "acquisition", "ipo", "funding",
                    "study", "research", "ai", "machine learning", "deep learning"]
    boost = sum(1 for s in high_signals if s in text)
    score = min(5, score + (boost // 2))

    if item.get("source") in ("STAT News", "Fierce Biotech"):
        score = min(5, score + 1)
    return score


# ── Data Sources ─────────────────────────────────────────────────────────────

MEDICAL_KEYWORDS = [
    # Clinical / patient
    "medic", "clinic", "patient", "hospital", "physician", "doctor",
    # Disease / condition
    "cancer", "tumor", "disease", "disorder", "syndrome", "diabetes",
    "alzheimer", "dementia", "cardiovascular", "cardiac", "covid",
    # Treatment / intervention
    "drug", "therapy", "treatment", "diagnos", "prognos", "surgery",
    "vaccine", "immunotherapy", "chemotherapy", "radiation",
    # Industry / regulatory
    "pharma", "biotech", "fda", "ehr", "clinical trial", "approval",
    # Biomedical science
    "genomic", "genome", "protein", "biomarker", "crispr", "patholog",
    "radiology", "imaging", "histolog", "biopsy",
    # Digital health
    "digital health", "telemedicine", "wearable", "health record",
    "bioinformat", "electronic health",
]


def fetch_rss_feed(feed_url: str, source_name: str, max_items: int = 15,
                   filter_medical: bool = False) -> list:
    """Generic RSS fetcher with optional medical keyword filter."""
    items = []
    try:
        resp = requests.get(feed_url, timeout=20,
                            headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        cutoff = datetime.now(timezone.utc) - timedelta(days=2)

        for entry in feed.entries[:max_items * 2]:
            published = entry.get("published_parsed") or entry.get("updated_parsed")
            if published:
                entry_date = datetime(*published[:6], tzinfo=timezone.utc)
                if entry_date < cutoff:
                    continue

            title = entry.get("title", "")
            summary = clean_text(entry.get("summary", ""))[:600]

            if filter_medical:
                text = (title + " " + summary).lower()
                if not any(kw in text for kw in MEDICAL_KEYWORDS):
                    continue

            item = {
                "title": title,
                "url": entry.get("link", ""),
                "summary": summary,
                "source": source_name,
                "published": entry.get("published", ""),
            }
            item["importance_hint"] = importance_hint(item)
            items.append(item)

            if len(items) >= max_items:
                break

    except Exception as e:
        print(f"  [{source_name}] Error: {e}")
    return items


def fetch_huggingface_medical_papers() -> list:
    """Fetch HuggingFace daily papers filtered for medical/biomedical content."""
    items = []
    try:
        resp = requests.get("https://huggingface.co/api/daily_papers", timeout=20)
        resp.raise_for_status()
        papers = resp.json()

        for p in papers:
            paper = p.get("paper", {})
            title = paper.get("title", "")
            summary = paper.get("summary", "")[:600]
            text = (title + " " + summary).lower()

            if any(kw in text for kw in MEDICAL_KEYWORDS):
                item = {
                    "title": title,
                    "url": f"https://huggingface.co/papers/{paper.get('id', '')}",
                    "summary": summary,
                    "source": "HuggingFace Papers (Medical)",
                    "published": p.get("publishedAt", ""),
                }
                item["importance_hint"] = importance_hint(item)
                items.append(item)

    except Exception as e:
        print(f"  [HuggingFace Medical Papers] Error: {e}")
    return items


# ── Source Registry ───────────────────────────────────────────────────────────

RSS_SOURCES = [
    # English — Medical / Health Tech / Biotech
    ("https://www.statnews.com/feed/",          "STAT News",        15, False),
    ("https://www.fiercehealthcare.com/rss/xml", "Fierce Healthcare", 12, False),
    ("https://www.fiercebiotech.com/rss/xml",    "Fierce Biotech",    12, False),
    # Chinese — Medical AI / Health Tech
    ("https://rsshub.rssforever.com/36kr/search/articles/医疗AI",   "36Kr 医疗AI",   12, False),
    ("https://rsshub.rssforever.com/36kr/search/articles/医疗科技", "36Kr 医疗科技", 12, False),
]


def fetch_all() -> dict:
    """Fetch from all sources, return categorized + deduped data."""
    print("Fetching HuggingFace Medical Papers...")
    papers = fetch_huggingface_medical_papers()
    print(f"  Got {len(papers)} medical papers")

    print("Fetching RSS feeds...")
    news = []
    for url, name, max_n, medical_filter in RSS_SOURCES:
        feed_items = fetch_rss_feed(url, name, max_items=max_n,
                                    filter_medical=medical_filter)
        print(f"  [{name}] Got {len(feed_items)} items")
        news.extend(feed_items)

    news = dedupe_items(news)
    papers = dedupe_items(papers)
    print(f"Deduped to {len(news)} news + {len(papers)} papers")

    return {"news": news, "papers": papers}
