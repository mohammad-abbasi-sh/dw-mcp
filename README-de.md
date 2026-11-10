# dw-mcp 📰

mcp-name: io.github.mohammad-abbasi-sh/dw-mcp

Inoffizieller **nur lesender** MCP-Server für **[dw.com](https://www.dw.com)** — Deutsche-Welle-Nachrichten in 31 Sprachen über die offiziellen DW-Sitemaps: neueste Schlagzeilen, Stichwortsuche, neueste Artikel, Volltexte und Themenseiten. Kein Schlüssel, kein Login. Kein Schlüssel, keine Anmeldung.

> Gebaut von Mohammad Abbasi als Teil der "Germany MCP factory". Nicht mit dw.com verbunden.

## Für KI-Agenten

Zur MCP-Client-Konfiguration hinzufügen (stdio):

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

Oder lokal starten: `python -m dw_mcp.server` (benötigt `mcp<2`, `httpx`).

## Tools

| Tool | Beschreibung |
|------|-------------|
| `dw_headlines` | Neueste DW-Schlagzeilen in einer Sprache |
| `dw_search_news` | Neueste DW-Schlagzeilen nach Stichwort suchen |
| `dw_latest_articles` | Neueste DW-Artikel in einer Sprache |
| `dw_get_article` | Volltext eines DW-Artikels |
| `dw_topics` | DW-Themenseiten zu einem Stichwort |
| `dw_health` | Erreichbarkeitsprüfung (ok / blocked / error) — eine höfliche Anfrage |

## Entwicklung

```bash
python3 -m venv .venv && .venv/bin/pip install "mcp<2" httpx pytest
.venv/bin/pip install -e .
.venv/bin/python -m pytest tests/ -q
```

## Lizenz

MIT

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
