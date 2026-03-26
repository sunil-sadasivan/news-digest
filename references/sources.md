# News Sources — Bias & Selection Criteria

## Selection Methodology

Sources selected using three independent media bias evaluators:
- **AllSides** (allsides.com) — crowd-sourced + editorial ratings
- **Ad Fontes Media** (adfontesmedia.com) — individual article analysis
- **Media Bias/Fact Check** (mediabiasfactcheck.com) — methodology-based ratings

Only sources rated **center, center-left, or center-right** by at least two of the three evaluators are included. Wire services (AP, Reuters) are prioritized as the most factual, least editorialized sources.

## Source Categories

### Wire Services (Highest Priority)
Wire services report facts with minimal editorializing. They supply stories to other outlets.

| Source | AllSides | MBFC | Notes |
|--------|----------|------|-------|
| AP News | Center | Very High factual | Gold standard wire service |
| Reuters | Center | Very High factual | Gold standard wire service |

### Public Broadcasters
Publicly funded, mandate for balanced reporting.

| Source | AllSides | MBFC | Notes |
|--------|----------|------|-------|
| BBC News | Center-Left | High factual | UK public broadcaster, strong int'l coverage |
| NPR | Center-Left | Very High factual | US public radio |
| PBS NewsHour | Center | Very High factual | US public television |

### Independent / Non-Profit
No corporate parent driving editorial agenda.

| Source | AllSides | MBFC | Notes |
|--------|----------|------|-------|
| Christian Science Monitor | Center | Very High factual | Non-profit, despite name not religious news |
| Al Jazeera English | Center | Mixed-High factual | Strong non-Western perspective |

### Political Coverage
Focused on politics but maintaining factual center.

| Source | AllSides | MBFC | Notes |
|--------|----------|------|-------|
| The Hill | Center | High factual | US political news, balanced op-ed mix |

## Excluded Sources & Why

These popular sources are intentionally **excluded** to avoid bias and sensationalism:

- **CNN, MSNBC** — Center-left to left; tendency toward sensationalist framing
- **Fox News** — Right; opinion/news blending
- **New York Times** — Center-left; strong reporting but editorial lens visible in headlines
- **Washington Post** — Center-left; similar to NYT
- **Wall Street Journal** — Center-right news, right opinion; paywall issues
- **Daily Mail, NY Post** — Tabloid framing, sensationalist headlines
- **Huffington Post, Breitbart, Vox** — Strong editorial bias in either direction
- **Social media aggregators** — Algorithmic bias, unverified sources

## Customization

Users can modify the feed list in `scripts/fetch_feeds.py` by editing the `FEEDS` dict. Add or remove sources based on personal preference. Each entry needs:

```python
{
    "name": "Source Name",
    "url": "https://example.com/rss.xml",
    "bias": "center",        # center, center-left, center-right
    "type": "wire_service"   # wire_service, public_broadcaster, independent, political
}
```

## RSS Feed Reliability Notes

- **AP/Reuters** don't offer direct public RSS anymore; we use RSSHub mirrors with feedx.net fallbacks
- **BBC** has stable, long-running RSS feeds
- **NPR/PBS** maintain official RSS endpoints
- **CSMonitor** has reliable RSS
- **Al Jazeera** RSS can be intermittent
- **The Hill** full-feed RSS available

If a feed goes down, the script logs a warning and continues with remaining sources.
