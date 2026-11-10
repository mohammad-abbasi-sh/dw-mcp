# dw-mcp 📰

mcp-name: io.github.mohammad-abbasi-sh/dw-mcp

سرور MCP غیررسمی و **فقط‌خواندنی** برای **[dw.com](https://www.dw.com)** — اخبار دویچه‌وله به ۳۱ زبان از سایت‌مپ‌های رسمی DW: تازه‌ترین تیترها، جست‌وجوی کلیدواژه، تازه‌ترین مقاله‌ها، متن کامل مقاله و صفحه‌های موضوعی. بدون کلید، بدون ورود. بدون کلید، بدون ورود.

> ساختهٔ محمد عباسی، بخشی از «کارخانهٔ MCP آلمان». وابسته به dw.com نیست.

## برای ایجنت‌های هوش مصنوعی

به پیکربندی MCP کلاینت اضافه کنید (stdio):

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

یا به‌صورت محلی اجرا کنید: `python -m dw_mcp.server` (نیازمند `mcp<2` و `httpx`).

## ابزارها

| ابزار | توضیح |
|------|-------|
| `dw_headlines` | تازه‌ترین تیترهای DW به یک زبان |
| `dw_search_news` | جست‌وجوی تیترهای اخیر DW با کلیدواژه |
| `dw_latest_articles` | تازه‌ترین مقاله‌های DW به یک زبان |
| `dw_get_article` | متن کامل یک مقالهٔ DW |
| `dw_topics` | صفحه‌های موضوعی DW برای یک واژه |
| `dw_health` | بررسی دسترس‌پذیری (ok / blocked / error) — یک درخواست مؤدبانه |

## توسعه

```bash
python3 -m venv .venv && .venv/bin/pip install "mcp<2" httpx pytest
.venv/bin/pip install -e .
.venv/bin/python -m pytest tests/ -q
```

## لایسنس

MIT

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
