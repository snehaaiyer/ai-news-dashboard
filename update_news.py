#!/usr/bin/env python3
"""
Daily AI news updater.

Calls Claude with web search to fetch today's top AI stories and writes the
result to ai_news_daily.json in the format expected by the Streamlit dashboard.

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
OUTPUT_FILE = Path(__file__).parent / "ai_news_daily.json"

SCHEMA_EXAMPLE = """
{
  "generated_at": "<YYYY-MM-DDTHH:MM:SS — today at 08:00:00>",
  "intro": "2–3 sentence opening hook summarising the day's biggest AI themes",
  "top_stories": [
    {"headline": "Story headline", "summary": "2–3 sentence summary.", "url": "https://real-source.com/article", "tag": "<one of: Models, Research, Funding, Policy, Industry>"},
    ... (exactly 5 items)
  ],
  "quick_hits": [
    {"text": "1–2 sentence item.", "url": "https://real-source.com/article"},
    ... (exactly 5 items)
  ],
  "india_roundup": [
    {"text": "1–2 sentence item about AI in India.", "url": "https://real-source.com/article"},
    ... (exactly 5 items)
  ],
  "closing_insight": "One sharp, memorable sentence to close the day."
}
"""


def build_prompt() -> str:
    today = datetime.now(IST).strftime("%B %-d, %Y")
    generated_at = datetime.now(IST).replace(hour=8, minute=0, second=0, microsecond=0).strftime(
        "%Y-%m-%dT%H:%M:%S"
    )
    return f"""Today is {today}. You are an AI news curator for the "Daily AI Wrap-Up" dashboard.

Search the web for the most important AI news published in the last 24–48 hours, then return a single JSON object that exactly matches this schema:

{SCHEMA_EXAMPLE}

Rules:
- top_stories: 5 significant global AI stories. Each must have a real URL and a "tag" chosen from: Models, Research, Funding, Policy, Industry.
- quick_hits: 5 shorter items (product updates, metrics, partnerships). Each must have a real URL.
- india_roundup: 5 items specifically about AI developments in India. Each must have a real URL.
- generated_at must be exactly: "{generated_at}"
- All URLs must be real, working links you actually found via web search — no invented links.
- Return ONLY the raw JSON object — no markdown fences, no preamble, no commentary after the closing brace."""


def extract_json(text: str) -> str:
    """Strip accidental markdown fences and return clean JSON text."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]  # drop opening fence line
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]  # drop closing fence line
        text = "\n".join(lines).strip()
    # Find first { in case there is preamble text
    start = text.find("{")
    if start > 0:
        text = text[start:]
    return text


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    today_str = datetime.now(IST).strftime("%B %-d, %Y")
    print(f"Fetching AI news for {today_str} ...")

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        tools=[
            {"type": "web_search_20260209", "name": "web_search"},
        ],
        messages=[{"role": "user", "content": build_prompt()}],
    ) as stream:
        response = stream.get_final_message()

    # Extract text blocks from the response
    text_parts = [block.text for block in response.content if block.type == "text"]
    raw_text = "\n".join(text_parts).strip()

    if not raw_text:
        print(f"ERROR: No text content in Claude's response (stop_reason={response.stop_reason}).",
              file=sys.stderr)
        sys.exit(1)

    clean_json = extract_json(raw_text)

    try:
        data = json.loads(clean_json)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Failed to parse JSON from response: {exc}", file=sys.stderr)
        print("--- raw response (first 1000 chars) ---", file=sys.stderr)
        print(raw_text[:1000], file=sys.stderr)
        sys.exit(1)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)

    # Save a dated copy to the archive folder
    archive_dir = Path(__file__).parent / "archive"
    archive_dir.mkdir(exist_ok=True)
    archive_date = datetime.now(IST).strftime("%Y-%m-%d")
    archive_file = archive_dir / f"{archive_date}.json"
    with open(archive_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Written: {OUTPUT_FILE}")
    print(f"Archive: {archive_file}")
    print(f"  generated_at : {data.get('generated_at', '???')}")
    print(f"  top_stories  : {len(data.get('top_stories', []))}")
    print(f"  quick_hits   : {len(data.get('quick_hits', []))}")
    print(f"  india_roundup: {len(data.get('india_roundup', []))}")


if __name__ == "__main__":
    main()
