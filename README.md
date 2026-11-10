# dw-mcp 📰

mcp-name: io.github.mohammad-abbasi-sh/dw-mcp

Unofficial **read-only** MCP server for **[dw.com](https://www.dw.com)** — Deutsche Welle news in 31 languages from DW's official sitemaps: latest headlines, keyword search over recent headlines, latest articles, full article text and topic pages. No key, no login. No key, no login.

> Built by Mohammad Abbasi as part of the "Germany MCP factory". Not affiliated with dw.com.

## For AI agents

Add to your MCP client config (stdio):

```json
{
  "mcpServers": {
    "dw": {
      "command": "uvx",
      "args": ["dw-mcp==0.1.0"]
    }
  }
}
```

Or run locally: `python -m dw_mcp.server` (needs `mcp<2`, `httpx`).

## Tools

| Tool | Description |
|------|-------------|
| `dw_headlines` | Latest DW headlines — `language` (e.g. "en", "de", "fa-ir"), `limit` 1..50 |
| `dw_search_news` | Keyword search over the latest DW headlines — `query`, `language`, `limit` 1..50 |
| `dw_latest_articles` | Latest DW articles by publication time — `language`, `limit` 1..50 |
| `dw_get_article` | Full text of one DW article — `url` (a dw.com article link) |
| `dw_topics` | DW topic pages matching a word — `query`, `language`, `limit` 1..50 |
| `dw_health` | Reachability probe (ok / blocked / error) — one polite request |

## Notes

- All data comes from **DW's official sitemaps** (free, no key, no login).
- DW has **no working RSS feeds any more** — every `/rss/` path returns 404 (verified 2026-11-10) — and its site search is gone, so headlines come from the news sitemaps and `dw_search_news` filters the latest ~50 headlines (not the full archive).
- Persian is two editions: `fa-ir` (Iran) and `fa-af` (Afghanistan/Dari); plain `fa` does not exist.
- Article bodies are extracted from DW's server-rendered pages (JSON-LD headline/date + cleaned `<p>` text); live blogs and video pages may return little or no body text.

Tests: 22/22 green (15 offline + 7 live, 2026-11-10).

## Development

```bash
python3 -m venv .venv && .venv/bin/pip install "mcp<2" httpx pytest
.venv/bin/pip install -e .
.venv/bin/python -m pytest tests/ -q
```

## License

MIT

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
