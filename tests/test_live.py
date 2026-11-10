"""Live tests — hit the real dw.com sitemaps + one article. Cautious: few requests.

Run:  pytest tests/test_live.py -v
Skip: pytest -m "not live"  (or set DW_SKIP_LIVE=1)
"""
import json
import os
import pathlib
import sys
import unittest

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from dw_mcp import server as srv

pytestmark = pytest.mark.live
SKIP = os.environ.get("DW_SKIP_LIVE") == "1"


@pytest.mark.skipif(SKIP, reason="DW_SKIP_LIVE=1")
class TestLive(unittest.TestCase):
    def test_headlines_en_live(self):
        out = json.loads(srv.dw_headlines("en", limit=3))
        self.assertNotIn("error", out)
        self.assertGreaterEqual(out["total_results"], 1)
        print(f"\nLIVE headlines EN: {out['total_results']} — {out['items'][0]['title'][:60]}")

    def test_headlines_fa_ir_live(self):
        out = json.loads(srv.dw_headlines("fa-ir", limit=3))
        self.assertNotIn("error", out)
        self.assertGreaterEqual(out["total_results"], 1)
        print(f"\nLIVE headlines FA-IR: {out['total_results']} — {out['items'][0]['title'][:60]}")

    def test_search_live(self):
        out = json.loads(srv.dw_search_news("Germany", "en", limit=3))
        self.assertNotIn("error", out)
        print(f"\nLIVE search 'Germany': {out['total_results']} hits")

    def test_latest_articles_live(self):
        out = json.loads(srv.dw_latest_articles("de", limit=3))
        self.assertNotIn("error", out)
        self.assertGreaterEqual(out["total_results"], 1)
        print(f"\nLIVE latest DE: {out['total_results']} — {out['items'][0]['url'][:70]}")

    def test_get_article_live(self):
        out = json.loads(srv.dw_get_article(
            "https://www.dw.com/en/iran-denies-french-fridge-cyberattack-hacking/a-79910206"))
        self.assertNotIn("error", out)
        self.assertTrue(out["headline"])
        self.assertGreater(len(out["body"]), 500)
        print(f"\nLIVE article: {out['headline'][:70]} — body {len(out['body'])} chars")

    def test_topics_live(self):
        out = json.loads(srv.dw_topics("bundesliga", "en", limit=3))
        self.assertNotIn("error", out)
        self.assertGreaterEqual(out["total_results"], 1)
        print(f"\nLIVE topics 'bundesliga': {out['total_results']} — {out['items'][0]['name']}")

    def test_health_live(self):
        out = json.loads(srv.dw_health())
        self.assertEqual(out["status"], "ok")
        self.assertEqual(out["http_status"], 200)
