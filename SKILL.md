---
name: news-digest
description: Generate daily news digests from unbiased RSS sources (AP, Reuters, BBC, NPR, PBS, CSMonitor). No API keys required. Use when asked for news, daily digest, news briefing, morning briefing, what's happening in the world, current events, headlines, or news summary. Also use for setting up scheduled/cron news digests. Covers world and US national news from wire services and public broadcasters only.
---

# News Digest

Generate factual, unsensationalized daily news digests from curated RSS feeds. Zero API keys — uses only public RSS endpoints from wire services and public broadcasters.

## Quick Start

Fetch and display today's news:

```bash
python3 scripts/fetch_feeds.py --category all --hours 24 --output text
```

Then synthesize into a digest following the guidelines below.

## Workflow

### 1. Fetch Articles

Run `scripts/fetch_feeds.py` with appropriate flags:

```bash
# All news from last 24 hours
python3 scripts/fetch_feeds.py --category all --hours 24 --output text

# World news only
python3 scripts/fetch_feeds.py --category world --hours 24 --output text

# National (US) news only
python3 scripts/fetch_feeds.py --category national --hours 24 --output text

# JSON output for programmatic use
python3 scripts/fetch_feeds.py --category all --hours 24 --output json
```

### 2. Synthesize the Digest

After fetching, synthesize articles into a clean digest:

1. Read `references/digest-guidelines.md` for tone and format rules
2. **Group by topic** — cluster related stories across sources
3. **Cross-reference** — prefer stories reported by 2+ sources
4. **Neutralize language** — strip sensationalist framing from headlines
5. **Attribute** — cite which sources reported each story
6. **Prioritize** — wire services (AP, Reuters) > public broadcasters > others

### 3. Format

Use this structure:

```
📰 Daily News Digest — [Date]

🌍 WORLD NEWS
• [Headline] — [1-2 sentence neutral summary] (AP, BBC)
• ...

🇺🇸 NATIONAL NEWS
• [Headline] — [1-2 sentence neutral summary] (Reuters, NPR)
• ...
```

Cap at 10-15 stories total. Quality over quantity.

## Cron Setup (Daily Digest)

To schedule a daily digest, create an OpenClaw cron job:

- **Schedule:** `0 7 * * *` (7 AM daily, adjust timezone)
- **Task:** Fetch feeds, synthesize digest, deliver to channel
- **Session:** Use isolated agentTurn so each run is clean

Example cron payload:
```
Fetch today's news using the news-digest skill. Run fetch_feeds.py for all categories, then write a clean digest following digest-guidelines.md. Deliver the digest.
```

## Source Customization

To review or modify news sources, see `references/sources.md` for the full source list with bias ratings and selection methodology.

To add/remove feeds, edit the `FEEDS` dict in `scripts/fetch_feeds.py`. Each feed needs: `name`, `url`, `bias` (center/center-left/center-right), and `type`.

## Hacker News Digest

Fetch top stories from Hacker News via its public API (no keys needed).

```bash
# Top stories with 100+ points
python3 scripts/fetch_hn.py --type top --limit 15 --min-score 100 --output text

# Best stories (curated by HN)
python3 scripts/fetch_hn.py --type best --limit 15 --min-score 100 --output text
```

### HN Digest Format

```
🟠 Hacker News Digest — [Date]

• [Title] — ⬆️ [score] | 💬 [comments]
  [1-sentence summary of why it's interesting if context is available]
```

Group by theme when possible (e.g., AI/ML, infrastructure, security, open source).
Prioritize by score. Skip job postings and Show HN launches unless exceptionally popular.

## Key Rules

- **No API keys** — everything uses public RSS feeds
- **No opinion pieces** — skip editorials even from included sources
- **Neutral language only** — see digest-guidelines.md for word replacements
- **Attribution required** — always cite which source(s) reported a story
- **Multi-source preference** — stories confirmed by 2+ sources get priority
