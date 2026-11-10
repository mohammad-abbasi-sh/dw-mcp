"""Offline tests — parse real captured DW sitemaps + a structural article
fixture, no network."""
import json
import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from dw_mcp import domain as dom
from dw_mcp import server as srv

FIX = pathlib.Path(__file__).resolve().parent / "fixtures"


def _read(name):
    return (FIX / name).read_text(encoding="utf-8")


class TestLanguages(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(dom.validate_language("en"), "en")
        self.assertEqual(dom.validate_language("FA-IR"), "fa-ir")
        self.assertEqual(dom.validate_language("  de "), "de")

    def test_invalid(self):
        for bad in ["", "fa", "xx", "eng", "fa_ir"]:
            with self.assertRaises(ValueError, msg=bad):
                dom.validate_language(bad)

    def test_limit(self):
        self.assertEqual(dom.validate_limit(10), 10)
        with self.assertRaises(ValueError):
            dom.validate_limit(0)
        with self.assertRaises(ValueError):
            dom.validate_limit(51)


class TestFixtures(unittest.TestCase):
    def test_news_en(self):
        items = dom.parse_news_sitemap(_read("news-en.xml"))
        self.assertEqual(len(items), 56)
        self.assertTrue(all(i["title"] and i["url"] and i["published"] for i in items))
        self.assertIn("dw.com/en/", items[0]["url"])

    def test_news_de(self):
        items = dom.parse_news_sitemap(_read("news-de.xml"))
        self.assertEqual(len(items), 30)
        self.assertTrue(all(i["title"] for i in items))

    def test_news_fa_ir(self):
        items = dom.parse_news_sitemap(_read("news-fa-ir.xml"))
        self.assertEqual(len(items), 15)
        self.assertTrue(all(i["title"] for i in items))

    def test_articles_en_sorted(self):
        items = dom.parse_article_sitemap(_read("articles-en.xml"))
        self.assertEqual(len(items), 30)
        mods = [i["lastmod"] for i in items]
        self.assertEqual(mods, sorted(mods, reverse=True))
        self.assertTrue(all(i["url"].startswith("https://www.dw.com/en/") for i in items))

    def test_topics_en(self):
        items = dom.parse_topic_sitemap(_read("topics-en.xml"))
        self.assertEqual(len(items), 30)
        names = [i["name"] for i in items]
        self.assertIn("Bundesliga", names)
        self.assertTrue(all(i["url"] and "/t-" in i["url"] for i in items))

    def test_article_fixture(self):
        out = dom.parse_article(_read("article-en.html"))
        self.assertEqual(out["headline"], "Test headline about Germany")
        self.assertEqual(out["published"], "2026-11-10T12:00:00.000Z")
        self.assertTrue(out["body"].startswith(
            "The first paragraph of the article body starts here"))
        self.assertNotIn("Skip to main menu", out["body"])
        self.assertNotIn("p.dw.com", out["body"])
        self.assertNotIn("Prefer DW on Google", out["body"])
        self.assertIn("second paragraph", out["body"])

    def test_bad_xml(self):
        with self.assertRaises(ValueError):
            dom.parse_news_sitemap("<urlset><unclosed")


class TestServerOffline(unittest.TestCase):
    def test_headlines_mock(self):
        with mock.patch("dw_mcp.http.fetch_text",
                        return_value=_read("news-en.xml")):
            out = json.loads(srv.dw_headlines("en", limit=3))
        self.assertEqual(out["language"], "en")
        self.assertEqual(out["total_results"], 56)
        self.assertEqual(out["count"], 3)
        self.assertIn("fetched_at", out)
        self.assertEqual(out["source"], "dw.com")

    def test_search_mock(self):
        with mock.patch("dw_mcp.http.fetch_text",
                        return_value=_read("news-en.xml")):
            out = json.loads(srv.dw_search_news("Iran", "en", limit=5))
        self.assertGreaterEqual(out["total_results"], 1)
        self.assertTrue(all("iran" in i["title"].casefold() for i in out["items"]))

    def test_bad_language(self):
        out = json.loads(srv.dw_headlines("fa", limit=3))
        self.assertIn("error", out)

    def test_get_article_mock(self):
        with mock.patch("dw_mcp.http.fetch_text",
                        return_value=_read("article-en.html")):
            out = json.loads(srv.dw_get_article(
                "https://www.dw.com/en/test-article/a-12345678"))
        self.assertEqual(out["headline"], "Test headline about Germany")
        self.assertIn("second paragraph", out["body"])

    def test_get_article_bad_url(self):
        out = json.loads(srv.dw_get_article("https://example.com/x"))
        self.assertIn("error", out)


if __name__ == "__main__":
    unittest.main()
