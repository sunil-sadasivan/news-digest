# 📰 news-digest

An [OpenClaw](https://github.com/openclaw/openclaw) skill that generates daily news digests from unbiased RSS sources. **No API keys required.**

## Sources

Curated for factual, unsensationalized reporting:

- **Wire Services:** AP News, Reuters
- **Public Broadcasters:** BBC, NPR, PBS NewsHour
- **Independent:** Christian Science Monitor, Al Jazeera English
- **Political:** The Hill

Sources selected using [AllSides](https://allsides.com), [Ad Fontes Media](https://adfontesmedia.com), and [Media Bias/Fact Check](https://mediabiasfactcheck.com) ratings. Only center/center-left/center-right rated sources included. See [references/sources.md](references/sources.md) for full methodology.

## Install

```bash
openclaw skill install news-digest
```

Or manually copy the `news-digest/` folder into your OpenClaw skills directory.

## Usage

Ask your agent:
- "Give me today's news digest"
- "What's happening in the world?"
- "Morning briefing"

Or set up a daily cron job for automatic delivery.

By default, digests are delivered as clean summaries without links — easier to scan. Just ask "links" or "get me the links" and your agent will re-send the digest with source URLs included.

## Customization

Edit `scripts/fetch_feeds.py` to add/remove RSS sources. Each feed entry needs:

```python
{
    "name": "Source Name",
    "url": "https://example.com/rss.xml",
    "bias": "center",           # center, center-left, center-right
    "type": "wire_service"      # wire_service, public_broadcaster, independent, political
}
```

## Philosophy

- **Facts over framing** — wire service style, not editorial
- **Multi-source corroboration** — stories confirmed by 2+ sources get priority
- **Neutral language** — no "slams", "bombshell", "devastating"
- **No API keys** — 100% public RSS feeds
- **Open source** — customize for your own bias preferences

## License

MIT
