import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Superstore Sales Forecasting",
    page_icon="📦",
    layout="wide"
)

@st.cache_data
def load_data():
    df = pd.read_csv("output/combined_for_powerbi.csv")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    return df

df = load_data()

historical = df[df["data_type"] == "Historical"].copy()
forecast   = df[df["data_type"] != "Historical"].copy()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("📦 Filters")
min_date = df["date"].min().date()
max_date = df["date"].max().date()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

if len(date_range) == 2:
    historical = historical[
        (historical["date"].dt.date >= date_range[0]) &
        (historical["date"].dt.date <= date_range[1])
    ]

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📦 Superstore Sales Forecasting Dashboard")
st.caption("End-to-end ETL pipeline · 6-month rolling window · 60-day forecast · Built by Suraj Kartha")
st.divider()

# ── KPI Cards ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Revenue", f"${historical['actual_revenue'].sum():,.0f}")
k2.metric("Avg Daily Revenue", f"${historical['actual_revenue'].mean():,.0f}")
k3.metric("Total Orders", f"{int(historical['order_count'].sum()):,}")
k4.metric("60-Day Forecast Total", f"${forecast['forecast_revenue'].sum():,.0f}" if not forecast.empty else "N/A")

st.divider()

# ── Chart 1: Revenue Trend + Forecast ────────────────────────────────────────
st.subheader("📈 Revenue Trend — Historical + 60-Day Forecast")

fig1 = go.Figure()

fig1.add_trace(go.Scatter(
    x=historical["date"], y=historical["actual_revenue"],
    name="Daily Revenue", mode="lines",
    line=dict(color="#7C3AED", width=1.5), opacity=0.5
))

fig1.add_trace(go.Scatter(
    x=historical["date"], y=historical["rolling_7d_avg"],
    name="7-Day Rolling Avg", mode="lines",
    line=dict(color="#2563EB", width=2.5)
))

if not forecast.empty:
    fig1.add_trace(go.Scatter(
        x=forecast["date"], y=forecast["forecast_revenue"],
        name="60-Day Forecast", mode="lines",
        line=dict(color="#F59E0B", width=2.5, dash="dash")
    ))
    fig1.add_vrect(
        x0=str(forecast["date"].min()),
        x1=str(forecast["date"].max()),
        fillcolor="#FEF3C7", opacity=0.25, layer="below", line_width=0
    )
    # Dividing line between historical and forecast
    fig1.add_vline(
        x=str(historical["date"].max()),
        line_dash="dot", line_color="#9CA3AF", line_width=1.5,
        annotation_text="Forecast Start",
        annotation_position="top right",
        annotation_font_color="#9CA3AF"
    )

fig1.update_layout(
    height=420, plot_bgcolor="white", paper_bgcolor="white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    xaxis=dict(showgrid=True, gridcolor="#F3F4F6"),
    yaxis=dict(showgrid=True, gridcolor="#F3F4F6", title="Revenue ($)")
)
st.plotly_chart(fig1, use_container_width=True)

# ── Chart 2 & 3 ───────────────────────────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📅 Monthly Revenue")
    monthly = historical.copy()
    monthly["Month"] = monthly["date"].dt.to_period("M").astype(str)
    monthly_grouped = monthly.groupby("Month")["actual_revenue"].sum().reset_index()
    fig2 = px.bar(
        monthly_grouped, x="Month", y="actual_revenue",
        color_discrete_sequence=["#7C3AED"],
        labels={"actual_revenue": "Revenue ($)", "Month": ""}
    )
    fig2.update_layout(
        height=350, plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(tickangle=-45),
        yaxis=dict(showgrid=True, gridcolor="#F3F4F6")
    )
    st.plotly_chart(fig2, use_container_width=True)

with col_b:
    st.subheader("🛒 Daily Order Volume")
    fig3 = px.line(
        historical, x="date", y="order_count",
        color_discrete_sequence=["#2563EB"],
        labels={"order_count": "Orders", "date": ""}
    )
    fig3.update_layout(
        height=350, plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="#F3F4F6"),
        yaxis=dict(showgrid=True, gridcolor="#F3F4F6")
    )
    st.plotly_chart(fig3, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("Suraj Kartha · Data Engineering Portfolio · github.com/sur4jsk/superstore-sales-forecasting-pipeline")