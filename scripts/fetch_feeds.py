#!/usr/bin/env python3
"""
Fetch and parse RSS feeds from unbiased news sources.
No API keys required — uses only public RSS feeds.

Usage:
    python3 fetch_feeds.py [--category world|national|all] [--hours 24] [--max-per-feed 10] [--output json|text]
"""

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from html import unescape
from urllib.request import Request, urlopen
from urllib.error import URLError
import re

# --- Feed Registry ---
# Selected for editorial independence, factual reporting, and minimal sensationalism.
# Sources chosen based on AllSides, Ad Fontes Media, and Media Bias/Fact Check ratings.

FEEDS = {
    "world": [
        {
            "name": "AP News - World",
            "url": "https://rsshub.app/apnews/topics/world-news",
            "fallback_url": "https://rss.app/feeds/v1.1/ts4gfDjrfNaCSvnA.xml",
            "bias": "center",
            "type": "wire_service"
        },
        {
            "name": "Reuters - World",
            "url": "https://rsshub.app/reuters/world",
            "fallback_url": "https://rss.app/feeds/v1.1/tVkCHHcZqxtGeAQH.xml",
            "bias": "center",
            "type": "wire_service"
        },
        {
            "name": "BBC News - World",
            "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
            "bias": "center-left",
            "type": "public_broadcaster"
        },
        {
            "name": "NPR - World",
            "url": "https://feeds.npr.org/1004/rss.xml",
            "bias": "center-left",
            "type": "public_broadcaster"
        },
        {
            "name": "Al Jazeera",
            "url": "https://www.aljazeera.com/xml/rss/all.xml",
            "bias": "center",
            "type": "international"
        },
        {
            "name": "PBS NewsHour - World",
            "url": "https://www.pbs.org/newshour/feeds/rss/world",
            "bias": "center",
            "type": "public_broadcaster"
        },
        {
            "name": "Christian Science Monitor",
            "url": "https://rss.csmonitor.com/feeds/world",
            "bias": "center",
            "type": "independent"
        },
    ],
    "national": [
        {
            "name": "AP News - US",
            "url": "https://rsshub.app/apnews/topics/us-news",
            "fallback_url": "https://rss.app/feeds/v1.1/ts4gfDjrfNaCSvnA.xml",
            "bias": "center",
            "type": "wire_service"
        },
        {
            "name": "Reuters - US",
            "url": "https://rsshub.app/reuters/us",
            "fallback_url": "https://rss.app/feeds/v1.1/tVkCHHcZqxtGeAQH.xml",
            "bias": "center",
            "type": "wire_service"
        },
        {
            "name": "BBC News - US & Canada",
            "url": "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml",
            "bias": "center-left",
            "type": "public_broadcaster"
        },
        {
            "name": "NPR - National",
            "url": "https://feeds.npr.org/1003/rss.xml",
            "bias": "center-left",
            "type": "public_broadcaster"
        },
        {
            "name": "PBS NewsHour - Nation",
            "url": "https://www.pbs.org/newshour/feeds/rss/nation",
            "bias": "center",
            "type": "public_broadcaster"
        },
        {
            "name": "Christian Science Monitor - USA",
            "url": "https://rss.csmonitor.com/feeds/usa",
            "bias": "center",
            "type": "independent"
        },
        {
            "name": "The Hill",
            "url": "https://thehill.com/feed/",
            "bias": "center",
            "type": "political"
        },
    ],
}

USER_AGENT = "NewsDigestSkill/1.0 (OpenClaw; RSS reader)"


def strip_html(text):
    """Remove HTML tags and decode entities."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_date(date_str):
    """Parse RSS date formats into datetime. Returns None on failure."""
    if not date_str:
        return None
    # Common RSS date formats
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",      # RFC 822
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",            # ISO 8601
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%a, %d %b %Y %H:%M %z",
    ]
    # Strip trailing timezone abbreviation in parens like "(EDT)"
    date_str = re.sub(r"\s*\([A-Z]+\)\s*$", "", date_str.strip())
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


def fetch_feed(feed_info, max_age_hours=24, max_items=10):
    """Fetch and parse a single RSS feed. Returns list of article dicts."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    articles = []

    urls_to_try = [feed_info["url"]]
    if "fallback_url" in feed_info:
        urls_to_try.append(feed_info["fallback_url"])

    for url in urls_to_try:
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(req, timeout=15) as resp:
                raw = resp.read()
            root = ET.fromstring(raw)

            # Handle both RSS 2.0 and Atom feeds
            ns = {"atom": "http://www.w3.org/2005/Atom"}

            items = root.findall(".//item")  # RSS 2.0
            if not items:
                items = root.findall(".//atom:entry", ns)  # Atom

            for item in items[:max_items * 2]:  # fetch extra, filter by date
                # RSS 2.0
                title = item.findtext("title") or item.findtext("atom:title", namespaces=ns) or ""
                link = item.findtext("link") or ""
                if not link:
                    link_el = item.find("atom:link", ns)
                    if link_el is not None:
                        link = link_el.get("href", "")
                desc = item.findtext("description") or item.findtext("atom:summary", namespaces=ns) or ""
                pub_date_str = (
                    item.findtext("pubDate")
                    or item.findtext("atom:published", namespaces=ns)
                    or item.findtext("atom:updated", namespaces=ns)
                    or ""
                )

                pub_date = parse_date(pub_date_str)

                # Filter by age
                if pub_date and pub_date < cutoff:
                    continue

                articles.append({
                    "title": strip_html(title),
                    "link": link.strip(),
                    "summary": strip_html(desc)[:500],
                    "published": pub_date.isoformat() if pub_date else None,
                    "source": feed_info["name"],
                    "bias": feed_info["bias"],
                    "type": feed_info["type"],
                })

                if len(articles) >= max_items:
                    break

            if articles:
                break  # success, don't try fallback

        except (URLError, ET.ParseError, Exception) as e:
            print(f"[WARN] Failed to fetch {feed_info['name']} from {url}: {e}", file=sys.stderr)
            continue

    return articles


def fetch_all(category="all", max_age_hours=24, max_per_feed=10):
    """Fetch articles from all feeds in the given category."""
    if category == "all":
        feed_list = FEEDS["world"] + FEEDS["national"]
    else:
        feed_list = FEEDS.get(category, [])

    all_articles = []
    errors = []

    for feed_info in feed_list:
        try:
            articles = fetch_feed(feed_info, max_age_hours, max_per_feed)
            all_articles.extend(articles)
        except Exception as e:
            errors.append({"source": feed_info["name"], "error": str(e)})

    # Deduplicate by title similarity (exact match after lowering)
    seen_titles = set()
    unique = []
    for a in all_articles:
        key = a["title"].lower().strip()
        if key not in seen_titles and key:
            seen_titles.add(key)
            unique.append(a)

    # Sort by published date (newest first), unknowns at end
    unique.sort(key=lambda x: x["published"] or "0000", reverse=True)

    return {"articles": unique, "errors": errors, "fetched_at": datetime.now(timezone.utc).isoformat()}


def format_text(data):
    """Format articles as readable text for the agent."""
    lines = [f"# News Digest — {datetime.now(timezone.utc).strftime('%B %d, %Y')}", ""]
    lines.append(f"**{len(data['articles'])} articles** from {len(set(a['source'] for a in data['articles']))} sources\n")

    if data["errors"]:
        lines.append(f"⚠️ {len(data['errors'])} feed(s) failed: {', '.join(e['source'] for e in data['errors'])}\n")

    for i, a in enumerate(data["articles"], 1):
        pub = ""
        if a["published"]:
            try:
                dt = datetime.fromisoformat(a["published"])
                pub = dt.strftime(" — %b %d, %I:%M %p UTC")
            except Exception:
                pass
        lines.append(f"## {i}. {a['title']}")
        lines.append(f"**{a['source']}** ({a['bias']}){pub}")
        if a["summary"]:
            lines.append(a["summary"])
        if a["link"]:
            lines.append(a["link"])
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Fetch news from unbiased RSS feeds")
    parser.add_argument("--category", choices=["world", "national", "all"], default="all")
    parser.add_argument("--hours", type=int, default=24, help="Max article age in hours")
    parser.add_argument("--max-per-feed", type=int, default=10, help="Max articles per feed")
    parser.add_argument("--output", choices=["json", "text"], default="text")
    args = parser.parse_args()

    data = fetch_all(args.category, args.hours, args.max_per_feed)

    if args.output == "json":
        print(json.dumps(data, indent=2))
    else:
        print(format_text(data))


if __name__ == "__main__":
    main()
