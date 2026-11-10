"""MCP server: unofficial read-only access to Deutsche Welle news via
DW's official sitemaps + article pages. 31 language editions, no key,
no login. NOTE: DW has no working RSS feeds any more (all /rss/ paths
404, verified 2026-11-10) — headlines come from the news sitemaps."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

from . import domain as _dom
from . import http as _http

INSTRUCTIONS = """\
Unofficial read-only MCP server for Deutsche Welle news via DW's \
official sitemaps (no key, no login): latest headlines, keyword \
search over the latest headlines, latest articles, full article \
text and topic pages — in 31 languages (en, de, fa-ir, fa-af, ar, \
tr, ...). Persian is "fa-ir" (Iran) or "fa-af" (Afghanistan/Dari); \
plain "fa" is not a DW edition. NOTE: DW has no working RSS feeds \
any more — headlines come from the news sitemaps, and search covers \
only the latest ~50 headlines, not the full archive. Built by \
Mohammad Abbasi (mohammad-abbasi-sh) — https://almanibama.ir · \
https://mabbasi.ir — Germany MCP factory.\
"""

_SOURCE = "dw.com"
_DISCLAIMER = "Unofficial read-only data from dw.com sitemaps and article pages; verify on the site before acting on it."


def _envelope() -> dict:
    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": _SOURCE,
        "disclaimer": _DISCLAIMER,
    }


def _ok(payload: dict) -> str:
    return json.dumps({**_envelope(), **payload}, ensure_ascii=False)


def _err(e: Exception) -> str:
    return _ok({"error": str(e)})


mcp = FastMCP("dw-mcp", instructions=INSTRUCTIONS)


@mcp.tool()
def dw_headlines(language: str = "en", limit: int = 10) -> str:
    """Latest DW headlines in one language. language: e.g. "en", "de",
    "fa-ir" (Iran Persian), "tr". limit: 1..50 (default 10)."""
    try:
        lang = _dom.validate_language(language)
        lim = _dom.validate_limit(limit)
        items = _dom.parse_news_sitemap(
            _http.fetch_text(_dom.news_sitemap_url(lang)))
    except (_http.DwMcpError, ValueError) as e:
        return _err(e)
    return _ok({"language": lang, "total_results": len(items),
                "count": min(lim, len(items)), "items": items[:lim]})


@mcp.tool()
def dw_search_news(query: str, language: str = "en", limit: int = 10) -> str:
    """Keyword search over the LATEST DW headlines (the news sitemap
    holds roughly the last 50 — this is not a full-archive search).
    query: keyword or phrase. language: e.g. "en", "de", "fa-ir".
    limit: 1..50 (default 10)."""
    try:
        lang = _dom.validate_language(language)
        lim = _dom.validate_limit(limit)
        q = (query or "").strip()
        if not q:
            raise ValueError("query must not be empty")
        items = _dom.parse_news_sitemap(
            _http.fetch_text(_dom.news_sitemap_url(lang)))
        ql = q.casefold()
        hits = [i for i in items if ql in i["title"].casefold()]
    except (_http.DwMcpError, ValueError) as e:
        return _err(e)
    return _ok({"language": lang, "query": q,
                "searched": "latest headlines in the DW news sitemap",
                "total_results": len(hits),
                "count": min(lim, len(hits)), "items": hits[:lim]})


@mcp.tool()
def dw_latest_articles(language: str = "en", limit: int = 10) -> str:
    """Latest DW articles in one language, newest first.
    language: e.g. "en", "de", "fa-ir". limit: 1..50 (default 10)."""
    try:
        lang = _dom.validate_language(language)
        lim = _dom.validate_limit(limit)
        items = _dom.parse_article_sitemap(
            _http.fetch_text(_dom.article_sitemap_url(lang)))
    except (_http.DwMcpError, ValueError) as e:
        return _err(e)
    return _ok({"language": lang, "total_results": len(items),
                "count": min(lim, len(items)), "items": items[:lim]})


@mcp.tool()
def dw_get_article(url: str) -> str:
    """Full text of one DW article. url: a dw.com article link, e.g.
    https://www.dw.com/en/.../a-12345678 (live blogs and video pages
    may return little or no body text)."""
    try:
        u = (url or "").strip()
        if not u.startswith("https://www.dw.com/"):
            raise ValueError("url must be a dw.com article link "
                             "(https://www.dw.com/...)")
        out = _dom.parse_article(_http.fetch_text(u))
        if not out["headline"] and not out["body"]:
            raise ValueError("no article content found at that URL "
                             "(it may be a live blog, video or topic page)")
    except (_http.DwMcpError, ValueError) as e:
        return _err(e)
    return _ok({"url": u, "headline": out["headline"],
                "published": out["published"],
                "body": out["body"][:6000]})


@mcp.tool()
def dw_topics(query: str = "", language: str = "en", limit: int = 10) -> str:
    """DW topic pages matching a word (e.g. "bundesliga", "klima").
    With no query, returns the most recently updated topics.
    language: e.g. "en", "de". limit: 1..50 (default 10)."""
    try:
        lang = _dom.validate_language(language)
        lim = _dom.validate_limit(limit)
        items = _dom.parse_topic_sitemap(
            _http.fetch_text(_dom.topic_sitemap_url(lang)))
        q = (query or "").strip().casefold()
        if q:
            items = [i for i in items
                     if q in i["name"].casefold() or q in i["url"].casefold()]
    except (_http.DwMcpError, ValueError) as e:
        return _err(e)
    return _ok({"language": lang, "query": query,
                "total_results": len(items),
                "count": min(lim, len(items)), "items": items[:lim]})


@mcp.tool()
def dw_health() -> str:
    """Check whether dw.com is reachable right now.

    Returns status ok (HTTP 200), blocked (HTTP 403/429 — bot wall or
    rate limit) or error, plus the HTTP status and the probed URL.
    One polite request; it does not fetch any listings."""
    return _ok(_http.health_check())


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    sys.exit(main())
