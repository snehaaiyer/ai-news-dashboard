import streamlit as st
import json
import requests
from datetime import datetime, date
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
GITHUB_USER   = "snehaaiyer"
GITHUB_REPO   = "ai-news-dashboard"
GITHUB_BRANCH = "main"
GITHUB_RAW_URL   = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/ai_news_daily.json"
ARCHIVE_BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/archive"
LOCAL_FALLBACK   = Path(__file__).parent / "ai_news_daily.json"

# Tag display config
TAG_CONFIG = {
    "Models":   {"emoji": "🤖", "bg": "#1f1a2d", "color": "#d2a8ff"},
    "Research": {"emoji": "🧠", "bg": "#0d1f3c", "color": "#79c0ff"},
    "Funding":  {"emoji": "💰", "bg": "#0f2d0f", "color": "#56d364"},
    "Policy":   {"emoji": "🏛️", "bg": "#2d1a0d", "color": "#ffa657"},
    "Industry": {"emoji": "🏭", "bg": "#0d2d2d", "color": "#39d3d3"},
}

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Daily AI Wrap-Up",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Open Graph meta tags ──────────────────────────────────────────────────────
THUMBNAIL_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/preview.png"
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
    margin-bottom: 1.2rem;
}
.hero-left h1 { font-size: 2rem; font-weight: 800; color: #ffffff; margin: 0 0 0.3rem 0; letter-spacing: -0.02em; }
.hero-left p  { font-size: 0.9rem; color: #8b949e; margin: 0; }
.hero-date    { text-align: right; color: #8b949e; font-size: 0.85rem; }
.hero-date span { display: block; font-size: 1.5rem; font-weight: 700; color: #58a6ff; letter-spacing: -0.01em; }

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
.section-label::after { content: ''; flex: 1; height: 1px; background: #21262d; }

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
    font-size: 0.7rem; font-weight: 700; color: #ffffff;
    width: 1.4rem; height: 1.4rem;
    background: #1f6feb;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
}
.story-content  { padding-left: 2.2rem; }
.story-headline { font-size: 1rem; font-weight: 700; color: #e6edf3; margin-bottom: 0.4rem; line-height: 1.4; }
.story-summary  { font-size: 0.88rem; color: #8b949e; line-height: 1.65; margin-bottom: 0.6rem; }
.story-link a   { font-size: 0.8rem; color: #58a6ff; text-decoration: none; font-weight: 500; }
.story-link a:hover { text-decoration: underline; }

.tag-pill {
    display: inline-block;
    padding: 0.13rem 0.55rem;
    border-radius: 999px;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    margin-bottom: 0.45rem;
}

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
.qh-dot  { width: 7px; height: 7px; background: #3fb950; border-radius: 50%; margin-top: 0.38rem; flex-shrink: 0; }
.qh-text { font-size: 0.88rem; color: #c9d1d9; line-height: 1.55; flex: 1; }
.qh-link a { font-size: 0.78rem; color: #58a6ff; text-decoration: none; white-space: nowrap; }
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

.archive-banner {
    background: #161b22;
    border: 1px solid #30363d;
    border-left: 4px solid #f97316;
    border-radius: 10px;
    padding: 0.6rem 1.2rem;
    font-size: 0.85rem;
    color: #8b949e;
    margin-bottom: 1.5rem;
}

.empty-state { text-align: center; padding: 5rem 2rem; color: #8b949e; }
.empty-state .icon { font-size: 3.5rem; margin-bottom: 1rem; }
.empty-state h2 { color: #e6edf3; font-weight: 700; margin-bottom: 0.5rem; }
.empty-state p  { font-size: 0.95rem; line-height: 1.6; }

.footer {
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid #21262d;
    text-align: center;
    color: #484f58;
    font-size: 0.78rem;
}

/* Streamlit tab overrides */
div[data-baseweb="tab-list"] { gap: 0.4rem; border-bottom: 1px solid #21262d !important; }
div[data-baseweb="tab"] { background: transparent !important; border-radius: 6px 6px 0 0 !important; color: #8b949e !important; font-size: 0.82rem !important; font-weight: 600 !important; padding: 0.4rem 0.9rem !important; }
div[aria-selected="true"] { color: #58a6ff !important; border-bottom: 2px solid #58a6ff !important; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_news(date_str=None):
    """Load news for today (date_str=None) or a past date (YYYY-MM-DD)."""
    if date_str:
        url = f"{ARCHIVE_BASE_URL}/{date_str}.json"
    else:
        url = GITHUB_RAW_URL
    try:
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200:
            return resp.json(), "github"
    except Exception:
        pass
    if date_str is None and LOCAL_FALLBACK.exists():
        with open(LOCAL_FALLBACK) as f:
            return json.load(f), "local"
    return None, None

def tag_html(tag):
    if not tag or tag not in TAG_CONFIG:
        return ""
    cfg = TAG_CONFIG[tag]
    return (f'<span class="tag-pill" style="background:{cfg["bg"]};color:{cfg["color"]};">'
            f'{cfg["emoji"]} {tag}</span>')

def format_generated_at(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("Updated %-I:%M %p · %b %-d, %Y")
    except Exception:
        return iso_str

def today_display():
    now = datetime.now()
    return now.strftime("%b %-d"), now.strftime("%A")

def render_story(story, idx):
    headline  = story.get("headline", "")
    summary   = story.get("summary", "")
    url       = story.get("url", "")
    tag       = story.get("tag", "")
    link_html = f'<div class="story-link"><a href="{url}" target="_blank">Read more ↗</a></div>' if url else ""
    st.markdown(f"""
    <div class="story-card">
      <div class="story-number">{idx}</div>
      <div class="story-content">
        {tag_html(tag)}
        <div class="story-headline">{headline}</div>
        <div class="story-summary">{summary}</div>
        {link_html}
      </div>
    </div>
    """, unsafe_allow_html=True)

def render_hit(hit, india=False):
    accent = "#f97316" if india else "#3fb950"
    if isinstance(hit, dict):
        text      = hit.get("text", "")
        url       = hit.get("url", "")
        link_html = f'<div class="qh-link"><a href="{url}" target="_blank">↗</a></div>' if url else ""
    else:
        text, link_html = hit, ""
    border = f'style="border-left: 3px solid {accent};"' if india else ""
    dot_style = f'style="background:{accent};"' if india else ""
    st.markdown(f"""
    <div class="qh-card" {border}>
      <div class="qh-dot" {dot_style}></div>
      <div class="qh-text">{text}</div>
      {link_html}
    </div>
    """, unsafe_allow_html=True)

# ── Sidebar — Archive picker ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📅 Browse Archive")
    st.caption("Pick a past date to read that day's edition.")
    today_date    = datetime.now().date()
    archive_start = date(2026, 4, 8)   # first archived day
    selected_date = st.date_input(
        "Date",
        value=today_date,
        min_value=archive_start,
        max_value=today_date,
        label_visibility="collapsed",
    )
    is_archive = selected_date < today_date
    date_str   = selected_date.strftime("%Y-%m-%d") if is_archive else None

# ── Load data ─────────────────────────────────────────────────────────────────
st.markdown('<meta http-equiv="refresh" content="300">', unsafe_allow_html=True)

data, source  = load_news(date_str)
day_short, weekday = today_display()
updated_str   = format_generated_at(data["generated_at"]) if data else "Awaiting first run…"

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

if is_archive:
    st.markdown(
        f'<div class="archive-banner">📂 Viewing archive for <strong>{selected_date.strftime("%B %-d, %Y")}</strong> — '
        f'open the sidebar to change date.</div>',
        unsafe_allow_html=True,
    )

# ── Empty state ───────────────────────────────────────────────────────────────
if not data:
    msg = (f"No archive found for {selected_date.strftime('%B %-d, %Y')}."
           if is_archive else
           "The scheduled task runs every day at <strong>8:00 AM</strong>.<br>"
           "Trigger it manually from the <strong>Scheduled</strong> section in Claude.")
    st.markdown(f"""
    <div class="empty-state">
      <div class="icon">📭</div>
      <h2>No news yet</h2>
      <p>{msg}</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Intro ─────────────────────────────────────────────────────────────────────
intro = data.get("intro", "")
if intro:
    st.markdown(f'<div class="intro-banner">{intro}</div>', unsafe_allow_html=True)

# ── Category filter ───────────────────────────────────────────────────────────
stories      = data.get("top_stories", [])
quick_hits   = data.get("quick_hits", [])
india_stories = data.get("india_roundup", [])

tab_all, tab_global, tab_india, tab_research, tab_funding, tab_policy, tab_models = st.tabs([
    "🗂️ All", "🌍 Global", "🇮🇳 India", "🧠 Research", "💰 Funding", "🏛️ Policy", "🤖 Models"
])

# ── All tab ───────────────────────────────────────────────────────────────────
with tab_all:
    if stories:
        st.markdown('<div class="section-label">📰 &nbsp;Top Stories</div>', unsafe_allow_html=True)
        for i, story in enumerate(stories, 1):
            render_story(story, i)
    st.markdown("<br>", unsafe_allow_html=True)
    if quick_hits:
        st.markdown('<div class="section-label">⚡ &nbsp;Quick Hits</div>', unsafe_allow_html=True)
        for hit in quick_hits:
            render_hit(hit)
    st.markdown("<br>", unsafe_allow_html=True)
    if india_stories:
        st.markdown('<div class="section-label">🇮🇳 &nbsp;India AI Roundup</div>', unsafe_allow_html=True)
        for story in india_stories:
            render_hit(story, india=True)
    st.markdown("<br>", unsafe_allow_html=True)
    insight = data.get("closing_insight", "")
    if insight:
        st.markdown('<div class="section-label">💡 &nbsp;Today\'s Insight</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight-box">"{insight}"</div>', unsafe_allow_html=True)

# ── Global tab ────────────────────────────────────────────────────────────────
with tab_global:
    if stories:
        st.markdown('<div class="section-label">📰 &nbsp;Top Stories</div>', unsafe_allow_html=True)
        for i, story in enumerate(stories, 1):
            render_story(story, i)
    st.markdown("<br>", unsafe_allow_html=True)
    if quick_hits:
        st.markdown('<div class="section-label">⚡ &nbsp;Quick Hits</div>', unsafe_allow_html=True)
        for hit in quick_hits:
            render_hit(hit)

# ── India tab ─────────────────────────────────────────────────────────────────
with tab_india:
    if india_stories:
        st.markdown('<div class="section-label">🇮🇳 &nbsp;India AI Roundup</div>', unsafe_allow_html=True)
        for story in india_stories:
            render_hit(story, india=True)
    else:
        st.info("No India stories for this edition.")

# ── Tag filter tabs ───────────────────────────────────────────────────────────
for tab, tag_name in [(tab_research, "Research"), (tab_funding, "Funding"),
                      (tab_policy, "Policy"), (tab_models, "Models")]:
    with tab:
        cfg = TAG_CONFIG[tag_name]
        tagged = [s for s in stories if s.get("tag") == tag_name]
        if tagged:
            st.markdown(f'<div class="section-label">{cfg["emoji"]} &nbsp;{tag_name}</div>',
                        unsafe_allow_html=True)
            for i, story in enumerate(tagged, 1):
                render_story(story, i)
        else:
            st.markdown(
                f'<div style="color:#8b949e;padding:2rem 0;text-align:center;">'
                f'No {tag_name} stories in today\'s edition.</div>',
                unsafe_allow_html=True,
            )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">Generated daily by Claude &nbsp;·&nbsp; Powered by Streamlit</div>',
    unsafe_allow_html=True,
)
