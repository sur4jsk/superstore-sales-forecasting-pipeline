#streamlit

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Superstore Sales Forecasting",
    page_icon="📊",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
    <style>
    .main { background-color: #F0F8FF; }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00B4D8;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    h1 { color: #0D1F3C !important; }
    h2, h3 { color: #0096C7 !important; }
    </style>
""", unsafe_allow_html=True)

# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    clean    = pd.read_csv('data/processed/superstore_clean.csv',
                           parse_dates=['order_date'])
    combined = pd.read_csv('output/combined_for_powerbi.csv',
                           parse_dates=['date'])
    region   = pd.read_csv('output/region_summary.csv')
    forecast = pd.read_csv('data/processed/forecast_60day.csv',
                           parse_dates=['date'])
    hist     = pd.read_csv('data/processed/historical_window.csv',
                           parse_dates=['date'])
    return clean, combined, region, forecast, hist

clean, combined, region, forecast, hist = load_data()

# ════════════════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════════════════
st.markdown("## 📊 Superstore Sales Forecasting Dashboard")
st.markdown("**End-to-end data engineering pipeline | Python · Pandas · Streamlit · Plotly**")
st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR — Filters
# ════════════════════════════════════════════════════════════════════════════
st.sidebar.image("https://img.icons8.com/color/96/combo-chart.png", width=60)
st.sidebar.title("🔧 Filters")

# Region filter
all_regions = sorted(clean['region'].unique())
selected_regions = st.sidebar.multiselect(
    "Select Region(s)",
    options=all_regions,
    default=all_regions
)

# Category filter
all_cats = sorted(clean['category'].unique())
selected_cats = st.sidebar.multiselect(
    "Select Category(s)",
    options=all_cats,
    default=all_cats
)

# Segment filter
all_segs = sorted(clean['segment'].unique())
selected_segs = st.sidebar.multiselect(
    "Select Segment(s)",
    options=all_segs,
    default=all_segs
)

# Year filter
all_years = sorted(clean['year'].unique())
selected_years = st.sidebar.multiselect(
    "Select Year(s)",
    options=all_years,
    default=all_years
)

st.sidebar.markdown("---")
st.sidebar.markdown("**📁 Project Links**")
st.sidebar.markdown("[GitHub Repository](https://github.com/sur4jsk/superstore-sales-forecasting-pipeline)")
st.sidebar.markdown("Built by **Vaisakh**")

# ── Apply filters ─────────────────────────────────────────────────────────────
filtered = clean[
    (clean['region'].isin(selected_regions)) &
    (clean['category'].isin(selected_cats)) &
    (clean['segment'].isin(selected_segs)) &
    (clean['year'].isin(selected_years))
]

# ════════════════════════════════════════════════════════════════════════════
# KPI METRICS ROW
# ════════════════════════════════════════════════════════════════════════════
st.markdown("### 📈 Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

total_sales   = filtered['sales'].sum()
total_orders  = filtered['order_id'].nunique()
avg_order     = filtered['sales'].mean()
top_category  = filtered.groupby('category')['sales'].sum().idxmax()
avg_ship_days = filtered['shipping_days'].mean()

col1.metric("💰 Total Revenue",    f"${total_sales:,.0f}")
col2.metric("📦 Total Orders",     f"{total_orders:,}")
col3.metric("🧾 Avg Order Value",  f"${avg_order:,.2f}")
col4.metric("🏆 Top Category",     top_category)
col5.metric("🚚 Avg Shipping",     f"{avg_ship_days:.1f} days")

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# ROW 1: Forecast Line Chart (full width)
# ════════════════════════════════════════════════════════════════════════════
st.markdown("### 📉 Revenue Trend: Rolling 6-Month History + 60-Day Forecast")

fig_line = go.Figure()

# Historical daily revenue
fig_line.add_trace(go.Scatter(
    x=hist['date'],
    y=hist['actual_revenue'],
    name='Daily Revenue',
    line=dict(color='#00B4D8', width=1),
    opacity=0.5,
    fill='tozeroy',
    fillcolor='rgba(0,180,216,0.08)'
))

# 7-day moving average
fig_line.add_trace(go.Scatter(
    x=hist['date'],
    y=hist['rolling_7d_avg'],
    name='7-Day Moving Avg',
    line=dict(color='#0D1F3C', width=2.5)
))

# 60-day forecast
fig_line.add_trace(go.Scatter(
    x=forecast['date'],
    y=forecast['forecast_revenue'],
    name='60-Day Forecast',
    line=dict(color='#FF9F1C', width=2.5, dash='dash')
))

# Divider line
fig_line.add_vline(
    x=hist['date'].max(),
    line_dash="dot",
    line_color="grey",
    annotation_text="Forecast starts →",
    annotation_font_color="#FF9F1C"
)

fig_line.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='#F0F8FF',
    height=380,
    legend=dict(orientation='h', yanchor='bottom', y=1.02),
    xaxis_title='Date',
    yaxis_title='Revenue (USD)',
    yaxis_tickprefix='$',
    margin=dict(l=10, r=10, t=30, b=10)
)
st.plotly_chart(fig_line, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# ROW 2: Category Bar + Region Donut
# ════════════════════════════════════════════════════════════════════════════
col_left, col_right = st.columns(2)

# ── Sales by Category ─────────────────────────────────────────────────────────
with col_left:
    st.markdown("### 🗂️ Sales by Category")
    cat_data = (filtered.groupby('category')['sales']
                .sum()
                .reset_index()
                .sort_values('sales', ascending=True))

    fig_bar = px.bar(
        cat_data,
        x='sales', y='category',
        orientation='h',
        color='category',
        color_discrete_sequence=['#0D1F3C', '#0096C7', '#00B4D8'],
        text=cat_data['sales'].apply(lambda x: f'${x:,.0f}')
    )
    fig_bar.update_traces(textposition='outside')
    fig_bar.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='#F0F8FF',
        showlegend=False,
        height=320,
        xaxis_tickprefix='$',
        margin=dict(l=10, r=60, t=10, b=10)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ── Sales by Region ───────────────────────────────────────────────────────────
with col_right:
    st.markdown("### 🌍 Sales by Region")
    region_data = (filtered.groupby('region')['sales']
                   .sum()
                   .reset_index())

    fig_donut = px.pie(
        region_data,
        values='sales',
        names='region',
        hole=0.5,
        color_discrete_sequence=['#0D1F3C', '#0096C7', '#00B4D8', '#48CAE4']
    )
    fig_donut.update_traces(
        textposition='outside',
        textinfo='label+percent'
    )
    fig_donut.update_layout(
        paper_bgcolor='#F0F8FF',
        height=320,
        showlegend=True,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# ROW 3: Monthly Trend + Shipping Analysis
# ════════════════════════════════════════════════════════════════════════════
col3_left, col3_right = st.columns(2)

# ── Monthly Revenue Trend ─────────────────────────────────────────────────────
with col3_left:
    st.markdown("### 📅 Monthly Revenue Trend")
    monthly = (filtered.groupby(
                   filtered['order_date'].dt.to_period('M'))['sales']
               .sum()
               .reset_index())
    monthly['order_date'] = monthly['order_date'].dt.to_timestamp()
    monthly.columns = ['month', 'revenue']

    fig_monthly = px.line(
        monthly, x='month', y='revenue',
        markers=True,
        color_discrete_sequence=['#06D6A0']
    )
    fig_monthly.update_traces(line_width=2.5, marker_size=5)
    fig_monthly.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='#F0F8FF',
        height=300,
        xaxis_title='Month',
        yaxis_title='Revenue (USD)',
        yaxis_tickprefix='$',
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

# ── Sales by Ship Mode ────────────────────────────────────────────────────────
with col3_right:
    st.markdown("### 🚢 Sales by Ship Mode")
    ship_data = (filtered.groupby('ship_mode')['sales']
                 .sum()
                 .reset_index()
                 .sort_values('sales', ascending=False))

    fig_ship = px.bar(
        ship_data,
        x='ship_mode', y='sales',
        color='ship_mode',
        color_discrete_sequence=['#0D1F3C','#0096C7','#00B4D8','#48CAE4'],
        text=ship_data['sales'].apply(lambda x: f'${x:,.0f}')
    )
    fig_ship.update_traces(textposition='outside')
    fig_ship.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='#F0F8FF',
        showlegend=False,
        height=300,
        yaxis_tickprefix='$',
        xaxis_title='Ship Mode',
        yaxis_title='Revenue (USD)',
        margin=dict(l=10, r=10, t=10, b=40)
    )
    st.plotly_chart(fig_ship, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# ROW 4: Sub-Category Breakdown
# ════════════════════════════════════════════════════════════════════════════
st.markdown("### 🔍 Sales by Sub-Category")
subcat = (filtered.groupby(['category', 'sub_category'])['sales']
          .sum()
          .reset_index()
          .sort_values('sales', ascending=True))

fig_subcat = px.bar(
    subcat,
    x='sales', y='sub_category',
    color='category',
    orientation='h',
    color_discrete_sequence=['#0D1F3C', '#0096C7', '#48CAE4'],
    text=subcat['sales'].apply(lambda x: f'${x:,.0f}')
)
fig_subcat.update_traces(textposition='outside')
fig_subcat.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='#F0F8FF',
    height=500,
    xaxis_tickprefix='$',
    xaxis_title='Revenue (USD)',
    yaxis_title='',
    margin=dict(l=10, r=80, t=10, b=10)
)
st.plotly_chart(fig_subcat, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# RAW DATA TABLE
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("### 🗃️ Raw Data Explorer")

with st.expander("Click to view & explore the cleaned dataset"):
    cols_to_show = ['order_date', 'category', 'sub_category', 'region',
                    'segment', 'ship_mode', 'sales', 'shipping_days',
                    'sale_size', 'quarter_label']
    st.dataframe(
        filtered[cols_to_show].sort_values('order_date', ascending=False),
        use_container_width=True,
        height=400
    )
    st.caption(f"Showing {len(filtered):,} rows based on current filters")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center><small>Built by Vaisakh · "
    "Superstore Sales Forecasting Pipeline · "
    "Python | Pandas | Streamlit | Plotly | Power BI"
    "</small></center>",
    unsafe_allow_html=True
)