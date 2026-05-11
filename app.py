"""
AI Data Analyst Agent - ULTIMATE VERSION
Features: Auto Dashboard, PDF/Excel/JSON Export, Smart Insights, Data Quality, Suggested Questions
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agent.orchestrator import DataAnalystAgent

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(page_title="AI Data Analyst Agent", page_icon="🤖", layout="wide")

# ============================================
# LOAD EXTERNAL CSS & JS
# ============================================
def load_css():
    css_path = "static/css/styles.css"
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            return f"<style>{f.read()}</style>"
    return ""

def load_js():
    js_path = "static/js/script.js"
    if os.path.exists(js_path):
        with open(js_path, "r", encoding="utf-8") as f:
            return f"<script>{f.read()}</script>"
    return ""

# ============================================
# SESSION STATE
# ============================================
def initialize_session_state():
    defaults = {
        'agent': None, 'chat_history': [], 'data_loaded': False,
        'current_df': None, 'analysis_count': 0, 'suggested_qs': [],
        'last_ai_response': "", 'quality_report': ""
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ============================================
# HELPER FUNCTIONS
# ============================================
def run_quick_action(query):
    if not st.session_state.agent:
        st.error("Initialize agent first!"); return
    if not st.session_state.data_loaded:
        st.error("Upload data first!"); return
    
    st.session_state.chat_history.append({"role": "user", "content": query, "time": datetime.now().strftime("%H:%M")})
    with st.spinner("🤔 Analyzing..."):
        response = st.session_state.agent.chat(query)
        st.session_state.chat_history.append({"role": "assistant", "content": response["output"], "time": datetime.now().strftime("%H:%M")})
        st.session_state.last_ai_response = response["output"]
        st.session_state.suggested_qs = st.session_state.agent.suggest_questions()
        st.session_state.analysis_count += 1

def generate_auto_dashboard(df):
    """Generate intelligent auto-dashboard charts"""
    charts = []
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    # 1. Correlation Heatmap
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr()
        fig = go.Figure(data=go.Heatmap(
            z=corr.values, x=corr.columns, y=corr.columns,
            colorscale='RdBu', zmid=0, text=corr.round(2).values,
            texttemplate='%{text}', textfont={"size": 10}
        ))
        fig.update_layout(title="🔗 Correlation Heatmap", template='plotly_white', height=450)
        charts.append(("Correlation", fig))
    
    # 2. Histogram for first numeric
    if numeric_cols:
        fig = px.histogram(df, x=numeric_cols[0], color_discrete_sequence=['#00D3EF'],
                          title=f"📊 Distribution of {numeric_cols[0]}")
        fig.update_layout(template='plotly_white', height=400)
        charts.append(("Distribution", fig))
    
    # 3. Bar chart for first categorical
    if cat_cols:
        vc = df[cat_cols[0]].value_counts().head(8).reset_index()
        vc.columns = [cat_cols[0], 'Count']
        fig = px.bar(vc, x=cat_cols[0], y='Count', color_discrete_sequence=['#222D35'],
                    title=f"📈 {cat_cols[0]} Distribution")
        fig.update_layout(template='plotly_white', height=400)
        charts.append(("Categories", fig))
    
    # 4. Box plot for second numeric
    if len(numeric_cols) > 1:
        fig = px.box(df, y=numeric_cols[1], color_discrete_sequence=['#00D3EF'],
                    title=f"⚡ {numeric_cols[1]} Box Plot")
        fig.update_layout(template='plotly_white', height=400)
        charts.append(("Box Plot", fig))
    
    # 5. Pie chart if categorical has few unique values
    if cat_cols and df[cat_cols[0]].nunique() <= 6:
        fig = px.pie(df, names=cat_cols[0], title=f"🥧 {cat_cols[0]} Proportion",
                    color_discrete_sequence=px.colors.sequential.Teal)
        fig.update_layout(template='plotly_white', height=400)
        charts.append(("Proportion", fig))
    
    # 6. Scatter if 2+ numerics
    if len(numeric_cols) >= 2:
        fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                        color=cat_cols[0] if cat_cols else None,
                        title=f"⚡ {numeric_cols[0]} vs {numeric_cols[1]}")
        fig.update_layout(template='plotly_white', height=400)
        charts.append(("Scatter", fig))
    
    return charts

# ============================================
# MAIN APP
# ============================================
def main():
    initialize_session_state()
    st.markdown(load_css(), unsafe_allow_html=True)
    st.markdown(load_js(), unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">🤖 AI Data Analyst Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">✨ Upload data & chat with AI for instant insights ✨</p>', unsafe_allow_html=True)
    
    # ============================================
    # SIDEBAR
    # ============================================
    with st.sidebar:
        st.header("⚙️ Settings")
        
        api_key = st.text_input("🔑 Google AI API Key", type="password",
                               help="Get free key from aistudio.google.com")
        
        if not api_key:
            st.warning("⚠️ Enter API key to continue")
            st.markdown("[Get Free API Key →](https://aistudio.google.com/app/apikey)")
            
            # Welcome info in sidebar area
            st.markdown("---")
            st.markdown("### 🚀 Features")
            st.markdown("""
            - 📊 Auto Dashboard
            - 📄 PDF/Excel/JSON Export
            - 💡 Smart AI Insights
            - 🔍 Data Quality Report
            - 💬 Contextual Suggestions
            """)
            st.stop()
        
        st.divider()
        
        # Model Selection
        st.subheader("🤖 Model")
        model = st.selectbox("Select", [
            "gemini-2.5-flash-lite", "gemini-2.0-flash-lite",
            "gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.5-pro"
        ])
        
        if st.button("🚀 Initialize Agent", use_container_width=True, type="primary"):
            with st.spinner("Starting..."):
                try:
                    st.session_state.agent = DataAnalystAgent(api_key=api_key, model=model)
                    st.success(f"✅ Ready!")
                except Exception as e:
                    st.error(f"❌ {str(e)}")
        
        st.divider()
        
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        qa = [
            ("📋 Data Summary", "Give me a comprehensive summary"),
            ("🔗 Find Correlations", "Find all strong correlations"),
            ("⚠️ Detect Outliers", "Detect outliers in all numeric columns"),
            ("💡 Smart Insights", "Generate deep business insights"),
            ("🔍 Data Quality", "Show me a complete data quality report")
        ]
        for label, query in qa:
            if st.button(label, use_container_width=True, key=f"qa_{label}"):
                run_quick_action(query)
                st.rerun()
        
        st.divider()
        
        # Export Section (Only when data loaded)
        if st.session_state.data_loaded and st.session_state.agent:
            st.markdown("### 📥 Export Report")
            rg = st.session_state.agent.get_report_generator()
            if rg:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📄 PDF", use_container_width=True):
                        pdf_bytes = rg.generate_pdf(
                            st.session_state.agent.current_insights,
                            st.session_state.agent.current_quality
                        )
                        st.download_button("Download PDF", pdf_bytes, "AI_Report.pdf", "application/pdf")
                with col2:
                    if st.button("📊 Excel", use_container_width=True):
                        excel_bytes = rg.generate_excel()
                        st.download_button("Download Excel", excel_bytes, "AI_Report.xlsx",
                                         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                
                if st.button("📋 JSON", use_container_width=True):
                    json_bytes = rg.generate_json()
                    st.download_button("Download JSON", json_bytes, "AI_Report.json", "application/json")
        
        st.divider()
        
        # Chat Controls
        st.markdown("### 💬 Controls")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.chat_history = []
                if st.session_state.agent: st.session_state.agent.clear_history()
                st.rerun()
        with c2:
            st.metric("Queries", st.session_state.analysis_count)
    
    # ============================================
    # TABS
    # ============================================
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat & Upload", "📊 Auto Dashboard", "🔍 Data Quality", "📈 Custom Charts"])
    
    # ---------- TAB 1: CHAT & UPLOAD ----------
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📁 Upload Your Data")
            uploaded_file = st.file_uploader("Choose CSV", type=['csv'])
            
            if uploaded_file and st.session_state.agent:
                save_path = f"temp_{uploaded_file.name}"
                with open(save_path, "wb") as f: f.write(uploaded_file.getbuffer())
                
                with st.spinner("Loading..."):
                    result = st.session_state.agent.process_file(save_path, "uploaded_data")
                    st.session_state.data_loaded = True
                    st.session_state.current_df = pd.read_csv(save_path)
                    st.session_state.quality_report = st.session_state.agent.current_quality
                    st.session_state.suggested_qs = st.session_state.agent.suggest_questions()
                
                st.success(result)
                os.remove(save_path)
            
            # Chat Interface
            if st.session_state.data_loaded:
                st.divider()
                st.subheader("💬 Chat with AI Analyst")
                
                # Show chat history
                for msg in st.session_state.chat_history:
                    if msg["role"] == "user":
                        st.markdown(f'<div class="user-message"><div class="user-bubble">{msg["content"]}</div></div>',
                                   unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="ai-message"><div class="ai-bubble">{msg["content"]}</div></div>',
                                   unsafe_allow_html=True)
                
                # Chat Input
                if prompt := st.chat_input("💭 Ask me about your data..."):
                    run_quick_action(prompt)
                    st.rerun()
                
                # Suggested Follow-up Questions
                if st.session_state.suggested_qs:
                    st.markdown("#### 💡 Suggested Follow-ups")
                    cols = st.columns(len(st.session_state.suggested_qs))
                    for idx, q in enumerate(st.session_state.suggested_qs):
                        with cols[idx]:
                            if st.button(q, key=f"sug_{idx}", use_container_width=True):
                                run_quick_action(q)
                                st.rerun()
        
        with col2:
            if st.session_state.data_loaded and st.session_state.current_df is not None:
                df = st.session_state.current_df
                
                # Metric Cards
                st.markdown("### 📊 Quick Stats")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f'<div class="metric-card"><div class="metric-value">{len(df)}</div><div class="metric-label">Rows</div></div>',
                               unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="metric-card"><div class="metric-value">{len(df.columns)}</div><div class="metric-label">Columns</div></div>',
                               unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                c3, c4 = st.columns(2)
                with c3:
                    missing = df.isnull().sum().sum()
                    st.markdown(f'<div class="metric-card" style="border-top: 4px solid #ef4444;"><div class="metric-value" style="font-size:1.8rem;">{missing}</div><div class="metric-label">Missing</div></div>',
                               unsafe_allow_html=True)
                with c4:
                    dups = df.duplicated().sum()
                    st.markdown(f'<div class="metric-card" style="border-top: 4px solid #f59e0b;"><div class="metric-value" style="font-size:1.8rem;">{dups}</div><div class="metric-label">Duplicates</div></div>',
                               unsafe_allow_html=True)
                
                st.divider()
                st.markdown("### 📋 Data Preview")
                st.dataframe(df.head(8), use_container_width=True, height=280)
    
    # ---------- TAB 2: AUTO DASHBOARD ----------
    with tab2:
        st.markdown("### 📊 Auto-Generated Dashboard")
        if st.session_state.data_loaded and st.session_state.current_df is not None:
            df = st.session_state.current_df
            charts = generate_auto_dashboard(df)
            
            if charts:
                for i in range(0, len(charts), 2):
                    cols = st.columns(2)
                    for j, (name, fig) in enumerate(charts[i:i+2]):
                        with cols[j]:
                            st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Not enough data variety for auto charts.")
        else:
            st.info("📥 Upload data to see auto dashboard")
    
    # ---------- TAB 3: DATA QUALITY ----------    # ---------- TAB 3: DATA QUALITY ----------
    with tab3:
        st.markdown("### 🔍 Comprehensive Data Quality Report")
        
        if st.session_state.data_loaded and st.session_state.current_df is not None:
            # Auto-generate if not present
            if not st.session_state.agent.current_quality:
                with st.spinner("Generating quality report..."):
                    from tools.quality_tools import generate_data_quality_report
                    st.session_state.agent.current_quality = generate_data_quality_report(st.session_state.current_df)
            
            # Parse the markdown report into sections for better styling
            report_text = st.session_state.agent.current_quality
            
            # Split by sections (## headers)
            sections = report_text.split('## ')
            
            # First section is usually title, skip if empty
            for section in sections:
                if not section.strip():
                    continue
                    
                lines = section.strip().split('\n')
                title = lines[0].strip().replace('📋 ', '').replace('🔍 ', '').replace('🔄 ', '').replace('⚠️ ', '').replace('📊 ', '').replace('💾 ', '').replace('💡 ', '')
                content = '\n'.join(lines[1:]).strip()
                
                # Skip empty sections
                if not content:
                    continue
                
                # Determine icon based on title
                icon = "📄"
                border_color = "#CBD5E1"
                bg_color = "#FFFFFF"
                if "Missing" in title:
                    icon = "🔍"
                    border_color = "#7DD3FC"
                    bg_color = "#F0F9FF"
                elif "Duplicate" in title:
                    icon = "🔄"
                    border_color = "#FCD34D"
                    bg_color = "#FFFBEB"
                elif "Outlier" in title:
                    icon = "⚠️"
                    border_color = "#FCA5A5"
                    bg_color = "#FEF2F2"
                elif "Data Type" in title:
                    icon = "📊"
                    border_color = "#C4B5FD"
                    bg_color = "#F5F3FF"
                elif "Memory" in title:
                    icon = "💾"
                    border_color = "#86EFAC"
                    bg_color = "#F0FDF4"
                elif "Recommend" in title:
                    icon = "💡"
                    border_color = "#00D3EF"
                    bg_color = "#ECFEFF"
                
                # Render styled card
                st.markdown(f"""
                <div style="
                    background: {bg_color};
                    border-left: 5px solid {border_color};
                    border-radius: 12px;
                    padding: 20px 24px;
                    margin-bottom: 16px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
                ">
                    <h4 style="
                        color: #222D35;
                        margin: 0 0 12px 0;
                        font-size: 1.15rem;
                        font-weight: 700;
                    ">{icon} {title}</h4>
                    <div style="
                        color: #334155;
                        font-size: 0.95rem;
                        line-height: 1.7;
                    ">
                        {content.replace(chr(10), '<br>').replace('**', '').replace('- ', '• ').replace('`', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
        else:
            st.info("📥 Upload data first to see quality report")
    
    # ---------- TAB 4: CUSTOM CHARTS ----------
    with tab4:
        st.markdown("### 📈 Custom Visualizations")
        if st.session_state.data_loaded and st.session_state.current_df is not None:
            df = st.session_state.current_df
            num_cols = df.select_dtypes(include=['number']).columns.tolist()
            cat_cols = df.select_dtypes(include=['object']).columns.tolist()
            
            chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Scatter", "Histogram", "Box", "Pie"])
            c1, c2 = st.columns(2)
            
            try:
                if chart_type == "Bar":
                    x = c1.selectbox("X", df.columns)
                    y = c2.selectbox("Y", num_cols) if num_cols else None
                    if y: st.plotly_chart(px.bar(df, x=x, y=y, color_discrete_sequence=['#00D3EF']), use_container_width=True)
                elif chart_type == "Histogram":
                    col = st.selectbox("Column", num_cols)
                    if col: st.plotly_chart(px.histogram(df, x=col, color_discrete_sequence=['#222D35']), use_container_width=True)
                elif chart_type == "Scatter":
                    x = c1.selectbox("X", num_cols)
                    y = c2.selectbox("Y", num_cols)
                    color = st.selectbox("Color", [None] + cat_cols)
                    if x and y: st.plotly_chart(px.scatter(df, x=x, y=y, color=color), use_container_width=True)
                elif chart_type == "Box":
                    y = st.selectbox("Y", num_cols)
                    x = st.selectbox("Group By", [None] + cat_cols)
                    if y: st.plotly_chart(px.box(df, x=x, y=y), use_container_width=True)
                elif chart_type == "Pie":
                    col = st.selectbox("Column", cat_cols)
                    if col: st.plotly_chart(px.pie(df, names=col), use_container_width=True)
            except Exception as e:
                st.error(f"Chart error: {str(e)}")
        else:
            st.info("Upload data first")

if __name__ == "__main__":
    main()