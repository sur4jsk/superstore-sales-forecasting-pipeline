import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Superstore Sales Forecasting",
    page_icon="📦",
    layout="wide"
)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("output/combined_for_powerbi.csv")
    # Normalise column names
    df.columns = df.columns.str.strip()

    # Find the date column (handles Order Date, order_date, date, etc.)
    date_col = next((c for c in df.columns if "date" in c.lower() and "ship" not in c.lower()), None)
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], infer_datetime_format=True, errors="coerce")
        df = df.rename(columns={date_col: "Order Date"})

    # Find sales column
    sales_col = next((c for c in df.columns if "sale" in c.lower()), None)
    if sales_col:
        df = df.rename(columns={sales_col: "Sales"})

    # Find type/label column (historical vs forecast)
    type_col = next((c for c in df.columns if "type" in c.lower() or "label" in c.lower() or "forecast" in c.lower()), None)
    if type_col:
        df = df.rename(columns={type_col: "Type"})
    else:
        df["Type"] = "Historical"

    df = df.dropna(subset=["Order Date", "Sales"])
    df = df.sort_values("Order Date")
    return df

df = load_data()

has_category = "Category" in df.columns
has_region   = "Region" in df.columns
has_profit   = "Profit" in df.columns
has_segment  = "Segment" in df.columns

# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/combo-chart.png", width=60)
st.sidebar.title("Filters")

min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

if has_category:
    categories = ["All"] + sorted(df["Category"].dropna().unique().tolist())
    selected_cat = st.sidebar.selectbox("Category", categories)
else:
    selected_cat = "All"

if has_region:
    regions = ["All"] + sorted(df["Region"].dropna().unique().tolist())
    selected_region = st.sidebar.selectbox("Region", regions)
else:
    selected_region = "All"

# apply filters
filtered = df.copy()
if len(date_range) == 2:
    filtered = filtered[
        (filtered["Order Date"].dt.date >= date_range[0]) &
        (filtered["Order Date"].dt.date <= date_range[1])
    ]
if selected_cat != "All" and has_category:
    filtered = filtered[filtered["Category"] == selected_cat]
if selected_region != "All" and has_region:
    filtered = filtered[filtered["Region"] == selected_region]

historical = filtered[filtered["Type"] == "Historical"] if "Type" in filtered.columns else filtered
forecast   = filtered[filtered["Type"] != "Historical"] if "Type" in filtered.columns else pd.DataFrame()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📦 Superstore Sales Forecasting Dashboard")
st.caption("End-to-end ETL pipeline with 6-month rolling window + 60-day forecast · Built by Suraj Kartha")
st.divider()

# ── KPI cards ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)

total_sales = historical["Sales"].sum()
avg_monthly = historical.groupby(historical["Order Date"].dt.to_period("M"))["Sales"].sum().mean()
forecast_total = forecast["Sales"].sum() if not forecast.empty else 0
profit_total = historical["Profit"].sum() if has_profit else None

k1.metric("Total Historical Sales", f"${total_sales:,.0f}")
k2.metric("Avg Monthly Sales", f"${avg_monthly:,.0f}")
k3.metric("60-Day Forecast Total", f"${forecast_total:,.0f}" if forecast_total else "N/A")
if profit_total is not None:
    k4.metric("Total Profit", f"${profit_total:,.0f}")
else:
    k4.metric("Data Points", f"{len(historical):,}")

st.divider()

# ── Chart 1: Sales Trend + Forecast ───────────────────────────────────────────
st.subheader("📈 Sales Trend — Historical + 60-Day Forecast")

daily_hist = historical.groupby("Order Date")["Sales"].sum().reset_index()
daily_hist["Rolling 6M Avg"] = daily_hist["Sales"].rolling(window=180, min_periods=1).mean()

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=daily_hist["Order Date"], y=daily_hist["Sales"],
    name="Daily Sales", mode="lines",
    line=dict(color="#7C3AED", width=1.5), opacity=0.6
))
fig1.add_trace(go.Scatter(
    x=daily_hist["Order Date"], y=daily_hist["Rolling 6M Avg"],
    name="6-Month Rolling Avg", mode="lines",
    line=dict(color="#2563EB", width=2.5)
))

if not forecast.empty:
    daily_fc = forecast.groupby("Order Date")["Sales"].sum().reset_index()
    fig1.add_trace(go.Scatter(
        x=daily_fc["Order Date"], y=daily_fc["Sales"],
        name="60-Day Forecast", mode="lines",
        line=dict(color="#F59E0B", width=2.5, dash="dash")
    ))
    # Shaded forecast zone
    fig1.add_vrect(
        x0=daily_fc["Order Date"].min(), x1=daily_fc["Order Date"].max(),
        fillcolor="#FEF3C7", opacity=0.3, layer="below", line_width=0,
    )

fig1.update_layout(
    height=400, plot_bgcolor="white", paper_bgcolor="white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    xaxis=dict(showgrid=True, gridcolor="#F3F4F6"),
    yaxis=dict(showgrid=True, gridcolor="#F3F4F6", title="Sales ($)")
)
st.plotly_chart(fig1, use_container_width=True)

# ── Chart 2 & 3 ───────────────────────────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📅 Monthly Sales")
    monthly = historical.copy()
    monthly["Month"] = monthly["Order Date"].dt.to_period("M").astype(str)
    monthly_grouped = monthly.groupby("Month")["Sales"].sum().reset_index()
    fig2 = px.bar(
        monthly_grouped, x="Month", y="Sales",
        color_discrete_sequence=["#7C3AED"],
        labels={"Sales": "Sales ($)", "Month": ""},
    )
    fig2.update_layout(
        height=350, plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(tickangle=-45), yaxis=dict(showgrid=True, gridcolor="#F3F4F6")
    )
    st.plotly_chart(fig2, use_container_width=True)

with col_b:
    if has_category:
        st.subheader("🗂️ Sales by Category")
        cat_data = historical.groupby("Category")["Sales"].sum().reset_index()
        fig3 = px.pie(
            cat_data, values="Sales", names="Category",
            color_discrete_sequence=["#7C3AED", "#2563EB", "#F59E0B"],
            hole=0.4
        )
        fig3.update_layout(height=350, paper_bgcolor="white")
        st.plotly_chart(fig3, use_container_width=True)
    elif has_segment:
        st.subheader("👥 Sales by Segment")
        seg_data = historical.groupby("Segment")["Sales"].sum().reset_index()
        fig3 = px.pie(
            seg_data, values="Sales", names="Segment",
            color_discrete_sequence=["#7C3AED", "#2563EB", "#F59E0B"],
            hole=0.4
        )
        fig3.update_layout(height=350, paper_bgcolor="white")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.subheader("📊 Sales Distribution")
        fig3 = px.histogram(
            historical, x="Sales", nbins=40,
            color_discrete_sequence=["#7C3AED"]
        )
        fig3.update_layout(height=350, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig3, use_container_width=True)

# ── Chart 4: Region breakdown ─────────────────────────────────────────────────
if has_region:
    st.subheader("🗺️ Sales by Region")
    region_data = historical.groupby("Region")["Sales"].sum().reset_index().sort_values("Sales", ascending=True)
    fig4 = px.bar(
        region_data, x="Sales", y="Region", orientation="h",
        color_discrete_sequence=["#2563EB"],
        labels={"Sales": "Total Sales ($)"}
    )
    fig4.update_layout(
        height=300, plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="#F3F4F6")
    )
    st.plotly_chart(fig4, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("Suraj Kartha · Data Engineering Portfolio · github.com/sur4jsk/superstore-sales-forecasting-pipeline")
