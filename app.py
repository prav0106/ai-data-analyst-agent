"""
AI Data Analyst Agent — Studio Edition
Chat with your data: instant insights, dashboards, quality reports & exports.
"""
import html as html_mod
import os
import sys
import warnings
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # loads GOOGLE_API_KEY from .env if present

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agent.orchestrator import DataAnalystAgent
from tools.data_tools import DataTools
from tools.quality_tools import generate_data_quality_report
from tools.report_generator import ReportGenerator

warnings.filterwarnings("ignore")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_CSV = os.path.join(BASE_DIR, "data", "sample_data.csv")

MODELS = [
    "gemini-2.5-flash-lite", "gemini-2.0-flash-lite",
    "gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.5-pro",
]

BRAND_COLORS = ["#0EA5E9", "#06B6D4", "#6366F1", "#10B981", "#F59E0B", "#EF4444", "#A855F7"]

# ============================================
# PAGE + PLOTLY THEME
# ============================================
st.set_page_config(page_title="AI Data Analyst Agent", page_icon="🤖", layout="wide")

pio.templates["saas"] = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Inter, ui-sans-serif, system-ui, sans-serif", size=13, color="#0F172A"),
        title=dict(font=dict(size=15, color="#0F172A"), x=0.01, xanchor="left"),
        paper_bgcolor="white", plot_bgcolor="white",
        colorway=BRAND_COLORS,
        margin=dict(l=10, r=16, t=52, b=8),
        hoverlabel=dict(bgcolor="#0F172A", font_size=12, bordercolor="#0F172A"),
        xaxis=dict(gridcolor="#EDF2F8", zerolinecolor="#E2E8F0", tickfont=dict(color="#64748B"), linecolor="#E2E8F0"),
        yaxis=dict(gridcolor="#EDF2F8", zerolinecolor="#E2E8F0", tickfont=dict(color="#64748B"), linecolor="#E2E8F0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.06, x=1, xanchor="right", bgcolor="rgba(0,0,0,0)"),
    )
)
pio.templates.default = "saas"


# ============================================
# CSS
# ============================================
def load_css() -> str:
    path = os.path.join(BASE_DIR, "static", "css", "styles.css")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f"<style>{f.read()}</style>"
    return ""


# ============================================
# SESSION STATE
# ============================================
def initialize_session_state():
    defaults = {
        "agent": None, "chat_history": [], "data_loaded": False,
        "current_df": None, "data_name": "", "analysis_count": 0,
        "suggested_qs": [], "last_ai_response": "", "quality_report": "",
        "agent_error": "", "init_attempted": False, "export_cache": {},
        "agent_model": MODELS[0],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def current_model_name() -> str:
    """Return the currently-selected Gemini model name."""
    return st.session_state.agent_model


# ============================================
# SMALL HTML COMPONENTS
# ============================================
def logo_svg(size: int = 42) -> str:
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 48 48" fill="none">
      <defs>
        <linearGradient id="lg{size}" x1="0" y1="0" x2="48" y2="48">
          <stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#E0F7FE"/>
        </linearGradient>
      </defs>
      <rect x="4" y="4" width="40" height="40" rx="12" fill="#0EA5E9" opacity="0.001"/>
      <rect x="10" y="26" width="6" height="12" rx="2" fill="url(#lg{size})" opacity=".55"/>
      <rect x="21" y="18" width="6" height="20" rx="2" fill="url(#lg{size})" opacity=".8"/>
      <rect x="32" y="10" width="6" height="28" rx="2" fill="url(#lg{size})"/>
      <path d="M10 20 L20 13 L29 17 L40 7" stroke="white" stroke-width="2.6"
            stroke-linecap="round" stroke-linejoin="round"/>
      <circle cx="40" cy="7" r="3" fill="#fff"/>
    </svg>"""


def chip(text: str, cls: str = "neutral", dot: bool = True) -> str:
    d = '<span class="dot"></span>' if dot else ""
    return f'<span class="chip {cls}">{d}{text}</span>'


def hero_html() -> str:
    agent = st.session_state.agent
    df = st.session_state.current_df

    if agent is not None:
        engine_chip = chip(f"<b>Gemini</b>&nbsp;· {current_model_name()}", "good")
    else:
        engine_chip = chip("AI engine offline — add API key", "warn")

    if st.session_state.data_loaded and df is not None:
        data_chip = chip(
            f"<b>{html_mod.escape(st.session_state.data_name or 'dataset')}</b>&nbsp;· {len(df):,} rows × {len(df.columns)} cols",
            "neutral")
    else:
        data_chip = chip("No dataset loaded", "neutral")

    return f"""
    <div class="hero">
        <div class="hero-left">
            <div class="hero-logo">{logo_svg(34)}</div>
            <div>
                <div class="hero-title">AI Data Analyst <span>Agent</span></div>
                <div class="hero-sub">Chat with your data — instant insights, dashboards &amp; reports</div>
            </div>
        </div>
        <div class="hero-chips">{engine_chip}{data_chip}</div>
    </div>"""


def metric_card(value: str, label: str, accent: str = "", hint: str = "") -> str:
    h = f'<div class="metric-hint">{hint}</div>' if hint else ""
    return (f'<div class="metric-card {accent}"><div class="metric-value">{value}</div>'
            f'<div class="metric-label">{label}</div>{h}</div>')


def empty_state(icon: str, title: str, desc: str) -> str:
    return (f'<div class="empty-state"><div class="big">{icon}</div>'
            f'<div class="t">{title}</div><div class="d">{desc}</div></div>')


def welcome_html() -> str:
    return f"""
    <div class="welcome">
        <div class="welcome-icon">{logo_svg(46)}</div>
        <h2>Analyze any CSV in seconds</h2>
        <p>Upload a dataset, connect Gemini, and ask questions in plain English —
           the agent builds dashboards, finds insights and checks data quality for you.</p>
        <div class="steps">
            <div class="step"><span class="n">1</span><div class="t">Upload a CSV</div>
                <div class="d">Drag &amp; drop your file, or try the built-in sample dataset.</div></div>
            <div class="step"><span class="n">2</span><div class="t">Connect Gemini</div>
                <div class="d">Paste a free Google AI API key in the sidebar to power the agent.</div></div>
            <div class="step"><span class="n">3</span><div class="t">Ask anything</div>
                <div class="d">Get insights, charts, quality reports and exportable summaries.</div></div>
        </div>
    </div>"""


def user_bubble(text: str, time: str) -> str:
    safe = html_mod.escape(text)
    return (f'<div class="chat-row user"><div class="bubble user-bubble">{safe}'
            f'<div class="chat-meta">{time}</div></div></div>')


# ============================================
# DATA HELPERS
# ============================================
def load_dataframe(path: str, name: str):
    """Load a CSV into the agent's global store + session, refresh quality/suggestions."""
    DataTools().load_csv_direct(path, "uploaded_data")
    df = pd.read_csv(path)
    st.session_state.current_df = df
    st.session_state.data_loaded = True
    st.session_state.data_name = name
    st.session_state.quality_report = generate_data_quality_report(df)
    st.session_state.suggested_qs = suggest_for(df)
    if st.session_state.agent is not None:
        st.session_state.agent.current_quality = st.session_state.quality_report


def suggest_for(df: pd.DataFrame) -> list:
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
    sug = ["Give me a comprehensive summary of this dataset",
           "What are the top 3 business insights from this data?",
           "Show descriptive statistics for all numeric columns"]
    if len(num_cols) >= 2:
        sug.append(f"Find correlation between {num_cols[0]} and {num_cols[1]}")
        sug.append(f"Detect outliers in {num_cols[0]}")
    if cat_cols and num_cols:
        sug.append(f"Compare average {num_cols[0]} across different {cat_cols[0]}")
    return sug[:5]


def quality_score(df: pd.DataFrame):
    miss_pct = df.isnull().sum().sum() / max(1, df.size) * 100
    dup_pct = df.duplicated().sum() / max(1, len(df)) * 100
    out_pct = 0.0
    num_df = df.select_dtypes(include="number")
    if not num_df.empty:
        total_out = 0
        for c in num_df.columns:
            q1, q3 = num_df[c].quantile([0.25, 0.75])
            iqr = q3 - q1
            if iqr > 0:
                total_out += int(((num_df[c] < q1 - 1.5 * iqr) | (num_df[c] > q3 + 1.5 * iqr)).sum())
        out_pct = total_out / max(1, num_df.size) * 100
    score = max(0, round(100 - miss_pct * 0.5 - dup_pct * 0.5 - out_pct * 0.25))
    color = "#10B981" if score >= 85 else ("#F59E0B" if score >= 65 else "#EF4444")
    verdict = "Excellent" if score >= 85 else ("Needs attention" if score >= 65 else "Poor")
    return score, color, verdict


Q_SECTIONS = {
    "Missing Values": ("🔍", "c-blue"),
    "Duplicate Rows": ("♻️", "c-amber"),
    "Outlier Analysis (IQR Method)": ("⚠️", "c-red"),
    "Column Data Types": ("🗂️", "c-indigo"),
    "Memory Usage": ("💾", "c-green"),
    "Recommendations": ("💡", "c-cyan"),
}


def parse_quality(text: str):
    """Parse the plain-text quality report into (title, lines) sections."""
    sections, current = [], None
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line in Q_SECTIONS:
            current = (line, [])
            sections.append(current)
        elif current is not None:
            current[1].append(line)
        elif line.startswith("Dataset Shape"):
            continue  # shown as metrics elsewhere
    return sections


# ============================================
# CHAT
# ============================================
def run_query(query: str):
    agent = st.session_state.agent
    if agent is None:
        st.toast("🔑 Connect Gemini first — add your API key in the sidebar", icon="🔑")
        return
    now = datetime.now().strftime("%H:%M")
    st.session_state.chat_history.append({"role": "user", "content": query, "time": now})
    with st.spinner("Analyzing your data…"):
        response = st.session_state.agent.chat(query)
    st.session_state.chat_history.append(
        {"role": "assistant", "content": response["output"], "time": datetime.now().strftime("%H:%M")})
    st.session_state.last_ai_response = response["output"]
    st.session_state.analysis_count += 1
    if st.session_state.current_df is not None:
        st.session_state.suggested_qs = suggest_for(st.session_state.current_df)


def render_chat():
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(user_bubble(msg["content"], msg.get("time", "")), unsafe_allow_html=True)
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(msg["content"])
                st.caption(msg.get("time", ""))


# ============================================
# DASHBOARD CHARTS
# ============================================
def generate_auto_dashboard(df: pd.DataFrame):
    charts = []
    numeric = df.select_dtypes(include=["number"]).columns.tolist()
    cats = df.select_dtypes(include=["object"]).columns.tolist()

    if len(numeric) >= 2:
        corr = df[numeric].corr(numeric_only=True)
        fig = go.Figure(data=go.Heatmap(
            z=corr.values, x=corr.columns, y=corr.columns,
            colorscale="RdBu", zmid=0, text=corr.round(2).values,
            texttemplate="%{text}", textfont={"size": 10},
        ))
        fig.update_layout(title="Correlation matrix", height=430)
        charts.append(("Correlation", fig))

    if numeric:
        fig = px.histogram(df, x=numeric[0], title=f"Distribution of {numeric[0]}",
                           color_discrete_sequence=["#0EA5E9"], nbins=30)
        fig.update_layout(height=370)
        charts.append(("Distribution", fig))

    if cats:
        vc = df[cats[0]].value_counts().head(8).reset_index()
        vc.columns = [cats[0], "Count"]
        fig = px.bar(vc, x=cats[0], y="Count", title=f"Top {cats[0]} categories",
                     color_discrete_sequence=["#06B6D4"])
        fig.update_layout(height=370)
        charts.append(("Categories", fig))

    if len(numeric) > 1:
        fig = px.box(df, y=numeric[1], title=f"Spread of {numeric[1]} (box plot)",
                     color_discrete_sequence=["#6366F1"])
        fig.update_layout(height=370)
        charts.append(("Box plot", fig))

    if cats and df[cats[0]].nunique() <= 6:
        fig = px.pie(df, names=cats[0], title=f"{cats[0]} proportion",
                     color_discrete_sequence=BRAND_COLORS)
        fig.update_layout(height=370)
        charts.append(("Proportion", fig))

    if len(numeric) >= 2:
        fig = px.scatter(df, x=numeric[0], y=numeric[1],
                         color=cats[0] if cats else None,
                         title=f"{numeric[0]} vs {numeric[1]}")
        fig.update_layout(height=370)
        charts.append(("Scatter", fig))

    return charts


# ============================================
# EXPORT (signature-cached so bytes are not rebuilt every rerun)
# ============================================
def get_export_bundle() -> dict:
    df = st.session_state.current_df
    if df is None:
        return {}
    agent = st.session_state.agent
    insights = (agent.current_insights if agent else "") or st.session_state.last_ai_response
    quality = st.session_state.quality_report
    sig = "|".join(map(str, [len(df), len(df.columns), df.isnull().sum().sum(),
                             df.duplicated().sum(), len(insights), len(quality)]))
    cache = st.session_state.export_cache
    if cache.get("sig") == sig:
        return cache

    rg = ReportGenerator(df)
    bundle = {"sig": sig}
    try:
        bundle["pdf"] = rg.generate_pdf(insights, quality)
    except Exception as e:
        bundle["pdf_err"] = str(e)
    try:
        bundle["excel"] = rg.generate_excel()
    except Exception as e:
        bundle["excel_err"] = str(e)
    try:
        bundle["json"] = rg.generate_json()
    except Exception as e:
        bundle["json_err"] = str(e)

    st.session_state.export_cache = bundle
    return bundle


# ============================================
# API KEY / AGENT
# ============================================
def get_default_key() -> str:
    key = os.getenv("GOOGLE_API_KEY", "")
    if not key:
        try:
            key = st.secrets.get("GOOGLE_API_KEY", "")
        except Exception:
            key = ""
    return key


def init_agent(api_key: str, model: str) -> bool:
    try:
        st.session_state.agent = DataAnalystAgent(api_key=api_key, model=model)
        st.session_state.agent_model = model
        st.session_state.agent_error = ""
        return True
    except Exception as e:
        st.session_state.agent = None
        st.session_state.agent_error = str(e)
        return False


# ============================================
# MAIN APP
# ============================================
def main():
    initialize_session_state()
    st.markdown(load_css(), unsafe_allow_html=True)

    default_key = get_default_key()

    # Auto-connect once if a key is available from env/secrets
    if default_key and st.session_state.agent is None and not st.session_state.init_attempted:
        st.session_state.init_attempted = True
        init_agent(default_key, MODELS[0])

    # ---------------- SIDEBAR ----------------
    with st.sidebar:
        st.markdown(f"""
        <div class="side-brand">
            <div class="side-logo">{logo_svg(24)}</div>
            <div>
                <div class="side-name">Data Analyst</div>
                <div class="side-tag">AI-powered analytics studio</div>
            </div>
        </div>""", unsafe_allow_html=True)

        # --- AI engine ---
        st.markdown('<div class="side-label">AI Engine</div>', unsafe_allow_html=True)

        if st.session_state.agent is not None:
            st.markdown('<span class="status-pill on"><span class="dot"></span>'
                        f'Connected · {current_model_name()}</span>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-pill off"><span class="dot"></span>Offline</span>',
                        unsafe_allow_html=True)

        api_key = st.text_input("Google AI API key", type="password",
                                help="Free key from aistudio.google.com",
                                placeholder="paste your key…" if default_key else "")

        model = st.selectbox("Model", MODELS,
                             help="Flash-lite is fastest & cheapest · Pro is deepest")

        if st.session_state.agent is None:
            if st.button("🚀 Connect Gemini", width='stretch', type="primary"):
                key = api_key.strip() or default_key
                if not key:
                    st.toast("Paste your Google AI API key first", icon="🔑")
                elif init_agent(key, model):
                    st.toast("Gemini connected 🎉", icon="✅")
                    st.rerun()
                else:
                    st.error(f"Could not connect: {st.session_state.agent_error}")
        else:
            if st.button("🔄 Reconnect / change model", width='stretch'):
                key = api_key.strip() or default_key
                if init_agent(key, model):
                    st.toast(f"Switched to {model}", icon="✅")
                    st.rerun()
            if not default_key:
                st.caption("🔑 Key is kept in this session only — not stored.")

        if not default_key and st.session_state.agent is None:
            st.markdown("👉 [Get a free API key](https://aistudio.google.com/app/apikey)")

        st.divider()

        # --- Quick actions ---
        st.markdown('<div class="side-label">Quick Actions</div>', unsafe_allow_html=True)
        quick = [
            ("📋 Data summary", "Give me a comprehensive summary"),
            ("🔗 Correlations", "Find all strong correlations"),
            ("⚠️ Outliers", "Detect outliers in all numeric columns"),
            ("💡 Smart insights", "Generate deep business insights"),
            ("🔍 Quality report", "Show me a complete data quality report"),
        ]
        for label, q in quick:
            if st.button(label, key=f"qa_{label}", width='stretch'):
                run_query(q)
                st.rerun()

        st.divider()

        # --- Export ---
        if st.session_state.data_loaded:
            st.markdown('<div class="side-label">Export Report</div>', unsafe_allow_html=True)
            bundle = get_export_bundle()
            c1, c2 = st.columns(2)
            if "pdf" in bundle:
                c1.download_button("📄 PDF", bundle["pdf"], "AI_Report.pdf", "application/pdf",
                                   width='stretch')
            if "excel" in bundle:
                c2.download_button("📊 Excel", bundle["excel"], "AI_Report.xlsx",
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   width='stretch')
            if "json" in bundle:
                st.download_button("🧾 JSON", bundle["json"], "AI_Report.json", "application/json",
                                   width='stretch')
            errs = [f"{k[:-4]}: {v}" for k, v in bundle.items() if k.endswith("_err")]
            if errs:
                st.caption("⚠️ " + " · ".join(errs))

            st.divider()

        # --- Session ---
        st.markdown('<div class="side-label">Session</div>', unsafe_allow_html=True)
        if st.button("🗑️ Clear chat", width='stretch'):
            st.session_state.chat_history = []
            st.session_state.analysis_count = 0
            st.session_state.export_cache = {}
            if st.session_state.agent:
                st.session_state.agent.clear_history()
            st.rerun()
        st.caption(f"{st.session_state.analysis_count} queries asked this session")

        st.markdown('<div class="side-foot">Powered by Gemini · LangChain · Streamlit</div>',
                    unsafe_allow_html=True)

    # ---------------- HEADER ----------------
    st.markdown(hero_html(), unsafe_allow_html=True)

    # ---------------- TABS ----------------
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "📊 Dashboard", "🔍 Data Quality", "📈 Charts"])

    # ===== TAB 1 — CHAT =====
    with tab1:
        if not st.session_state.data_loaded:
            st.markdown(welcome_html(), unsafe_allow_html=True)

            c1, c2, _ = st.columns([1.4, 1, .4])
            with c1:
                st.file_uploader("Upload your CSV", type=["csv"], key="welcome_upload",
                                 label_visibility="collapsed")
            with c2:
                if st.button("✨ Try sample dataset", width='stretch', type="primary"):
                    load_dataframe(SAMPLE_CSV, "sample_data.csv")
                    st.toast("Sample dataset loaded — explore the tabs below 👀", icon="📊")
                    st.rerun()
        else:
            left, right = st.columns([1.9, 1], gap="medium")

            with left:
                with st.expander(f"📁 {st.session_state.data_name} — upload a different file", expanded=False):
                    new_file = st.file_uploader("Upload your CSV", type=["csv"], key="main_upload",
                                                label_visibility="collapsed")
                    if new_file is not None:
                        tmp = os.path.join(BASE_DIR, f"temp_{new_file.name}")
                        with open(tmp, "wb") as f:
                            f.write(new_file.getbuffer())
                        try:
                            load_dataframe(tmp, new_file.name)
                            st.toast(f"{new_file.name} loaded ✅", icon="📥")
                            st.rerun()
                        finally:
                            if os.path.exists(tmp):
                                os.remove(tmp)

                if st.session_state.chat_history:
                    render_chat()
                else:
                    st.markdown(empty_state("💬", "Ask your first question",
                                            "e.g. “What drives sales the most?” or use a quick action in the sidebar."),
                                unsafe_allow_html=True)

                if st.session_state.agent is None:
                    st.info("🔑 Connect Gemini in the sidebar to start chatting — you can still "
                            "explore the Dashboard, Quality and Charts tabs meanwhile.")
                prompt = st.chat_input("Ask me anything about your data…",
                                       disabled=st.session_state.agent is None)
                if prompt:
                    run_query(prompt)
                    st.rerun()

                if st.session_state.suggested_qs and st.session_state.agent is not None:
                    st.markdown('<div class="side-label" style="margin-top:12px">Try asking</div>',
                                unsafe_allow_html=True)
                    cols = st.columns(min(3, len(st.session_state.suggested_qs)))
                    for i, q in enumerate(st.session_state.suggested_qs):
                        with cols[i % len(cols)]:
                            if st.button(q, key=f"sug_{i}", width='stretch'):
                                run_query(q)
                                st.rerun()

            with right:
                df = st.session_state.current_df
                st.markdown('<div class="side-label">Dataset snapshot</div>', unsafe_allow_html=True)

                num_n = len(df.select_dtypes(include="number").columns)
                cat_n = len(df.select_dtypes(include="object").columns)
                m1, m2 = st.columns(2)
                with m1:
                    st.markdown(metric_card(f"{len(df):,}", "Rows", hint=f"{num_n} numeric cols"),
                                unsafe_allow_html=True)
                with m2:
                    st.markdown(metric_card(str(len(df.columns)), "Columns", "indigo",
                                            hint=f"{cat_n} text cols"), unsafe_allow_html=True)
                m3, m4 = st.columns(2)
                with m3:
                    miss = int(df.isnull().sum().sum())
                    pct = round(miss / max(1, df.size) * 100, 1)
                    st.markdown(metric_card(f"{miss:,}", "Missing cells", "red" if miss else "green",
                                            hint=f"{pct}% of data"), unsafe_allow_html=True)
                with m4:
                    dups = int(df.duplicated().sum())
                    st.markdown(metric_card(f"{dups:,}", "Duplicate rows", "amber" if dups else "green"),
                                unsafe_allow_html=True)

                score, color, verdict = quality_score(df)
                st.markdown(f"""
                <div class="panel" style="display:flex;align-items:center;gap:14px;">
                    <div class="q-score" style="padding:0;margin:0;background:none;border:none;box-shadow:none;">
                        <div class="score-ring" style="--p:{score};--sc:{color};width:64px;height:64px;flex:0 0 64px;">
                            <span style="font-size:1rem;">{score}</span>
                        </div>
                    </div>
                    <div>
                        <div style="font-weight:700;font-size:.9rem;">Data quality: {verdict}</div>
                        <div class="score-bar" style="width:150px;"><i style="width:{score}%;--sc:{color};background:{color};"></i></div>
                        <div style="font-size:.72rem;color:var(--muted);margin-top:4px;">Full report in the Quality tab →</div>
                    </div>
                </div>""", unsafe_allow_html=True)

                with st.container(border=True):
                    st.markdown("**Preview**")
                    st.dataframe(df.head(8), width='stretch', height=260, hide_index=True)

    # ===== TAB 2 — DASHBOARD =====
    with tab2:
        if not (st.session_state.data_loaded and st.session_state.current_df is not None):
            st.markdown(empty_state("📊", "No dashboard yet",
                                    "Upload a CSV in the Chat tab (or load the sample dataset) to auto-generate one."),
                        unsafe_allow_html=True)
        else:
            df = st.session_state.current_df
            k1, k2, k3, k4, k5 = st.columns(5)
            with k1:
                st.markdown(metric_card(f"{len(df):,}", "Rows", hint="observations"), unsafe_allow_html=True)
            with k2:
                st.markdown(metric_card(str(len(df.columns)), "Columns", "indigo"), unsafe_allow_html=True)
            with k3:
                miss = int(df.isnull().sum().sum())
                st.markdown(metric_card(f"{miss:,}", "Missing", "red" if miss else "green"), unsafe_allow_html=True)
            with k4:
                dups = int(df.duplicated().sum())
                st.markdown(metric_card(f"{dups:,}", "Duplicates", "amber" if dups else "green"), unsafe_allow_html=True)
            with k5:
                mem = df.memory_usage(deep=True).sum() / 1024
                val = f"{mem:.1f} KB" if mem < 1024 else f"{mem/1024:.1f} MB"
                st.markdown(metric_card(val, "Memory", "green"), unsafe_allow_html=True)

            charts = generate_auto_dashboard(df)
            if charts:
                first, *rest = charts
                st.plotly_chart(first[1], width='stretch')
                for i in range(0, len(rest), 2):
                    cols = st.columns(2)
                    for j, (name, fig) in enumerate(rest[i:i + 2]):
                        with cols[j]:
                            st.plotly_chart(fig, width='stretch')
            else:
                st.markdown(empty_state("📉", "Not enough variety",
                                        "This dataset doesn't have numeric or categorical columns to chart."),
                            unsafe_allow_html=True)

    # ===== TAB 3 — QUALITY =====
    with tab3:
        if not (st.session_state.data_loaded and st.session_state.current_df is not None):
            st.markdown(empty_state("🔍", "No data to check",
                                    "Upload a CSV to see missing values, duplicates, outliers and recommendations."),
                        unsafe_allow_html=True)
        else:
            df = st.session_state.current_df
            if not st.session_state.quality_report:
                st.session_state.quality_report = generate_data_quality_report(df)
                if st.session_state.agent:
                    st.session_state.agent.current_quality = st.session_state.quality_report

            score, color, verdict = quality_score(df)
            miss = int(df.isnull().sum().sum())
            dups = int(df.duplicated().sum())
            st.markdown(f"""
            <div class="q-score">
                <div class="score-ring" style="--p:{score};--sc:{color};"><span>{score}</span></div>
                <div style="flex:1;min-width:220px;">
                    <div style="font-weight:800;font-size:1.05rem;color:var(--ink);">
                        Data quality score — {verdict}
                    </div>
                    <div style="font-size:.82rem;color:var(--muted);margin:2px 0 6px;">
                        {len(df):,} rows × {len(df.columns)} columns ·
                        <b style="color:var(--red);">{miss:,} missing</b> ·
                        <b style="color:var(--amber);">{dups:,} duplicates</b>
                    </div>
                    <div class="score-bar"><i style="width:{score}%;background:{color};"></i></div>
                </div>
            </div>""", unsafe_allow_html=True)

            sections = parse_quality(st.session_state.quality_report)
            half = (len(sections) + 1) // 2
            col_l, col_r = st.columns(2, gap="medium")
            for idx, (title, lines) in enumerate(sections):
                icon, cls = Q_SECTIONS.get(title, ("📄", "c-cyan"))
                items = "".join(f"<li>{html_mod.escape(l)}</li>" for l in lines)
                card = (f'<div class="q-card {cls}"><h4>{icon} {html_mod.escape(title)}</h4>'
                        f"<ul>{items}</ul></div>")
                (col_l if idx < half else col_r).markdown(card, unsafe_allow_html=True)

    # ===== TAB 4 — CUSTOM CHARTS =====
    with tab4:
        if not (st.session_state.data_loaded and st.session_state.current_df is not None):
            st.markdown(empty_state("📈", "Nothing to plot yet",
                                    "Upload a CSV first, then build bar, line, scatter, histogram, box or pie charts."),
                        unsafe_allow_html=True)
        else:
            df = st.session_state.current_df
            num_cols = df.select_dtypes(include=["number"]).columns.tolist()
            cat_cols = df.select_dtypes(include=["object"]).columns.tolist()

            c0, c1, c2, c3 = st.columns([1.2, 1, 1, 1])
            chart_type = c0.selectbox("Chart type", ["Bar", "Line", "Scatter", "Histogram", "Box", "Pie"])
            fig = None

            try:
                if chart_type == "Bar":
                    x = c1.selectbox("X axis", df.columns.tolist())
                    y = c2.selectbox("Y axis (value)", num_cols)
                    if y:
                        agg = c3.selectbox("Aggregation", ["sum", "mean", "count"])
                        grouped = df.groupby(x, dropna=False)[y].agg(agg).reset_index()
                        fig = px.bar(grouped, x=x, y=y, title=f"{agg.title()} of {y} by {x}",
                                     color_discrete_sequence=["#0EA5E9"])
                elif chart_type == "Line":
                    x = c1.selectbox("X axis", df.columns.tolist())
                    y = c2.selectbox("Y axis", num_cols)
                    if x and y:
                        fig = px.line(df.sort_values(x), x=x, y=y, title=f"{y} over {x}",
                                      markers=True, color_discrete_sequence=["#06B6D4"])
                elif chart_type == "Scatter":
                    x = c1.selectbox("X axis", num_cols)
                    y = c2.selectbox("Y axis", num_cols)
                    color = c3.selectbox("Color by", [None] + cat_cols)
                    if x and y:
                        fig = px.scatter(df, x=x, y=y, color=color, title=f"{x} vs {y}",
                                         opacity=.75)
                elif chart_type == "Histogram":
                    col = c1.selectbox("Column", num_cols)
                    bins = c2.slider("Bins", 10, 80, 30)
                    if col:
                        fig = px.histogram(df, x=col, nbins=bins, title=f"Distribution of {col}",
                                           color_discrete_sequence=["#6366F1"], marginal="box")
                elif chart_type == "Box":
                    y = c1.selectbox("Value", num_cols)
                    x = c2.selectbox("Group by", [None] + cat_cols)
                    if y:
                        fig = px.box(df, x=x, y=y, title=f"Spread of {y}", color_discrete_sequence=["#10B981"])
                elif chart_type == "Pie":
                    col = c1.selectbox("Column", cat_cols)
                    if col:
                        vc = df[col].value_counts().head(10).reset_index()
                        vc.columns = [col, "Count"]
                        fig = px.pie(vc, names=col, values="Count", title=f"{col} share",
                                     color_discrete_sequence=BRAND_COLORS)
            except Exception as e:
                st.error(f"Chart error: {e}")

            if fig is not None:
                fig.update_layout(height=470)
                with st.container(border=True):
                    st.plotly_chart(fig, width='stretch')
            elif num_cols or cat_cols:
                st.markdown(empty_state("🎛️", "Pick your axes",
                                        "Choose the columns above and your chart appears here."), unsafe_allow_html=True)

    st.markdown('<div class="app-foot">AI Data Analyst Agent · built with Streamlit, LangChain &amp; Google Gemini</div>',
                unsafe_allow_html=True)


if __name__ == "__main__":
    main()
