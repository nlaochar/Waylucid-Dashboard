import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# ============================================================
#  PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="WayLucid Capstone Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #0d0d1a; }
    [data-testid="stSidebar"] { background: #11112a; border-right: 1px solid #2a2a4a; }
    h1, h2, h3, h4, h5 { color: #e0e0f0 !important; }
    p, label, .stMarkdown, div[data-testid="stText"] { color: #a0a0c0 !important; }
    .section-header {
        font-size: 11px; font-weight: 600; letter-spacing: 1.5px;
        text-transform: uppercase; color: #6b7db3 !important;
        margin: 24px 0 12px 0; border-bottom: 0.5px solid #2a2a4a; padding-bottom: 6px;
    }
    .metric-card {
        background: #161628; border: 0.5px solid #2a2a4a;
        border-radius: 12px; padding: 16px 20px; margin-bottom: 10px;
    }
    .metric-label { font-size: 12px; color: #6b7db3; margin-bottom: 4px; }
    .metric-value { font-size: 26px; font-weight: 600; color: #e0e0f0; }
    .metric-sub { font-size: 11px; color: #6b7db3; margin-top: 2px; }
    div[data-testid="metric-container"] {
        background: #161628; border: 0.5px solid #2a2a4a;
        border-radius: 12px; padding: 12px 16px;
    }
    div[data-testid="metric-container"] label { color: #6b7db3 !important; }
    div[data-testid="metric-container"] div { color: #e0e0f0 !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
#  BUSINESS & FILE CONFIG
#  When you get CSV files for other businesses, uncomment
#  their sections below and fill in the exact filenames.
# ============================================================
BUSINESSES = {
    "NOLA Boards": {
        "color": "#7c3aed",
        "foot_traffic":    "pilot-nola-footTraffic-2026-04-12.csv",
        "repeat_visits":   "pilot-nola-repeatVisits-2026-04-12.csv",
        "dwell_time":      "pilot-nola-dwellTime-2026-04-12.csv",
        "redemption_rate": "pilot-nola-redemptionRate-2026-04-12.csv",
        "social_pulse":    "social-pulse-nola-boards.csv",
    },
    # "Lower Coast Coffee": {
    #     "color": "#1d9e75",
    #     "foot_traffic":    "pilot-lcc-footTraffic-2026-04-12.csv",
    #     "repeat_visits":   "pilot-lcc-repeatVisits-2026-04-12.csv",
    #     "dwell_time":      "pilot-lcc-dwellTime-2026-04-12.csv",
    #     "redemption_rate": "pilot-lcc-redemptionRate-2026-04-12.csv",
    #     "social_pulse":    "social-pulse-lower-coast-coffee.csv",
    # },
    # "AZ Chimney Cakes": {
    #     "color": "#e07b39",
    #     "foot_traffic":    "pilot-azcc-footTraffic-2026-04-12.csv",
    #     "repeat_visits":   "pilot-azcc-repeatVisits-2026-04-12.csv",
    #     "dwell_time":      "pilot-azcc-dwellTime-2026-04-12.csv",
    #     "redemption_rate": "pilot-azcc-redemptionRate-2026-04-12.csv",
    #     "social_pulse":    "social-pulse-az-chimney-cakes.csv",
    # },
    # "City of El Mirage": {
    #     "color": "#3b82f6",
    #     "foot_traffic":    "pilot-elmirage-footTraffic-2026-04-12.csv",
    #     "repeat_visits":   "pilot-elmirage-repeatVisits-2026-04-12.csv",
    #     "dwell_time":      "pilot-elmirage-dwellTime-2026-04-12.csv",
    #     "redemption_rate": "pilot-elmirage-redemptionRate-2026-04-12.csv",
    #     "social_pulse":    "social-pulse-el-mirage.csv",
    # },
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#11112a",
    font_color="#a0a0c0",
    font_size=12,
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis=dict(gridcolor="#1e1e38", linecolor="#2a2a4a"),
    yaxis=dict(gridcolor="#1e1e38", linecolor="#2a2a4a"),
)

# ============================================================
#  HELPERS
# ============================================================
@st.cache_data
def load_csv(filename):
    if filename is None or not os.path.exists(filename):
        return None
    df = pd.read_csv(filename)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df

def load_business(biz):
    files = BUSINESSES[biz]
    return {
        "foot_traffic":    load_csv(files.get("foot_traffic")),
        "repeat_visits":   load_csv(files.get("repeat_visits")),
        "dwell_time":      load_csv(files.get("dwell_time")),
        "redemption_rate": load_csv(files.get("redemption_rate")),
        "social_pulse":    load_csv(files.get("social_pulse")),
    }

def metric_card(label, value, sub=None):
    sub_html = f'<div class="metric-sub">{sub}</div>' if sub else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {sub_html}
    </div>""", unsafe_allow_html=True)

# ============================================================
#  SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## 🌐 WayLucid")
    st.markdown("**Capstone Analytics Dashboard**")
    st.markdown("*CIS 450 — ASU*")
    st.markdown("---")
    selected_biz = st.selectbox("Select Business", list(BUSINESSES.keys()))
    st.markdown("---")
    st.caption("Pilot data: Mar 14 – Apr 12, 2026")
    st.caption("Social data: Apr 7, 2026")
    st.markdown("---")
    st.caption("More businesses will appear in this dropdown once their CSV files are added to the repo.")

color = BUSINESSES[selected_biz]["color"]
data  = load_business(selected_biz)

# ============================================================
#  HEADER
# ============================================================
st.markdown(f"# 📊 {selected_biz} — Analytics Dashboard")
st.markdown("---")

# ============================================================
#  SECTION 1 — KPI CARDS
# ============================================================
st.markdown('<div class="section-header">Key Performance Indicators</div>', unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)

with k1:
    df = data["foot_traffic"]
    if df is not None:
        metric_card("Avg Daily Foot Traffic",
                    round(df["foot Traffic"].mean(), 1),
                    f"Peak: {round(df['foot Traffic'].max(), 1)}")
    else:
        metric_card("Avg Daily Foot Traffic", "N/A")

with k2:
    df = data["repeat_visits"]
    if df is not None:
        metric_card("Avg Repeat Visits",
                    round(df["repeat Visits"].mean(), 1),
                    f"Peak: {round(df['repeat Visits'].max(), 1)}")
    else:
        metric_card("Avg Repeat Visits", "N/A")

with k3:
    df = data["dwell_time"]
    if df is not None:
        metric_card("Avg Dwell Time (min)",
                    round(df["dwell Time"].mean(), 1))
    else:
        metric_card("Avg Dwell Time", "N/A")

with k4:
    df = data["redemption_rate"]
    if df is not None:
        metric_card("Avg Redemption Rate (%)",
                    round(df["redemption Rate"].mean(), 1),
                    f"Peak: {round(df['redemption Rate'].max(), 1)}%")
    else:
        metric_card("Avg Redemption Rate", "N/A")

# ============================================================
#  SECTION 2 — SOCIAL PULSE
# ============================================================
st.markdown('<div class="section-header">Social Pulse — Google · Yelp · Instagram</div>', unsafe_allow_html=True)

df_social = data["social_pulse"]
if df_social is not None:
    s1, s2, s3, s4 = st.columns(4)
    google = df_social[df_social["Platform"] == "google"]
    yelp   = df_social[df_social["Platform"] == "yelp"]
    insta  = df_social[df_social["Platform"] == "instagram"]

    with s1:
        if not google.empty:
            reviews = int(google["Review Count"].iloc[-1]) if pd.notna(google["Review Count"].iloc[-1]) else "—"
            metric_card("Google Rating", f"⭐ {google['Rating'].iloc[-1]}", f"{reviews} reviews")
    with s2:
        if not yelp.empty:
            reviews = int(yelp["Review Count"].iloc[-1]) if pd.notna(yelp["Review Count"].iloc[-1]) else "—"
            metric_card("Yelp Rating", f"⭐ {yelp['Rating'].iloc[-1]}", f"{reviews} reviews")
    with s3:
        if not insta.empty:
            followers = int(insta["Follower Count"].iloc[-1]) if pd.notna(insta["Follower Count"].iloc[-1]) else "—"
            metric_card("Instagram Followers", f"{followers:,}" if isinstance(followers, int) else followers)
    with s4:
        metric_card("Last Refreshed", "Apr 7, 2026")
else:
    st.info("No social pulse data available for this business.")

# ============================================================
#  SECTION 3 — FOOT TRAFFIC & REDEMPTION RATE
# ============================================================
st.markdown('<div class="section-header">Foot Traffic & Redemption Rate — 30 Day Trend</div>', unsafe_allow_html=True)

col_l, col_r = st.columns(2)

with col_l:
    df = data["foot_traffic"]
    if df is not None:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df["foot Traffic"],
            mode="lines+markers", name="Foot Traffic",
            line=dict(color=color, width=2), marker=dict(size=5),
            fill="tozeroy", fillcolor="rgba(124,58,237,0.08)",
        ))
        fig.add_hline(y=df["foot Traffic"].mean(), line_dash="dash",
                      line_color="#6b7db3",
                      annotation_text=f"Avg: {df['foot Traffic'].mean():.1f}")
        fig.update_layout(title="Daily Foot Traffic", yaxis_title="Score", **PLOTLY_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

with col_r:
    df = data["redemption_rate"]
    if df is not None:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df["Date"], y=df["redemption Rate"],
            mode="lines+markers", name="Redemption Rate",
            line=dict(color="#1d9e75", width=2), marker=dict(size=5),
            fill="tozeroy", fillcolor="rgba(29,158,117,0.08)",
        ))
        fig2.add_hline(y=df["redemption Rate"].mean(), line_dash="dash",
                       line_color="#6b7db3",
                       annotation_text=f"Avg: {df['redemption Rate'].mean():.1f}%")
        fig2.update_layout(title="Daily Redemption Rate (%)", yaxis_title="%", **PLOTLY_LAYOUT)
        st.plotly_chart(fig2, use_container_width=True)

# ============================================================
#  SECTION 4 — REPEAT VISITS & DWELL TIME
# ============================================================
st.markdown('<div class="section-header">Repeat Visits & Dwell Time</div>', unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    df = data["repeat_visits"]
    if df is not None:
        fig3 = go.Figure(go.Bar(
            x=df["Date"], y=df["repeat Visits"],
            marker_color=color, opacity=0.85, name="Repeat Visits",
        ))
        fig3.update_layout(title="Daily Repeat Visits", yaxis_title="Visits", **PLOTLY_LAYOUT)
        st.plotly_chart(fig3, use_container_width=True)

with col_b:
    df = data["dwell_time"]
    if df is not None:
        fig4 = go.Figure(go.Scatter(
            x=df["Date"], y=df["dwell Time"],
            mode="lines+markers", name="Dwell Time",
            line=dict(color="#e07b39", width=2), marker=dict(size=5),
        ))
        fig4.add_hline(y=df["dwell Time"].mean(), line_dash="dash",
                       line_color="#6b7db3",
                       annotation_text=f"Avg: {df['dwell Time'].mean():.1f} min")
        fig4.update_layout(title="Daily Dwell Time (minutes)", yaxis_title="Minutes", **PLOTLY_LAYOUT)
        st.plotly_chart(fig4, use_container_width=True)

# ============================================================
#  SECTION 5 — ALL METRICS COMBINED
# ============================================================
st.markdown('<div class="section-header">All Metrics Combined — Full Overview</div>', unsafe_allow_html=True)

fig5 = go.Figure()
all_metrics = [
    (data["foot_traffic"],    "foot Traffic",    color,     "Foot Traffic"),
    (data["repeat_visits"],   "repeat Visits",   "#1d9e75", "Repeat Visits"),
    (data["dwell_time"],      "dwell Time",      "#e07b39", "Dwell Time (min)"),
    (data["redemption_rate"], "redemption Rate", "#3b82f6", "Redemption Rate (%)"),
]
for df, col_name, clr, label in all_metrics:
    if df is not None:
        fig5.add_trace(go.Scatter(
            x=df["Date"], y=df[col_name],
            mode="lines", name=label,
            line=dict(color=clr, width=2),
        ))
fig5.update_layout(
    title=f"{selected_biz} — All Metrics Over Time",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    **PLOTLY_LAYOUT,
)
st.plotly_chart(fig5, use_container_width=True)

# ============================================================
#  SECTION 6 — DAY OF WEEK PATTERNS
# ============================================================
st.markdown('<div class="section-header">Day of Week Patterns</div>', unsafe_allow_html=True)

day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
col_d1, col_d2 = st.columns(2)

with col_d1:
    df = data["foot_traffic"]
    if df is not None:
        df = df.copy()
        df["day"] = df["Date"].dt.day_name()
        dow = df.groupby("day")["foot Traffic"].mean().reindex(day_order).reset_index()
        fig6 = go.Figure(go.Bar(
            x=dow["day"], y=dow["foot Traffic"].round(1),
            marker_color=color, opacity=0.85,
        ))
        fig6.update_layout(title="Avg Foot Traffic by Day of Week", **PLOTLY_LAYOUT)
        st.plotly_chart(fig6, use_container_width=True)

with col_d2:
    df = data["redemption_rate"]
    if df is not None:
        df = df.copy()
        df["day"] = df["Date"].dt.day_name()
        dow = df.groupby("day")["redemption Rate"].mean().reindex(day_order).reset_index()
        fig7 = go.Figure(go.Bar(
            x=dow["day"], y=dow["redemption Rate"].round(1),
            marker_color="#1d9e75", opacity=0.85,
        ))
        fig7.update_layout(title="Avg Redemption Rate by Day of Week", **PLOTLY_LAYOUT)
        st.plotly_chart(fig7, use_container_width=True)

# ============================================================
#  FOOTER
# ============================================================
st.markdown("---")
st.caption("WayLucid Capstone Dashboard · CIS 450 Data Analytics · ASU · Built with Streamlit")
