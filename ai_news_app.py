import streamlit as st
import json
import requests
from datetime import datetime
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
GITHUB_USER = "snehaaiyer"
GITHUB_REPO = "ai-news-dashboard"
GITHUB_BRANCH = "main"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/ai_news_daily.json"
LOCAL_FALLBACK = Path(__file__).parent / "ai_news_daily.json"

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Daily AI Wrap-Up",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Open Graph meta tags (thumbnail when sharing the link) ────────────────────
THUMBNAIL_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/thumbnail.png"
st.markdown(f"""
<head>
  <meta property="og:title" content="Daily AI Wrap-Up 🤖" />
  <meta property="og:description" content="Auto-curated AI news delivered every morning. Powered by Claude." />
  <meta property="og:image" content="{THUMBNAIL_URL}" />
  <meta property="og:type" content="website" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:image" content="{THUMBNAIL_URL}" />
</head>
""", unsafe_allow_html=True)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem 3rem; max-width: 1100px; }

.hero {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 2rem 2.4rem;
    background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
    border: 1px solid #21262d;
    border-radius: 16px;
    margin-bottom: 2rem;
}
.hero-left h1 {
    font-size: 2rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 0.3rem 0;
    letter-spacing: -0.02em;
}
.hero-left p { font-size: 0.9rem; color: #8b949e; margin: 0; }
.hero-date { text-align: right; color: #8b949e; font-size: 0.85rem; }
.hero-date span {
    display: block;
    font-size: 1.5rem;
    font-weight: 700;
    color: #58a6ff;
    letter-spacing: -0.01em;
}

.intro-banner {
    background: #1c2128;
    border: 1px solid #30363d;
    border-left: 4px solid #58a6ff;
    border-radius: 10px;
    padding: 1rem 1.4rem;
    font-size: 1rem;
    color: #c9d1d9;
    margin-bottom: 2rem;
    line-height: 1.6;
}

.section-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #8b949e;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #21262d;
}

.story-card {
    background: #0d1117;
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 0.9rem;
    transition: border-color 0.2s;
    position: relative;
}
.story-card:hover { border-color: #388bfd; }
.story-number {
    position: absolute;
    top: 1.3rem; left: 1.5rem;
    font-size: 0.7rem;
    font-weight: 700;
    color: #ffffff;
    width: 1.4rem; height: 1.4rem;
    background: #1f6feb;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}
.story-content { padding-left: 2.2rem; }
.story-headline {
    font-size: 1rem;
    font-weight: 700;
    color: #e6edf3;
    margin-bottom: 0.4rem;
    line-height: 1.4;
}
.story-summary {
    font-size: 0.88rem;
    color: #8b949e;
    line-height: 1.65;
    margin-bottom: 0.6rem;
}
.story-link a {
    font-size: 0.8rem;
    color: #58a6ff;
    text-decoration: none;
    font-weight: 500;
}
.story-link a:hover { text-decoration: underline; }

.qh-card {
    background: #0d1117;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 0.85rem 1.2rem;
    margin-bottom: 0.6rem;
    display: flex;
    align-items: flex-start;
    gap: 0.8rem;
    transition: border-color 0.2s;
}
.qh-card:hover { border-color: #3fb950; }
.qh-dot {
    width: 7px; height: 7px;
    background: #3fb950;
    border-radius: 50%;
    margin-top: 0.38rem;
    flex-shrink: 0;
}
.qh-text { font-size: 0.88rem; color: #c9d1d9; line-height: 1.55; flex: 1; }
.qh-link a {
    font-size: 0.78rem;
    color: #58a6ff;
    text-decoration: none;
    white-space: nowrap;
}
.qh-link a:hover { text-decoration: underline; }

.insight-box {
    background: linear-gradient(135deg, #1a1f2e 0%, #0d1117 100%);
    border: 1px solid #30363d;
    border-top: 3px solid #d2a8ff;
    border-radius: 12px;
    padding: 1.2rem 1.6rem;
    color: #c9d1d9;
    font-size: 0.95rem;
    line-height: 1.7;
    font-style: italic;
}

.empty-state { text-align: center; padding: 5rem 2rem; color: #8b949e; }
.empty-state .icon { font-size: 3.5rem; margin-bottom: 1rem; }
.empty-state h2 { color: #e6edf3; font-weight: 700; margin-bottom: 0.5rem; }
.empty-state p { font-size: 0.95rem; line-height: 1.6; }

.footer {
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid #21262d;
    text-align: center;
    color: #484f58;
    font-size: 0.78rem;
}
</style>
""", unsafe_allow_html=True)

# ── Load news ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_news():
    # Try GitHub first (for deployed / web version)
    try:
        resp = requests.get(GITHUB_RAW_URL, timeout=8)
        if resp.status_code == 200:
            return resp.json(), "github"
    except Exception:
        pass
    # Fall back to local file (for local dev)
    if LOCAL_FALLBACK.exists():
        with open(LOCAL_FALLBACK) as f:
            return json.load(f), "local"
    return None, None

def format_generated_at(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("Updated %-I:%M %p · %b %-d, %Y")
    except Exception:
        return iso_str

def today_display():
    now = datetime.now()
    return now.strftime("%b %-d"), now.strftime("%A")

# Auto-refresh every 5 min
st.markdown('<meta http-equiv="refresh" content="300">', unsafe_allow_html=True)

data, source = load_news()
day_short, weekday = today_display()
updated_str = format_generated_at(data["generated_at"]) if data else "Awaiting first run…"

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <div class="hero-left">
    <h1>🤖 Daily AI Wrap-Up</h1>
    <p>{updated_str}</p>
  </div>
  <div class="hero-date">
    {weekday}
    <span>{day_short}</span>
  </div>
</div>
""", unsafe_allow_html=True)

_, btn_col = st.columns([9, 1])
with btn_col:
    if st.button("↺ Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ── Empty state ───────────────────────────────────────────────────────────────
if not data:
    st.markdown("""
    <div class="empty-state">
      <div class="icon">📭</div>
      <h2>No news yet</h2>
      <p>The scheduled task runs every day at <strong>8:00 AM</strong>.<br>
      Trigger it manually from the <strong>Scheduled</strong> section in Claude.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Intro ─────────────────────────────────────────────────────────────────────
intro = data.get("intro", "")
if intro:
    st.markdown(f'<div class="intro-banner">{intro}</div>', unsafe_allow_html=True)

# ── Top Stories ───────────────────────────────────────────────────────────────
stories = data.get("top_stories", [])
if stories:
    st.markdown('<div class="section-label">📰 &nbsp;Top Stories</div>', unsafe_allow_html=True)
    for i, story in enumerate(stories, 1):
        headline = story.get("headline", "")
        summary  = story.get("summary", "")
        url      = story.get("url", "")
        link_html = f'<div class="story-link"><a href="{url}" target="_blank">Read more ↗</a></div>' if url else ""
        st.markdown(f"""
        <div class="story-card">
          <div class="story-number">{i}</div>
          <div class="story-content">
            <div class="story-headline">{headline}</div>
            <div class="story-summary">{summary}</div>
            {link_html}
          </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Quick Hits ────────────────────────────────────────────────────────────────
quick_hits = data.get("quick_hits", [])
if quick_hits:
    st.markdown('<div class="section-label">⚡ &nbsp;Quick Hits</div>', unsafe_allow_html=True)
    for hit in quick_hits:
        if isinstance(hit, dict):
            text      = hit.get("text", "")
            url       = hit.get("url", "")
            link_html = f'<div class="qh-link"><a href="{url}" target="_blank">↗</a></div>' if url else ""
        else:
            text      = hit
            link_html = ""
        st.markdown(f"""
        <div class="qh-card">
          <div class="qh-dot"></div>
          <div class="qh-text">{text}</div>
          {link_html}
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── India AI Roundup ──────────────────────────────────────────────────────────
india_stories = data.get("india_roundup", [])
if india_stories:
    st.markdown('<div class="section-label">🇮🇳 &nbsp;India AI Roundup</div>', unsafe_allow_html=True)
    for story in india_stories:
        if isinstance(story, dict):
            text      = story.get("text", "")
            url       = story.get("url", "")
            link_html = f'<div class="qh-link"><a href="{url}" target="_blank">↗</a></div>' if url else ""
        else:
            text      = story
            link_html = ""
        st.markdown(f"""
        <div class="qh-card" style="border-left: 3px solid #f97316;">
          <div class="qh-dot" style="background:#f97316;"></div>
          <div class="qh-text">{text}</div>
          {link_html}
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Closing Insight ───────────────────────────────────────────────────────────
insight = data.get("closing_insight", "")
if insight:
    st.markdown('<div class="section-label">💡 &nbsp;Today\'s Insight</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="insight-box">"{insight}"</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">Generated daily by Claude &nbsp;·&nbsp; Powered by Streamlit</div>',
    unsafe_allow_html=True,
)
