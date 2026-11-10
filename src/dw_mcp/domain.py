"""Domain logic: shape Deutsche Welle sitemap XML + article HTML into
compact dicts (stdlib only).

Data source: DW's official sitemaps
(https://www.dw.com/{lang}/news-sitemap.xml,
/{lang}/article-sitemap.xml, /{lang}/auto-topic-sitemap.xml) and
dw.com article pages — free, no key, no login.

DW has NO working RSS feeds any more (all /rss/ paths 404, verified
2026-11-10) and its site search is gone too, so `dw_search_news`
filters the latest news-sitemap headlines by keyword — it searches
the ~last 50 headlines, not the full archive, and says so.
"""
from __future__ import annotations

import html as _html
import json
import re
import xml.etree.ElementTree as ET

BASE = "https://www.dw.com"

# Language editions with a news sitemap (from the DW sitemap index,
# verified 2026-11-10). Note: Persian is "fa-ir" (Iran) and "fa-af"
# (Afghanistan/Dari) — plain "fa" 400s.
LANGUAGES = {
    "am", "ar", "bg", "bn", "bs", "de", "el", "en", "es", "fa-af",
    "fa-ir", "fr", "ha", "hi", "hr", "id", "mk", "pl", "ps",
    "pt-002", "pt-br", "ro", "ru", "sq", "sr", "sw", "tr", "uk",
    "ur", "zh", "zh-hant",
}

_NS = {
    "s": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "n": "http://www.google.com/schemas/sitemap-news/0.9",
}

_LD_RE = re.compile(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', re.S)
_P_RE = re.compile(r'<p[^>]*>(.*?)</p>', re.S)
_TAG_RE = re.compile(r'<[^>]+>')
_SHORT_URL_RE = re.compile(r'^https?://p\.dw\.com/p/\S+?Prefer DW on Google\s*')
_SHORT_URL_BARE_RE = re.compile(r'^https?://p\.dw\.com/p/\S+\s+')


def validate_language(language: str) -> str:
    key = (language or "").strip().lower()
    if key not in LANGUAGES:
        raise ValueError(
            f"unsupported language: {language!r} "
            f"(use one of: {', '.join(sorted(LANGUAGES))})"
        )
    return key


def validate_limit(limit: int) -> int:
    if not 1 <= limit <= 50:
        raise ValueError(f"limit out of range: {limit} (expected 1..50)")
    return limit


def news_sitemap_url(language: str) -> str:
    return f"{BASE}/{language}/news-sitemap.xml"


def article_sitemap_url(language: str) -> str:
    return f"{BASE}/{language}/article-sitemap.xml"


def topic_sitemap_url(language: str) -> str:
    return f"{BASE}/{language}/auto-topic-sitemap.xml"


def _parse_xml(text: str, what: str) -> ET.Element:
    try:
        return ET.fromstring(text)
    except ET.ParseError as e:
        raise ValueError(f"invalid {what}: {e}") from e


def parse_news_sitemap(text: str) -> list[dict]:
    """[{title, url, published}] — newest first (sitemap order)."""
    root = _parse_xml(text, "news sitemap")
    out = []
    for url in root.findall("s:url", _NS):
        news = url.find("n:news", _NS)
        if news is None:
            continue
        out.append({
            "title": news.findtext("n:title", namespaces=_NS) or "",
            "url": url.findtext("s:loc", namespaces=_NS) or "",
            "published": news.findtext("n:publication_date", namespaces=_NS) or "",
        })
    return out


def parse_article_sitemap(text: str) -> list[dict]:
    """[{url, lastmod}] — sorted newest first by lastmod."""
    root = _parse_xml(text, "article sitemap")
    out = []
    for url in root.findall("s:url", _NS):
        out.append({
            "url": url.findtext("s:loc", namespaces=_NS) or "",
            "lastmod": url.findtext("s:lastmod", namespaces=_NS) or "",
        })
    out.sort(key=lambda e: e["lastmod"], reverse=True)
    return out


def parse_topic_sitemap(text: str) -> list[dict]:
    """[{name, url, lastmod}] — name derived from the topic slug."""
    root = _parse_xml(text, "topic sitemap")
    out = []
    for url in root.findall("s:url", _NS):
        loc = url.findtext("s:loc", namespaces=_NS) or ""
        slug = loc.rstrip("/").split("/")[-2] if "/t-" in loc else ""
        name = slug.replace("-", " ").strip().title() if slug else ""
        out.append({
            "name": name,
            "url": loc,
            "lastmod": url.findtext("s:lastmod", namespaces=_NS) or "",
        })
    out.sort(key=lambda e: e["lastmod"], reverse=True)
    return out


def parse_article(html_text: str) -> dict:
    """Extract headline/date (JSON-LD NewsArticle) + cleaned body <p>s.

    DW article pages are server-rendered: the body is plain <p> tags.
    The first <p> is navigation junk ("Skip to main menu...") and is
    dropped; the intro paragraph carries a leading p.dw.com short URL
    + "Prefer DW on Google" prefix which is stripped.
    """
    headline, published = "", ""
    m = _LD_RE.search(html_text)
    if m:
        try:
            ld = json.loads(m.group(1))
            if isinstance(ld, dict) and ld.get("@type") == "NewsArticle":
                headline = ld.get("headline") or ""
                published = ld.get("datePublished") or ""
        except json.JSONDecodeError:
            pass
    paras = []
    for raw in _P_RE.findall(html_text):
        txt = _html.unescape(_TAG_RE.sub("", raw)).replace("\u00a0", " ").strip()
        if not txt:
            continue
        if txt.startswith("Skip to main menu"):
            continue
        txt = _SHORT_URL_RE.sub("", txt)
        txt = _SHORT_URL_BARE_RE.sub("", txt)
        txt = txt.strip()
        if txt:
            paras.append(txt)
    body = "\n\n".join(paras)
    return {"headline": headline, "published": published, "body": body}
