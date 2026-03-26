#!/usr/bin/env python3
"""
Fetch top Hacker News stories via the official API.
No API keys required.

Usage:
    python3 fetch_hn.py [--type top|best|new] [--limit 30] [--min-score 50] [--output json|text]
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError
from concurrent.futures import ThreadPoolExecutor, as_completed

HN_API = "https://hacker-news.firebaseio.com/v0"
USER_AGENT = "NewsDigestSkill/1.0 (OpenClaw; HN reader)"


def fetch_json(url):
    """Fetch JSON from a URL."""
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def fetch_item(item_id):
    """Fetch a single HN item."""
    try:
        return fetch_json(f"{HN_API}/item/{item_id}.json")
    except Exception:
        return None


def fetch_stories(story_type="top", limit=30, min_score=50):
    """Fetch top/best/new stories from HN API."""
    endpoint = {
        "top": "topstories",
        "best": "beststories",
        "new": "newstories",
    }.get(story_type, "topstories")

    try:
        story_ids = fetch_json(f"{HN_API}/{endpoint}.json")
    except URLError as e:
        print(f"[ERROR] Failed to fetch HN {endpoint}: {e}", file=sys.stderr)
        return []

    # Fetch more than needed to filter by score
    fetch_count = min(limit * 3, len(story_ids))
    story_ids = story_ids[:fetch_count]

    stories = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_item, sid): sid for sid in story_ids}
        for future in as_completed(futures):
            item = future.result()
            if item and item.get("type") == "story" and not item.get("dead") and not item.get("deleted"):
                stories.append(item)

    # Filter by score and sort
    stories = [s for s in stories if s.get("score", 0) >= min_score]
    stories.sort(key=lambda s: s.get("score", 0), reverse=True)

    return stories[:limit]


def format_text(stories):
    """Format stories as readable text."""
    lines = [f"# Hacker News Digest — {datetime.now(timezone.utc).strftime('%B %d, %Y')}", ""]
    lines.append(f"**{len(stories)} top stories**\n")

    for i, s in enumerate(stories, 1):
        score = s.get("score", 0)
        comments = s.get("descendants", 0)
        title = s.get("title", "")
        url = s.get("url", "")
        hn_url = f"https://news.ycombinator.com/item?id={s['id']}"
        time_posted = ""
        if s.get("time"):
            dt = datetime.fromtimestamp(s["time"], tz=timezone.utc)
            time_posted = dt.strftime(" — %b %d, %I:%M %p UTC")

        lines.append(f"## {i}. {title}")
        lines.append(f"⬆️ {score} points | 💬 {comments} comments{time_posted}")
        if url:
            lines.append(url)
        lines.append(f"Discussion: {hn_url}")
        lines.append("")

    return "\n".join(lines)


def format_json(stories):
    """Format stories as JSON."""
    output = []
    for s in stories:
        output.append({
            "title": s.get("title", ""),
            "url": s.get("url", ""),
            "hn_url": f"https://news.ycombinator.com/item?id={s['id']}",
            "score": s.get("score", 0),
            "comments": s.get("descendants", 0),
            "by": s.get("by", ""),
            "time": datetime.fromtimestamp(s["time"], tz=timezone.utc).isoformat() if s.get("time") else None,
        })
    return json.dumps({"stories": output, "fetched_at": datetime.now(timezone.utc).isoformat()}, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Fetch Hacker News top stories")
    parser.add_argument("--type", choices=["top", "best", "new"], default="top")
    parser.add_argument("--limit", type=int, default=30, help="Max stories to return")
    parser.add_argument("--min-score", type=int, default=50, help="Minimum score threshold")
    parser.add_argument("--output", choices=["json", "text"], default="text")
    args = parser.parse_args()

    stories = fetch_stories(args.type, args.limit, args.min_score)

    if args.output == "json":
        print(format_json(stories))
    else:
        print(format_text(stories))


if __name__ == "__main__":
    main()
