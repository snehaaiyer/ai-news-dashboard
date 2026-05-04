#!/usr/bin/env python3
"""
Daily AI news updater.

Generates two editions each morning:
  - ai_news_daily.json    — general AI news dashboard
  - ai_news_operator.json — monetization/revenue-focused operator edition

Usage:
    ANTHROPIC_API_KEY=sk-... python update_news.py

Requires: anthropic
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import anthropic

# ── Constants ─────────────────────────────────────────────────────────────────
IST = timezone(timedelta(hours=5, minutes=30))
BASE_DIR      = Path(__file__).parent
OUTPUT_FILE   = BASE_DIR / "ai_news_daily.json"
OPERATOR_FILE = BASE_DIR / "ai_news_operator.json"

# ── General edition schema ────────────────────────────────────────────────────
GENERAL_SCHEMA = """
{
  "generated_at": "<YYYY-MM-DDTHH:MM:SS — today at 08:00:00>",
  "intro": "2–3 sentence opening hook summarising the day's biggest AI themes",
  "top_stories": [
    {"headline": "...", "summary": "2–3 sentence summary.", "url": "https://...", "tag": "<Models|Research|Funding|Policy|Industry>"},
    ... (exactly 5 items)
  ],
  "quick_hits": [
    {"text": "1–2 sentence item.", "url": "https://..."},
    ... (exactly 5 items)
  ],
  "tools_products": [
    {"name": "Tool or product name", "maker": "Company", "what": "One sentence on what it does or what's new today.", "url": "https://..."},
    ... (exactly 5 items)
  ],
  "india_roundup": [
    {"text": "1–2 sentence item about AI in India.", "url": "https://..."},
    ... (exactly 5 items)
  ],
  "closing_insight": "One sharp, memorable sentence to close the day."
}
"""

# ── Operator edition schema ───────────────────────────────────────────────────
OPERATOR_SCHEMA = """
{
  "generated_at": "<YYYY-MM-DDTHH:MM:SS — today at 08:00:00>",
  "big_story": {
    "headline": "The single AI development with the biggest monetization/distribution impact today",
    "what_happened": "2–3 sentences: what happened, factually",
    "why_it_matters": "2–3 sentences: the non-obvious business implication",
    "revenue_impact": "2–3 sentences: how this changes revenue, ads, or business models"
  },
  "key_headlines": {
    "ads_monetization": [
      {"summary": "One-line summary", "implication": "One-line business implication"},
      {"summary": "...", "implication": "..."}
    ],
    "ai_products": [
      {"summary": "...", "implication": "..."},
      {"summary": "...", "implication": "..."}
    ],
    "distribution": [
      {"summary": "...", "implication": "..."},
      {"summary": "...", "implication": "..."}
    ]
  },
  "money_moves": {
    "revenue_shifts": ["Who earns more / less and why — 1 sentence each", "..."],
    "ad_inventory": ["New surfaces, formats, or inventory changes — 1 sentence each", "..."],
    "pricing_power": ["Who gains or loses pricing power — 1 sentence each", "..."],
    "winners": ["Company or category gaining — with one-line reason", "..."],
    "losers": ["Company or category losing — with one-line reason", "..."]
  },
  "operator_insight": {
    "company": "Company name",
    "strategy": "3–4 sentences explaining the strategy deeply",
    "why_effective": "2–3 sentences on why this works and what others can learn"
  },
  "playbook": {
    "marketers": ["Concrete action 1", "Concrete action 2"],
    "pms": ["Concrete action 1", "Concrete action 2"],
    "founders": ["Concrete action 1", "Concrete action 2"]
  },
  "trend": "2–3 sentences connecting today's updates into a broader shift",
  "tldr": {
    "insight": "Key insight in one sentence",
    "opportunity": "The opportunity in one sentence",
    "risk": "The risk in one sentence"
  }
}
"""


def build_general_prompt(today: str, generated_at: str) -> str:
    return f"""Today is {today}. You are an AI news curator for the "Daily AI Wrap-Up" dashboard.

Search the web for the most important AI news published in the last 24–48 hours, then return a single JSON object matching this schema exactly:

{GENERAL_SCHEMA}

Rules:
- top_stories: 5 significant global AI stories. Each needs a real URL and a tag (Models, Research, Funding, Policy, or Industry).
- quick_hits: 5 shorter items with real URLs.
- tools_products: 5 noteworthy AI tools or product launches/updates today. Each needs a name, maker, one-sentence "what", and a real URL.
- india_roundup: 5 India-specific AI items with real URLs.
- generated_at must be exactly: "{generated_at}"
- Return ONLY the raw JSON — no markdown fences, no preamble."""


def build_operator_prompt(today: str, generated_at: str) -> str:
    return f"""Today is {today}. You are an expert in AI, advertising, and monetization writing a high-quality daily newsletter for operators — PMs, marketers, and founders.

Search the web for today's most important AI news, then interpret it through the lens of revenue generation, ad ecosystems, and growth/distribution. Focus especially on Meta, Google, OpenAI, and Microsoft developments.

Return a single JSON object matching this schema exactly:

{OPERATOR_SCHEMA}

Rules:
- big_story: the single development with the biggest monetization/distribution impact today.
- key_headlines: 2 items per cluster (ads_monetization, ai_products, distribution).
- money_moves: 2–3 items per sub-key (revenue_shifts, ad_inventory, pricing_power, winners, losers).
- playbook: 2 concrete, actionable items per audience (marketers, pms, founders).
- generated_at must be exactly: "{generated_at}"
- Be sharp and operator-focused — avoid generic summaries, prioritise insight over information.
- Return ONLY the raw JSON — no markdown fences, no preamble."""


def extract_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    start = text.find("{")
    if start > 0:
        text = text[start:]
    return text


def generate(client: anthropic.Anthropic, prompt: str, label: str) -> dict:
    print(f"  Generating {label} edition...")
    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=16000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        response = stream.get_final_message()

    text_parts = [block.text for block in response.content if block.type == "text"]
    raw_text = "\n".join(text_parts).strip()

    if not raw_text:
        print(f"ERROR: No text in {label} response (stop_reason={response.stop_reason}).",
              file=sys.stderr)
        sys.exit(1)

    try:
        return json.loads(extract_json(raw_text))
    except json.JSONDecodeError as exc:
        print(f"ERROR: Failed to parse {label} JSON: {exc}", file=sys.stderr)
        print(raw_text[:1000], file=sys.stderr)
        sys.exit(1)


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set.", file=sys.stderr)
        sys.exit(1)

    client    = anthropic.Anthropic(
        api_key=api_key,
        default_headers={"anthropic-beta": "web-search-2025-03-05"},
    )
    now_ist   = datetime.now(IST)
    today_str = now_ist.strftime("%B %-d, %Y")
    gen_at    = now_ist.replace(hour=8, minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%S")
    date_str  = now_ist.strftime("%Y-%m-%d")

    print(f"Daily AI news update — {today_str}")

    # Generate both editions
    general_data  = generate(client, build_general_prompt(today_str, gen_at),  "general")
    operator_data = generate(client, build_operator_prompt(today_str, gen_at), "operator")

    # Save main files
    for path, data in [(OUTPUT_FILE, general_data), (OPERATOR_FILE, operator_data)]:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Written: {path}")

    # Save dated archive copies
    archive_dir = BASE_DIR / "archive"
    archive_dir.mkdir(exist_ok=True)
    for suffix, data in [("", general_data), ("-operator", operator_data)]:
        archive_path = archive_dir / f"{date_str}{suffix}.json"
        with open(archive_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Archive: {archive_path}")

    print(f"  top_stories  : {len(general_data.get('top_stories', []))}")
    print(f"  quick_hits   : {len(general_data.get('quick_hits', []))}")
    print(f"  india_roundup: {len(general_data.get('india_roundup', []))}")


if __name__ == "__main__":
    main()
