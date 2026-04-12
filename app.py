import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ============================================================
#  COLUMN CONFIG — EDIT THESE TO MATCH YOUR CSV HEADERS
# ============================================================
# Open each CSV and check the exact column names at the top.
# Replace the values below with your actual column names.

COL = {
    # --- Foot Traffic ---
    "date":           "date",           # e.g. "2025-03-01"
    "transactions":   "transactions",   # number of cafe transactions
    "day_of_week":    "day_of_week",    # e.g. "Monday"
    "pilot_participants": "pilot_participants",  # number of geocaching participants

    # --- Social Media ---
    "likes":          "likes",
    "shares":         "shares",
    "bookmarks":      "bookmarks",
    "hour":           "hour",           # 0–23 integer

    # --- Rewards / Pilot ---
    "merch_revenue":  "merch_revenue",
    "prev_members":   "prev_members",   # previously rewards members
    "new_members":    "new_members",    # joined rewards during pilot

    # --- Social Pulse (Yelp / Google / Instagram) ---
    "google_reviews": "google_reviews",
    "google_rating":  "google_rating",
    "yelp_reviews":   "yelp_reviews",
    "yelp_rating":    "yelp_rating",
    "instagram_followers": "instagram_followers",
}

# ============================================================
#  FILE PATHS — point these to your actual CSV files
# ============================================================
DATA_FILES = {
    "NOLA Boards":       "data/nola_boards.csv",
    "Lower Coast Coffee":"data/lower_coast_coffee.csv",
    "AZ Chimney Cakes":  "data/az_chimney_cakes.csv",
    "City of El Mirage": "data/el_mirage.csv",
}

BRAND_COLORS = {
    "NOLA Boards":       "#7c3aed",
    "Lower Coast Coffee":"#1d9e75",
    "AZ Chimney Cakes":  "#e07b39",
    "City of El Mirage": "#3b82f6",
}

# ============================================================
#  PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="WayLucid Capstone Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
#  STYLING
# ============================================================
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #0d0d1a; }
    [data-testid="stSidebar"] { background: #11112a; border-right: 1px solid #2a2a4a; }
    h1, h2, h3, h4 { color: #e0e0f0 !important; }
    p, label, .stMarkdown { color: #a0a0c0 !important; }
    .metric-card {
        background: #161628;
        border: 0.5px solid #2a2a4a;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
    .metric-label { font-size: 12px; color: #6b7db3; margin-bottom: 4px; }
    .metric-value { font-size: 28px; font-weight: 600; color: #e0e0f0; }
    .metric-delta-up { font-size: 12px; color: #34d399; }
    .metric-delta-down { font-size: 12px; color: #f87171; }
    .section-header {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #6b7db3 !important;
        margin: 24px 0 12px 0;
        border-bottom: 0.5px solid #2a2a4a;
        padding-bottom: 6px;
    }
    .stPlotlyChart { border-radius: 12px; }
    div[data-testid="metric-container"] {
        background: #161628;
        border: 0.5px solid #2a2a4a;
        border-radius: 12px;
        padding: 12px 16px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
#  HELPERS
# ============================================================
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#11112a",
    font_color="#a0a0c0",
    font_size=12,
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis=dict(gridcolor="#1e1e38", linecolor="#2a2a4a"),
    yaxis=dict(gridcolor="#1e1e38", linecolor="#2a2a4a"),
)

@st.cache_data
def load_data(path):
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    # Try to parse date column
    if COL["date"] in df.columns:
        df[COL["date"]] = pd.to_datetime(df[COL["date"]], errors="coerce")
    return df

def safe_col(df, col_key):
    """Return column if it exists, else None."""
    name = COL.get(col_key)
    return name if (df is not None and name in df.columns) else None

def metric_card(label, value, delta=None, delta_up=True):
    delta_html = ""
    if delta:
        cls = "metric-delta-up" if delta_up else "metric-delta-down"
        arrow = "▲" if delta_up else "▼"
        delta_html = f'<div class="{cls}">{arrow} {delta}</div>'
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>""", unsafe_allow_html=True)

# ============================================================
#  SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## 🌐 WayLucid")
    st.markdown("**Capstone Analytics Dashboard**")
    st.markdown("---")
    view_mode = st.radio("View", ["Single Business", "Compare All"])
    if view_mode == "Single Business":
        selected_biz = st.selectbox("Select Business", list(DATA_FILES.keys()))
        businesses_to_show = [selected_biz]
    else:
        businesses_to_show = list(DATA_FILES.keys())
    st.markdown("---")
    st.caption("Data source: WayLucid platform")
    st.caption("Refreshed: Apr 7, 2026")

# ============================================================
#  LOAD DATA
# ============================================================
all_data = {biz: load_data(path) for biz, path in DATA_FILES.items()}

# ============================================================
#  HEADER
# ============================================================
st.markdown(f"# 📊 WayLucid Capstone Dashboard")
st.markdown(f"Analyzing: **{' · '.join(businesses_to_show)}**")
st.markdown("---")

# ============================================================
#  SECTION 1 — KPI OVERVIEW
# ============================================================
st.markdown('<div class="section-header">Key Performance Indicators</div>', unsafe_allow_html=True)

kpi_cols = st.columns(len(businesses_to_show))
for i, biz in enumerate(businesses_to_show):
    df = all_data[biz]
    with kpi_cols[i]:
        st.markdown(f"**{biz}**")
        if df is not None:
            # Foot traffic
            if safe_col(df, "transactions"):
                total_tx = int(df[COL["transactions"]].sum())
                max_tx = int(df[COL["transactions"]].max())
                metric_card("Total Transactions", f"{total_tx:,}", f"Peak: {max_tx}")
            # Revenue
            if safe_col(df, "merch_revenue"):
                total_rev = df[COL["merch_revenue"]].sum()
                metric_card("Merch Revenue", f"${total_rev:,.2f}")
            # New members
            if safe_col(df, "new_members"):
                total_new = int(df[COL["new_members"]].sum())
                metric_card("New Rewards Members", str(total_new))
            # Instagram followers
            if safe_col(df, "instagram_followers"):
                followers = int(df[COL["instagram_followers"]].max())
                metric_card("Instagram Followers", f"{followers:,}")
            # Google rating
            if safe_col(df, "google_rating"):
                rating = round(df[COL["google_rating"]].iloc[-1], 1)
                metric_card("Google Rating", f"⭐ {rating}")
        else:
            st.warning(f"No data file found for {biz}.\nCheck your file path in DATA_FILES.")

# ============================================================
#  SECTION 2 — SOCIAL PULSE
# ============================================================
st.markdown('<div class="section-header">Social Pulse — Yelp · Google · Instagram</div>', unsafe_allow_html=True)

for biz in businesses_to_show:
    df = all_data[biz]
    if df is None:
        continue
    has_social = any(safe_col(df, k) for k in ["google_rating", "yelp_rating", "instagram_followers"])
    if not has_social:
        continue

    st.markdown(f"#### {biz}")
    cols = st.columns(4)
    with cols[0]:
        if safe_col(df, "google_rating"):
            st.metric("Google Rating", f"⭐ {df[COL['google_rating']].iloc[-1]:.1f}")
    with cols[1]:
        if safe_col(df, "google_reviews"):
            st.metric("Google Reviews", int(df[COL["google_reviews"]].iloc[-1]))
    with cols[2]:
        if safe_col(df, "yelp_rating"):
            st.metric("Yelp Rating", f"⭐ {df[COL['yelp_rating']].iloc[-1]:.1f}")
    with cols[3]:
        if safe_col(df, "instagram_followers"):
            st.metric("Instagram Followers", f"{int(df[COL['instagram_followers']].iloc[-1]):,}")

# ============================================================
#  SECTION 3 — FOOT TRAFFIC
# ============================================================
st.markdown('<div class="section-header">Foot Traffic Analysis</div>', unsafe_allow_html=True)

col_left, col_right = st.columns(2)

with col_left:
    # Transactions over time
    fig = go.Figure()
    for biz in businesses_to_show:
        df = all_data[biz]
        if df is None or not safe_col(df, "transactions") or not safe_col(df, "date"):
            continue
        daily = df.groupby(COL["date"])[COL["transactions"]].sum().reset_index()
        fig.add_trace(go.Scatter(
            x=daily[COL["date"]], y=daily[COL["transactions"]],
            name=biz, mode="lines",
            line=dict(color=BRAND_COLORS[biz], width=2),
        ))
    fig.update_layout(title="Daily Transactions Over Time", **PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    # Transactions by day of week
    fig2 = go.Figure()
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    for biz in businesses_to_show:
        df = all_data[biz]
        if df is None or not safe_col(df, "transactions"):
            continue
        # Use day_of_week column if available, else derive from date
        if safe_col(df, "day_of_week"):
            dow = df.groupby(COL["day_of_week"])[COL["transactions"]].sum().reindex(day_order).reset_index()
        elif safe_col(df, "date"):
            df["_dow"] = df[COL["date"]].dt.day_name()
            dow = df.groupby("_dow")[COL["transactions"]].sum().reindex(day_order).reset_index()
            dow.columns = [COL["day_of_week"], COL["transactions"]]
        else:
            continue
        fig2.add_trace(go.Bar(
            x=dow.iloc[:,0], y=dow[COL["transactions"]],
            name=biz, marker_color=BRAND_COLORS[biz],
        ))
    fig2.update_layout(title="Transactions by Day of Week", barmode="group", **PLOTLY_LAYOUT)
    st.plotly_chart(fig2, use_container_width=True)

# Monthly foot traffic
st.markdown("##### Monthly Foot Traffic Breakdown")
fig3 = go.Figure()
for biz in businesses_to_show:
    df = all_data[biz]
    if df is None or not safe_col(df, "date") or not safe_col(df, "transactions"):
        continue
    df["_month"] = df[COL["date"]].dt.to_period("M").astype(str)
    monthly = df.groupby("_month")[COL["transactions"]].sum().reset_index()
    fig3.add_trace(go.Bar(
        x=monthly["_month"], y=monthly[COL["transactions"]],
        name=biz, marker_color=BRAND_COLORS[biz],
    ))
fig3.update_layout(title="Monthly Transactions", barmode="group", **PLOTLY_LAYOUT)
st.plotly_chart(fig3, use_container_width=True)

# ============================================================
#  SECTION 4 — SOCIAL MEDIA ENGAGEMENT
# ============================================================
st.markdown('<div class="section-header">Social Media Engagement</div>', unsafe_allow_html=True)

col_l, col_r = st.columns(2)

with col_l:
    # Engagement by day of week
    fig4 = go.Figure()
    for biz in businesses_to_show:
        df = all_data[biz]
        if df is None or not safe_col(df, "likes"):
            continue
        if safe_col(df, "day_of_week"):
            dow_col = COL["day_of_week"]
        elif safe_col(df, "date"):
            df["_dow"] = df[COL["date"]].dt.day_name()
            dow_col = "_dow"
        else:
            continue
        for metric, color in [("likes","#60a5fa"),("shares","#f87171"),("bookmarks","#34d399")]:
            if safe_col(df, metric):
                grp = df.groupby(dow_col)[COL[metric]].sum().reindex(day_order).reset_index()
                fig4.add_trace(go.Bar(
                    x=grp.iloc[:,0], y=grp[COL[metric]],
                    name=f"{biz} — {metric.title()}",
                    marker_color=color,
                    visible=True if biz == businesses_to_show[0] else "legendonly",
                ))
    fig4.update_layout(title="Engagement by Day of Week", barmode="stack", **PLOTLY_LAYOUT)
    st.plotly_chart(fig4, use_container_width=True)

with col_r:
    # Hourly engagement
    fig5 = go.Figure()
    for biz in businesses_to_show:
        df = all_data[biz]
        if df is None or not safe_col(df, "likes") or not safe_col(df, "hour"):
            continue
        hourly = df.groupby(COL["hour"])[COL["likes"]].sum().reset_index()
        fig5.add_trace(go.Scatter(
            x=hourly[COL["hour"]], y=hourly[COL["likes"]],
            name=biz, mode="lines+markers",
            line=dict(color=BRAND_COLORS[biz], width=2),
        ))
    fig5.update_layout(
        title="Hourly Likes Trend",
        xaxis_title="Hour of Day (24h)",
        **PLOTLY_LAYOUT
    )
    st.plotly_chart(fig5, use_container_width=True)

# ============================================================
#  SECTION 5 — REWARDS & PILOT METRICS
# ============================================================
st.markdown('<div class="section-header">Rewards Program & Pilot Metrics</div>', unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    fig6 = go.Figure()
    for biz in businesses_to_show:
        df = all_data[biz]
        if df is None or not safe_col(df, "merch_revenue") or not safe_col(df, "date"):
            continue
        daily_rev = df.groupby(COL["date"])[COL["merch_revenue"]].sum().reset_index()
        fig6.add_trace(go.Scatter(
            x=daily_rev[COL["date"]], y=daily_rev[COL["merch_revenue"]],
            name=biz, mode="lines+markers",
            line=dict(color=BRAND_COLORS[biz], width=2),
        ))
        mean_rev = daily_rev[COL["merch_revenue"]].mean()
        fig6.add_hline(y=mean_rev, line_dash="dash",
                       line_color=BRAND_COLORS[biz], opacity=0.5,
                       annotation_text=f"{biz} mean: ${mean_rev:.0f}")
    fig6.update_layout(title="Merch Revenue Over Time", **PLOTLY_LAYOUT)
    st.plotly_chart(fig6, use_container_width=True)

with col_b:
    # New vs previous rewards members
    biz_labels, prev_vals, new_vals = [], [], []
    for biz in businesses_to_show:
        df = all_data[biz]
        if df is None:
            continue
        biz_labels.append(biz)
        prev_vals.append(int(df[COL["prev_members"]].sum()) if safe_col(df, "prev_members") else 0)
        new_vals.append(int(df[COL["new_members"]].sum()) if safe_col(df, "new_members") else 0)

    fig7 = go.Figure(data=[
        go.Bar(name="Previous Members", x=biz_labels, y=prev_vals, marker_color="#5b21b6"),
        go.Bar(name="New Members (Pilot)", x=biz_labels, y=new_vals, marker_color="#1d9e75"),
    ])
    fig7.update_layout(title="Rewards Members: Previous vs New", barmode="group", **PLOTLY_LAYOUT)
    st.plotly_chart(fig7, use_container_width=True)

# ============================================================
#  SECTION 6 — CORRELATION MATRIX
# ============================================================
st.markdown('<div class="section-header">Correlation Analysis — Social vs Pilot</div>', unsafe_allow_html=True)

for biz in businesses_to_show:
    df = all_data[biz]
    if df is None:
        continue
    corr_cols = [COL[k] for k in ["likes","shares","bookmarks","pilot_participants"]
                 if safe_col(df, k)]
    if len(corr_cols) < 2:
        continue
    corr = df[corr_cols].corr().round(2)
    fig8 = go.Figure(go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.index.tolist(),
        colorscale="RdBu",
        zmin=-1, zmax=1,
        text=corr.values,
        texttemplate="%{text}",
        showscale=True,
    ))
    fig8.update_layout(title=f"Correlation Matrix — {biz}", **PLOTLY_LAYOUT)
    st.plotly_chart(fig8, use_container_width=True)

# ============================================================
#  SECTION 7 — PILOT: FOOT TRAFFIC vs PARTICIPANTS
# ============================================================
st.markdown('<div class="section-header">Pilot Participants vs Cafe Transactions</div>', unsafe_allow_html=True)

fig9 = make_subplots(specs=[[{"secondary_y": True}]])
for biz in businesses_to_show:
    df = all_data[biz]
    if df is None or not safe_col(df, "date") or not safe_col(df, "transactions"):
        continue
    daily = df.groupby(COL["date"])[COL["transactions"]].sum().reset_index()
    fig9.add_trace(go.Scatter(
        x=daily[COL["date"]], y=daily[COL["transactions"]],
        name=f"{biz} — Transactions",
        line=dict(color=BRAND_COLORS[biz], width=2),
    ), secondary_y=False)
    if safe_col(df, "pilot_participants"):
        pilot = df.groupby(COL["date"])[COL["pilot_participants"]].sum().reset_index()
        fig9.add_trace(go.Scatter(
            x=pilot[COL["date"]], y=pilot[COL["pilot_participants"]],
            name=f"{biz} — Pilot Participants",
            line=dict(color=BRAND_COLORS[biz], width=1, dash="dot"),
        ), secondary_y=True)
fig9.update_layout(title="Daily Cafe Foot Traffic vs Pilot Participants", **PLOTLY_LAYOUT)
fig9.update_yaxes(title_text="Cafe Transactions", secondary_y=False)
fig9.update_yaxes(title_text="Pilot Participants", secondary_y=True)
st.plotly_chart(fig9, use_container_width=True)

# ============================================================
#  FOOTER
# ============================================================
st.markdown("---")
st.caption("WayLucid Capstone Dashboard · CIS 450 Data Analytics · ASU · Data refreshed Apr 7, 2026")
