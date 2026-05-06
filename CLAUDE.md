# AI News Dashboard — Claude Instructions

## Git Workflow

**Always commit and push directly to `main`.** Never create feature branches or push to any other branch. The website reads from `main`; pushing to any other branch silently breaks the live site.

```
git add <files>
git commit -m "..."
git push origin main
```

Do not create `claude/*` branches, do not open pull requests, do not work on feature branches.

## Project Structure

- `ai_news_daily.json` — main general edition (what the site serves)
- `ai_news_operator.json` — main operator edition (what the site serves)
- `archive/YYYY-MM-DD.json` — general edition archive
- `archive/YYYY-MM-DD-operator.json` — operator edition archive
- `update_news.py` — cron script that auto-generates both editions daily at 08:00 IST

## Newsletter Update Rules

When manually updating the newsletter:

1. Update `ai_news_daily.json` and `ai_news_operator.json` with today's date and content
2. Write the corresponding archive files (`archive/YYYY-MM-DD.json` and `archive/YYYY-MM-DD-operator.json`)
3. Backfill any missing archive dates before today
4. Commit everything in one batch and push to `main`

The `intro` field must open with the correct day of the week for the `generated_at` date.

## JSON Schemas

### General edition (`ai_news_daily.json`)
```json
{
  "generated_at": "YYYY-MM-DDT08:00:00",
  "intro": "Dayname: ...",
  "top_stories": [ { "headline", "summary", "url", "tag" } ],  // 5 items
  "quick_hits": [ { "text", "url" } ],                          // 5 items
  "tools_products": [ { "name", "maker", "what", "url" } ],     // 5 items
  "india_roundup": [ { "text", "url" } ],                       // 5 items
  "closing_insight": "..."
}
```

### Operator edition (`ai_news_operator.json`)
```json
{
  "generated_at": "YYYY-MM-DDT08:00:00",
  "big_story": { "headline", "what_happened", "why_it_matters", "revenue_impact" },
  "key_headlines": {
    "ads_monetization": [ { "summary", "implication" } ],
    "ai_products": [ { "summary", "implication" } ],
    "distribution": [ { "summary", "implication" } ]
  },
  "money_moves": {
    "revenue_shifts": [],
    "ad_inventory": [],
    "pricing_power": [],
    "winners": [],
    "losers": []
  },
  "operator_insight": { "company", "strategy", "why_effective" },
  "playbook": { "marketers": [], "pms": [], "founders": [] },
  "trend": "...",
  "tldr": { "insight", "opportunity", "risk" }
}
```
