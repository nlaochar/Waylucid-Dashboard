import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta
import os

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
    p, label, .stMarkdown { color: #a0a0c0 !important; }
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
    .filter-note {
        background: #1a1a35; border: 0.5px solid #3a3a6a;
        border-radius: 8px; padding: 8px 12px;
        font-size: 11px; color: #7b7baa; margin-bottom: 8px;
    }
    div[data-testid="metric-container"] {
        background: #161628; border: 0.5px solid #2a2a4a;
        border-radius: 12px; padding: 12px 16px;
    }
    div[data-testid="metric-container"] label { color: #6b7db3 !important; }
    div[data-testid="metric-container"] div { color: #e0e0f0 !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
#  PILOT DATE RANGE — common across all businesses
#  Mar 19 is the first date all 4 businesses have data
#  Apr 17 is the latest download date
# ============================================================
PILOT_MIN = date(2026, 3, 19)
PILOT_MAX = date(2026, 4, 17)

# ============================================================
#  BUSINESS & FILE CONFIG
# ============================================================
BUSINESSES = {
    "NOLA Boards": {
        "color":           "#7c3aed",
        "foot_traffic":    "pilot-nola-footTraffic-2026-04-17.csv",
        "repeat_visits":   "pilot-nola-repeatVisits-2026-04-17.csv",
        "dwell_time":      "pilot-nola-dwellTime-2026-04-17.csv",
        "redemption_rate": "pilot-nola-redemptionRate-2026-04-12.csv",
        "social_pulse":    "social-pulse-nola-boards (2).csv",
    },
    "Lower Coast Coffee": {
        "color":           "#1d9e75",
        "foot_traffic":    "pilot-lcc-footTraffic-2026-04-17.csv",
        "repeat_visits":   "pilot-lcc-repeatVisits-2026-04-17.csv",
        "dwell_time":      "pilot-lcc-dwellTime-2026-04-17.csv",
        "redemption_rate": "pilot-lcc-redemptionRate-2026-04-17.csv",
        "social_pulse":    "social-pulse-lower-coast-coffee (1).csv",
    },
    "AZ Chimney Cakes": {
        "color":           "#e07b39",
        "foot_traffic":    "pilot-azcc-footTraffic-2026-04-17.csv",
        "repeat_visits":   "pilot-azcc-repeatVisits-2026-04-17.csv",
        "dwell_time":      "pilot-azcc-dwellTime-2026-04-17.csv",
        "redemption_rate": "pilot-azcc-redemptionRate-2026-04-17.csv",
        "social_pulse":    "social-pulse-az-chimney-cakes (1).csv",
    },
    "City of El Mirage": {
        "color":           "#3b82f6",
        "foot_traffic":    "pilot-elmirage-footTraffic-2026-04-17.csv",
        "repeat_visits":   "pilot-elmirage-repeatVisits-2026-04-17.csv",
        "dwell_time":      "pilot-elmirage-dwellTime-2026-04-17.csv",
        "redemption_rate": None,
        "social_pulse":    "social-pulse-el-mirage (1).csv",
    },
}

BIZ_COLORS = {b: BUSINESSES[b]["color"] for b in BUSINESSES}

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
    if not filename or not os.path.exists(filename):
        return None
    df = pd.read_csv(filename)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df

def load_business(biz):
    return {k: load_csv(v) for k, v in BUSINESSES[biz].items() if k != "color"}

def filter_df(df, start, end):
    if df is None or "Date" not in df.columns:
        return df
    return df[
        (df["Date"] >= pd.Timestamp(start)) &
        (df["Date"] <= pd.Timestamp(end))
    ].copy()

def metric_card(label, value, sub=None):
    sub_html = f'<div class="metric-sub">{sub}</div>' if sub else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {sub_html}
    </div>""", unsafe_allow_html=True)

def line_chart(df, col, color, title, ytitle, fill_rgba):
    if df is None or df.empty:
        st.info(f"No {title} data for selected range.")
        return
    avg = df[col].mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df[col],
        mode="lines+markers", name=title,
        line=dict(color=color, width=2), marker=dict(size=5),
        fill="tozeroy", fillcolor=fill_rgba,
    ))
    fig.add_hline(y=avg, line_dash="dash", line_color="#6b7db3",
                  annotation_text=f"Avg: {avg:.1f}")
    fig.update_layout(title=title, yaxis_title=ytitle, **PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

def bar_chart(df, col, color, title, ytitle):
    if df is None or df.empty:
        st.info(f"No {title} data for selected range.")
        return
    fig = go.Figure(go.Bar(
        x=df["Date"], y=df[col],
        marker_color=color, opacity=0.85))
    fig.update_layout(title=title, yaxis_title=ytitle, **PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

def dow_chart(df, col, color, title):
    if df is None or df.empty:
        return
    day_order = ["Monday","Tuesday","Wednesday","Thursday",
                 "Friday","Saturday","Sunday"]
    d = df.copy()
    d["day"] = d["Date"].dt.day_name()
    dow = d.groupby("day")[col].mean().reindex(day_order).reset_index()
    fig = go.Figure(go.Bar(
        x=dow["day"], y=dow[col].round(1),
        marker_color=color, opacity=0.85))
    fig.update_layout(title=title, **PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
#  SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## 🌐 WayLucid")
    st.markdown("**Capstone Analytics Dashboard**")
    st.markdown("*CIS 450 — ASU*")
    st.markdown("---")

    selected_biz = st.selectbox("Select Business", list(BUSINESSES.keys()))
    color = BUSINESSES[selected_biz]["color"]
    data  = load_business(selected_biz)

    st.markdown("---")
    st.markdown("### 📅 Date Range Filter")
    st.caption("Filters pilot data charts only.")

    date_range = st.date_input(
        "Select date range",
        value=(PILOT_MIN, PILOT_MAX),
        min_value=PILOT_MIN,
        max_value=PILOT_MAX,
        label_visibility="collapsed",
    )
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = PILOT_MIN, PILOT_MAX

    st.markdown("**Quick select:**")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("7 days",   use_container_width=True):
            start_date = PILOT_MAX - timedelta(days=6)
            end_date   = PILOT_MAX
        if st.button("30 days",  use_container_width=True):
            start_date = PILOT_MAX - timedelta(days=29)
            end_date   = PILOT_MAX
    with c2:
        if st.button("14 days",  use_container_width=True):
            start_date = PILOT_MAX - timedelta(days=13)
            end_date   = PILOT_MAX
        if st.button("All data", use_container_width=True):
            start_date = PILOT_MIN
            end_date   = PILOT_MAX

    days_selected = (pd.Timestamp(end_date) - pd.Timestamp(start_date)).days + 1
    st.markdown(f"""
    <div class="filter-note">
        <strong style="color:#a78bfa">{days_selected} days selected</strong><br>
        {start_date.strftime("%b %d")} → {end_date.strftime("%b %d, %Y")}
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Pilot data: Mar 19 – Apr 17, 2026")
    st.caption("Social data: Feb 10 – Apr 7, 2026")

# ============================================================
#  APPLY DATE FILTER
# ============================================================
f = {k: filter_df(df, start_date, end_date) for k, df in data.items()}

# ============================================================
#  HEADER
# ============================================================
st.markdown(f"# 📊 {selected_biz} — Analytics Dashboard")
st.markdown(
    f"Showing **{start_date.strftime('%b %d')} → "
    f"{end_date.strftime('%b %d, %Y')}** &nbsp;·&nbsp; {days_selected} days"
)
st.markdown("---")

# ============================================================
#  SECTION 1 — KPI CARDS
# ============================================================
st.markdown('<div class="section-header">Key Performance Indicators</div>',
            unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)

with k1:
    df = f["foot_traffic"]
    if df is not None and not df.empty:
        metric_card("Avg Daily Foot Traffic",
                    round(df["foot Traffic"].mean(), 1),
                    f"Peak: {round(df['foot Traffic'].max(), 1)}")
    else:
        metric_card("Avg Daily Foot Traffic", "N/A",
                    "File missing from GitHub")

with k2:
    df = f["repeat_visits"]
    if df is not None and not df.empty:
        metric_card("Avg Repeat Visits",
                    round(df["repeat Visits"].mean(), 1),
                    f"Peak: {round(df['repeat Visits'].max(), 1)}")
    else:
        metric_card("Avg Repeat Visits", "N/A",
                    "File missing from GitHub")

with k3:
    df = f["dwell_time"]
    if df is not None and not df.empty:
        metric_card("Avg Dwell Time (min)",
                    round(df["dwell Time"].mean(), 1),
                    f"Peak: {round(df['dwell Time'].max(), 1)} min")
    else:
        metric_card("Avg Dwell Time", "N/A",
                    "File missing from GitHub")

with k4:
    df = f["redemption_rate"]
    if df is not None and not df.empty:
        metric_card("Avg Redemption Rate (%)",
                    round(df["redemption Rate"].mean(), 1),
                    f"Peak: {round(df['redemption Rate'].max(), 1)}%")
    else:
        metric_card("Avg Redemption Rate", "N/A",
                    "Not available for this business")

# ============================================================
#  SECTION 2 — SOCIAL PULSE
# ============================================================
st.markdown(
    '<div class="section-header">Social Pulse — Google · Yelp · Instagram · TikTok</div>',
    unsafe_allow_html=True)

df_social = data["social_pulse"]
if df_social is not None and not df_social.empty:
    latest = df_social.sort_values("Date").groupby("Platform").last().reset_index()
    google = latest[latest["Platform"] == "google"]
    yelp   = latest[latest["Platform"] == "yelp"]
    insta  = latest[latest["Platform"] == "instagram"]
    tiktok = latest[latest["Platform"] == "tiktok"]

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        if not google.empty:
            rev = int(google["Review Count"].iloc[0]) \
                  if pd.notna(google["Review Count"].iloc[0]) else "—"
            metric_card("Google Rating",
                        f"⭐ {google['Rating'].iloc[0]}", f"{rev} reviews")
    with s2:
        if not yelp.empty:
            rev = int(yelp["Review Count"].iloc[0]) \
                  if pd.notna(yelp["Review Count"].iloc[0]) else "—"
            metric_card("Yelp Rating",
                        f"⭐ {yelp['Rating'].iloc[0]}", f"{rev} reviews")
    with s3:
        if not insta.empty and pd.notna(insta["Follower Count"].iloc[0]):
            posts = int(insta["Post Count"].iloc[0]) \
                    if pd.notna(insta["Post Count"].iloc[0]) else "—"
            metric_card("Instagram Followers",
                        f"{int(insta['Follower Count'].iloc[0]):,}",
                        f"{posts} posts")
    with s4:
        if not tiktok.empty and pd.notna(tiktok["Follower Count"].iloc[0]):
            posts = int(tiktok["Post Count"].iloc[0]) \
                    if pd.notna(tiktok["Post Count"].iloc[0]) else "—"
            metric_card("TikTok Followers",
                        f"{int(tiktok['Follower Count'].iloc[0]):,}",
                        f"{posts} posts")

    st.markdown("##### Follower Growth Over Time")
    fig_s = go.Figure()
    for platform, clr in [("instagram", "#e1306c"), ("tiktok", "#69c9d0")]:
        pf = df_social[df_social["Platform"] == platform].sort_values("Date")
        if not pf.empty and pf["Follower Count"].notna().any():
            fig_s.add_trace(go.Scatter(
                x=pf["Date"], y=pf["Follower Count"],
                mode="lines+markers", name=platform.title(),
                line=dict(color=clr, width=2), marker=dict(size=5),
            ))
    fig_s.update_layout(
        title="Instagram & TikTok Follower Growth", **PLOTLY_LAYOUT)
    st.plotly_chart(fig_s, use_container_width=True)
else:
    st.info("No social pulse data available for this business.")

# ============================================================
#  SECTION 3 — FOOT TRAFFIC & REDEMPTION RATE
# ============================================================
st.markdown(
    '<div class="section-header">Foot Traffic & Redemption Rate — Trend</div>',
    unsafe_allow_html=True)
col_l, col_r = st.columns(2)
with col_l:
    line_chart(f["foot_traffic"], "foot Traffic", color,
               "Daily Foot Traffic", "Score", "rgba(124,58,237,0.08)")
with col_r:
    line_chart(f["redemption_rate"], "redemption Rate", "#1d9e75",
               "Daily Redemption Rate (%)", "%", "rgba(29,158,117,0.08)")

# ============================================================
#  SECTION 4 — REPEAT VISITS & DWELL TIME
# ============================================================
st.markdown('<div class="section-header">Repeat Visits & Dwell Time</div>',
            unsafe_allow_html=True)
col_a, col_b = st.columns(2)
with col_a:
    bar_chart(f["repeat_visits"], "repeat Visits", color,
              "Daily Repeat Visits", "Visits")
with col_b:
    line_chart(f["dwell_time"], "dwell Time", "#e07b39",
               "Daily Dwell Time (minutes)", "Minutes",
               "rgba(224,123,57,0.08)")

# ============================================================
#  SECTION 5 — ALL METRICS COMBINED
# ============================================================
st.markdown('<div class="section-header">All Pilot Metrics Combined</div>',
            unsafe_allow_html=True)
fig_all = go.Figure()
for df, col_name, clr, label in [
    (f["foot_traffic"],    "foot Traffic",    color,     "Foot Traffic"),
    (f["repeat_visits"],   "repeat Visits",   "#1d9e75", "Repeat Visits"),
    (f["dwell_time"],      "dwell Time",      "#e07b39", "Dwell Time (min)"),
    (f["redemption_rate"], "redemption Rate", "#3b82f6", "Redemption Rate (%)"),
]:
    if df is not None and not df.empty:
        fig_all.add_trace(go.Scatter(
            x=df["Date"], y=df[col_name],
            mode="lines", name=label,
            line=dict(color=clr, width=2),
        ))
fig_all.update_layout(
    title=f"{selected_biz} — All Metrics Over Time",
    legend=dict(orientation="h", yanchor="bottom", y=1.02,
                xanchor="right", x=1),
    **PLOTLY_LAYOUT,
)
st.plotly_chart(fig_all, use_container_width=True)

# ============================================================
#  SECTION 6 — DAY OF WEEK PATTERNS
# ============================================================
st.markdown('<div class="section-header">Day of Week Patterns</div>',
            unsafe_allow_html=True)
col_d1, col_d2 = st.columns(2)
with col_d1:
    dow_chart(f["foot_traffic"], "foot Traffic", color,
              "Avg Foot Traffic by Day of Week")
with col_d2:
    dow_chart(f["redemption_rate"], "redemption Rate", "#1d9e75",
              "Avg Redemption Rate by Day of Week")
col_d3, col_d4 = st.columns(2)
with col_d3:
    dow_chart(f["repeat_visits"], "repeat Visits", "#e07b39",
              "Avg Repeat Visits by Day of Week")
with col_d4:
    dow_chart(f["dwell_time"], "dwell Time", "#3b82f6",
              "Avg Dwell Time by Day of Week")

# ============================================================
#  SECTION 7 — CROSS-BUSINESS COMPARISON
# ============================================================
st.markdown(
    '<div class="section-header">Cross-Business Comparison — All 4 Businesses</div>',
    unsafe_allow_html=True)
st.caption("Averages across all businesses for the selected date range.")

biz_names = []
ft_avgs   = []
rv_avgs   = []
dt_avgs   = []
rr_avgs   = []

for biz in BUSINESSES:
    bd = load_business(biz)
    bf = {k: filter_df(df, start_date, end_date) for k, df in bd.items()}
    biz_names.append(biz)

    ft = bf.get("foot_traffic")
    ft_avgs.append(round(ft["foot Traffic"].mean(), 1)
                   if ft is not None and not ft.empty else 0)

    rv = bf.get("repeat_visits")
    rv_avgs.append(round(rv["repeat Visits"].mean(), 1)
                   if rv is not None and not rv.empty else 0)

    dt = bf.get("dwell_time")
    dt_avgs.append(round(dt["dwell Time"].mean(), 1)
                   if dt is not None and not dt.empty else 0)

    rr = bf.get("redemption_rate")
    rr_avgs.append(round(rr["redemption Rate"].mean(), 1)
                   if rr is not None and not rr.empty else 0)

comp_colors = [BIZ_COLORS[b] for b in biz_names]

cc1, cc2 = st.columns(2)
with cc1:
    fig_c1 = go.Figure(go.Bar(
        x=biz_names, y=ft_avgs,
        marker_color=comp_colors, opacity=0.85))
    fig_c1.update_layout(
        title="Avg Foot Traffic — All Businesses", **PLOTLY_LAYOUT)
    st.plotly_chart(fig_c1, use_container_width=True)
with cc2:
    fig_c2 = go.Figure(go.Bar(
        x=biz_names, y=rr_avgs,
        marker_color=comp_colors, opacity=0.85))
    fig_c2.update_layout(
        title="Avg Redemption Rate — All Businesses", **PLOTLY_LAYOUT)
    st.plotly_chart(fig_c2, use_container_width=True)

cc3, cc4 = st.columns(2)
with cc3:
    fig_c3 = go.Figure(go.Bar(
        x=biz_names, y=rv_avgs,
        marker_color=comp_colors, opacity=0.85))
    fig_c3.update_layout(
        title="Avg Repeat Visits — All Businesses", **PLOTLY_LAYOUT)
    st.plotly_chart(fig_c3, use_container_width=True)
with cc4:
    fig_c4 = go.Figure(go.Bar(
        x=biz_names, y=dt_avgs,
        marker_color=comp_colors, opacity=0.85))
    fig_c4.update_layout(
        title="Avg Dwell Time — All Businesses", **PLOTLY_LAYOUT)
    st.plotly_chart(fig_c4, use_container_width=True)

# ============================================================
#  FOOTER
# ============================================================
st.markdown("---")
st.caption(
    "WayLucid Capstone Dashboard · CIS 450 Data Analytics · "
    "ASU · Built with Streamlit")
