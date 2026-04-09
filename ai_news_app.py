import streamlit as st
import json
import requests
from datetime import datetime, date
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
GITHUB_USER   = "snehaaiyer"
GITHUB_REPO   = "ai-news-dashboard"
GITHUB_BRANCH = "main"
GITHUB_RAW_URL      = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/ai_news_daily.json"
OPERATOR_RAW_URL    = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/ai_news_operator.json"
ARCHIVE_BASE_URL    = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/archive"
LOCAL_FALLBACK      = Path(__file__).parent / "ai_news_daily.json"
LOCAL_OP_FALLBACK   = Path(__file__).parent / "ai_news_operator.json"

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

/* ── Operator edition cards ── */
.op-big-story {
    background: linear-gradient(135deg, #0d1117 0%, #1a1124 100%);
    border: 1px solid #30363d;
    border-top: 3px solid #f85149;
    border-radius: 14px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.5rem;
}
.op-big-story .op-headline { font-size: 1.15rem; font-weight: 800; color: #e6edf3; margin-bottom: 1rem; line-height: 1.35; }
.op-sub-label { font-size: 0.7rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #8b949e; margin-bottom: 0.3rem; }
.op-sub-text  { font-size: 0.9rem; color: #c9d1d9; line-height: 1.65; margin-bottom: 0.9rem; }
.op-revenue-box {
    background: #0f2d0f;
    border: 1px solid #238636;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.88rem;
    color: #56d364;
    line-height: 1.6;
}

.op-cluster {
    background: #0d1117;
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 1rem;
}
.op-cluster-title { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #8b949e; margin-bottom: 0.8rem; }
.op-row { display: flex; gap: 0.5rem; margin-bottom: 0.6rem; align-items: flex-start; }
.op-row:last-child { margin-bottom: 0; }
.op-row-summary    { font-size: 0.88rem; color: #e6edf3; font-weight: 600; flex: 1; line-height: 1.5; }
.op-row-impl       { font-size: 0.82rem; color: #8b949e; flex: 1; line-height: 1.5; }
.op-divider        { width: 1px; background: #21262d; flex-shrink: 0; align-self: stretch; }

.op-money {
    background: #0d1117;
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 1rem;
}
.op-money-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.op-money-cell { }
.op-money-cell-label { font-size: 0.68rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #8b949e; margin-bottom: 0.4rem; }
.op-money-item { font-size: 0.83rem; color: #c9d1d9; line-height: 1.5; padding: 0.2rem 0; border-bottom: 1px solid #21262d; }
.op-money-item:last-child { border-bottom: none; }
.op-winner { color: #56d364 !important; }
.op-loser  { color: #f85149 !important; }

.op-insight {
    background: #1c1624;
    border: 1px solid #30363d;
    border-left: 4px solid #d2a8ff;
    border-radius: 12px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1rem;
}
.op-insight-company { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #d2a8ff; margin-bottom: 0.5rem; }

.op-playbook {
    background: #0d1117;
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 1rem;
}
.op-audience { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #ffa657; margin-bottom: 0.4rem; margin-top: 0.8rem; }
.op-audience:first-child { margin-top: 0; }
.op-action { font-size: 0.88rem; color: #c9d1d9; line-height: 1.6; padding-left: 1rem; position: relative; margin-bottom: 0.3rem; }
.op-action::before { content: "→"; position: absolute; left: 0; color: #ffa657; font-weight: 700; }

.op-trend {
    background: #1c2128;
    border: 1px solid #30363d;
    border-left: 4px solid #58a6ff;
    border-radius: 10px;
    padding: 1rem 1.4rem;
    font-size: 0.95rem;
    color: #c9d1d9;
    line-height: 1.7;
    margin-bottom: 1rem;
}

.op-tldr {
    background: #0d1117;
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
}
.op-tldr-row { display: flex; gap: 0.8rem; align-items: flex-start; padding: 0.5rem 0; border-bottom: 1px solid #21262d; }
.op-tldr-row:last-child { border-bottom: none; }
.op-tldr-icon  { font-size: 1rem; flex-shrink: 0; margin-top: 0.05rem; }
.op-tldr-label { font-size: 0.68rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #8b949e; min-width: 5rem; margin-top: 0.15rem; }
.op-tldr-text  { font-size: 0.88rem; color: #c9d1d9; line-height: 1.55; }

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
    """Load general news for today (date_str=None) or a past date (YYYY-MM-DD)."""
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

@st.cache_data(ttl=300)
def load_operator(date_str=None):
    """Load operator edition for today or a past date."""
    if date_str:
        url = f"{ARCHIVE_BASE_URL}/{date_str}-operator.json"
    else:
        url = OPERATOR_RAW_URL
    try:
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    if date_str is None and LOCAL_OP_FALLBACK.exists():
        with open(LOCAL_OP_FALLBACK) as f:
            return json.load(f)
    return None

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

# ── Sidebar — archive only ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📅 Browse Archive")
    st.caption("Pick a past date to read that day's edition.")
    today_date    = datetime.now().date()
    archive_start = date(2026, 4, 8)
    selected_date = st.date_input(
        "Date",
        value=today_date,
        min_value=archive_start,
        max_value=today_date,
        label_visibility="collapsed",
    )
    is_archive = selected_date < today_date
    date_str   = selected_date.strftime("%Y-%m-%d") if is_archive else None

# ── Edition state (must be resolved before data loading) ──────────────────────
if "edition" not in st.session_state:
    st.session_state["edition"] = "📰 General"
is_operator = st.session_state["edition"] == "💼 Operator Edition"

# ── Load data ─────────────────────────────────────────────────────────────────
st.markdown('<meta http-equiv="refresh" content="300">', unsafe_allow_html=True)

data, source   = load_news(date_str)
op_data        = load_operator(date_str)
day_short, weekday = today_display()
active_data    = op_data if is_operator else data
updated_str    = format_generated_at(active_data["generated_at"]) if active_data else "Awaiting first run…"

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

toggle_col, _, btn_col = st.columns([4, 5, 1])
with toggle_col:
    st.radio(
        "Edition",
        ["📰 General", "💼 Operator Edition"],
        horizontal=True,
        label_visibility="collapsed",
        key="edition",
    )
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
if not active_data:
    edition_label = "Operator Edition" if is_operator else "news"
    msg = (f"No {edition_label} archive found for {selected_date.strftime('%B %-d, %Y')}."
           if is_archive else
           "The scheduled task runs every day at <strong>8:00 AM</strong>.<br>"
           "Trigger it manually from the <strong>Scheduled</strong> section in Claude.")
    st.markdown(f"""
    <div class="empty-state">
      <div class="icon">📭</div>
      <h2>No content yet</h2>
      <p>{msg}</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# OPERATOR EDITION
# ══════════════════════════════════════════════════════════════════════════════
if is_operator:
    od = op_data  # shorthand

    # 🔥 Big Story
    big = od.get("big_story", {})
    if big:
        st.markdown('<div class="section-label">🔥 &nbsp;Big Story</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="op-big-story">
          <div class="op-headline">{big.get("headline","")}</div>
          <div class="op-sub-label">What happened</div>
          <div class="op-sub-text">{big.get("what_happened","")}</div>
          <div class="op-sub-label">Why it matters</div>
          <div class="op-sub-text">{big.get("why_it_matters","")}</div>
          <div class="op-revenue-box">💰 {big.get("revenue_impact","")}</div>
        </div>
        """, unsafe_allow_html=True)

    # ⚡ Key Headlines
    kh = od.get("key_headlines", {})
    CLUSTERS = [
        ("ads_monetization", "💸 Ads & Monetization"),
        ("ai_products",      "🤖 AI Products / Models"),
        ("distribution",     "📡 Distribution / Platforms"),
    ]
    if any(kh.get(k) for k, _ in CLUSTERS):
        st.markdown('<div class="section-label">⚡ &nbsp;Key Headlines</div>', unsafe_allow_html=True)
        for key, label in CLUSTERS:
            items = kh.get(key, [])
            if not items:
                continue
            rows_html = ""
            for item in items:
                rows_html += f"""
                <div class="op-row">
                  <div class="op-row-summary">{item.get("summary","")}</div>
                  <div class="op-divider"></div>
                  <div class="op-row-impl">{item.get("implication","")}</div>
                </div>"""
            st.markdown(f"""
            <div class="op-cluster">
              <div class="op-cluster-title">{label}</div>
              {rows_html}
            </div>
            """, unsafe_allow_html=True)

    # 💰 Where the Money Moves
    mm = od.get("money_moves", {})
    if mm:
        st.markdown('<div class="section-label">💰 &nbsp;Where the Money Moves</div>', unsafe_allow_html=True)

        def money_col(items, css_class="op-money-item"):
            return "".join(f'<div class="{css_class}">{i}</div>' for i in items)

        st.markdown(f"""
        <div class="op-money">
          <div class="op-money-grid">
            <div class="op-money-cell">
              <div class="op-money-cell-label">Revenue Shifts</div>
              {money_col(mm.get("revenue_shifts",[]))}
            </div>
            <div class="op-money-cell">
              <div class="op-money-cell-label">Ad Inventory</div>
              {money_col(mm.get("ad_inventory",[]))}
            </div>
            <div class="op-money-cell">
              <div class="op-money-cell-label">Pricing Power</div>
              {money_col(mm.get("pricing_power",[]))}
            </div>
            <div class="op-money-cell">
              <div class="op-money-cell-label">🟢 Winners</div>
              {money_col(mm.get("winners",[]), "op-money-item op-winner")}
              <div class="op-money-cell-label" style="margin-top:0.6rem;">🔴 Losers</div>
              {money_col(mm.get("losers",[]), "op-money-item op-loser")}
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # 🧩 Operator Insight
    oi = od.get("operator_insight", {})
    if oi:
        st.markdown('<div class="section-label">🧩 &nbsp;Operator Insight</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="op-insight">
          <div class="op-insight-company">{oi.get("company","")}</div>
          <div class="op-sub-text">{oi.get("strategy","")}</div>
          <div class="op-sub-label">Why it works</div>
          <div class="op-sub-text" style="margin-bottom:0;">{oi.get("why_effective","")}</div>
        </div>
        """, unsafe_allow_html=True)

    # 🛠️ Actionable Playbook
    pb = od.get("playbook", {})
    if pb:
        st.markdown('<div class="section-label">🛠️ &nbsp;Actionable Playbook</div>', unsafe_allow_html=True)
        audiences = [("marketers","🎯 Marketers"), ("pms","🗂️ PMs"), ("founders","🚀 Founders")]
        rows_html = ""
        for key, label in audiences:
            actions = pb.get(key, [])
            acts_html = "".join(f'<div class="op-action">{a}</div>' for a in actions)
            rows_html += f'<div class="op-audience">{label}</div>{acts_html}'
        st.markdown(f'<div class="op-playbook">{rows_html}</div>', unsafe_allow_html=True)

    # 📊 Trend
    trend = od.get("trend", "")
    if trend:
        st.markdown('<div class="section-label">📊 &nbsp;Trend / Pattern</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="op-trend">{trend}</div>', unsafe_allow_html=True)

    # 🎯 TL;DR
    tldr = od.get("tldr", {})
    if tldr:
        st.markdown('<div class="section-label">🎯 &nbsp;TL;DR</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="op-tldr">
          <div class="op-tldr-row">
            <div class="op-tldr-icon">💡</div>
            <div class="op-tldr-label">Insight</div>
            <div class="op-tldr-text">{tldr.get("insight","")}</div>
          </div>
          <div class="op-tldr-row">
            <div class="op-tldr-icon">🚀</div>
            <div class="op-tldr-label">Opportunity</div>
            <div class="op-tldr-text">{tldr.get("opportunity","")}</div>
          </div>
          <div class="op-tldr-row">
            <div class="op-tldr-icon">⚠️</div>
            <div class="op-tldr-label">Risk</div>
            <div class="op-tldr-text">{tldr.get("risk","")}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        '<div class="footer">Operator Edition · Generated daily by Claude &nbsp;·&nbsp; Powered by Streamlit</div>',
        unsafe_allow_html=True,
    )
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# GENERAL EDITION
# ══════════════════════════════════════════════════════════════════════════════

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
