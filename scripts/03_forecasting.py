# ── 03_forecasting.py ─────────────────────────────────────────────────────────
# This script does two things:
#
# PART 1 — Rolling 6-month window
#   Filters only the most recent 6 months of data.
#   Computes daily totals and a 7-day moving average.
#
# PART 2 — 60-day forecast
#   Projects daily revenue 60 days into the future
#   using a simple linear trend (average + growth rate).
#
# Output: 3 CSV files ready to load into Power BI.
# ─────────────────────────────────────────────────────────────────────────────

import pandas as pd
import numpy as np
from datetime import timedelta

# ── Load the clean ETL output ─────────────────────────────────────────────────
print(">>> Loading clean data...")
df = pd.read_csv('data/processed/superstore_clean.csv',
                 parse_dates=['order_date'])

print(f"    Rows loaded: {len(df):,}")
print(f"    Date range : {df['order_date'].min().date()} → {df['order_date'].max().date()}")


# ════════════════════════════════════════════════════════════════════════════
# PART 1: ROLLING 6-MONTH WINDOW
# ════════════════════════════════════════════════════════════════════════════
print("\n>>> PART 1: Applying rolling 6-month window...")

# Use the latest date in the dataset as "today"
today      = df['order_date'].max()
six_mo_ago = today - pd.DateOffset(months=6)

# Filter to last 6 months only
df_window = df[df['order_date'] >= six_mo_ago].copy()
print(f"    Window : {six_mo_ago.date()} → {today.date()}")
print(f"    Rows   : {len(df_window):,}")

# ── Aggregate to daily totals ──────────────────────────────────────────────────
daily = (df_window
         .groupby('order_date')
         .agg(
             actual_revenue = ('sales', 'sum'),
             order_count    = ('order_id', 'count'),
         )
         .reset_index()
         .rename(columns={'order_date': 'date'}))

daily['actual_revenue'] = daily['actual_revenue'].round(2)

# ── 7-day rolling average (smooths out day-to-day spikes) ─────────────────────
daily['rolling_7d_avg'] = (daily['actual_revenue']
                           .rolling(window=7, min_periods=1)
                           .mean()
                           .round(2))

# ── Monthly totals for category breakdown ─────────────────────────────────────
monthly_by_cat = (df_window
                  .groupby(['month_year', 'category'])['sales']
                  .sum()
                  .reset_index()
                  .rename(columns={'sales': 'monthly_sales'}))
monthly_by_cat['monthly_sales'] = monthly_by_cat['monthly_sales'].round(2)

# ── Region breakdown ──────────────────────────────────────────────────────────
region_summary = (df_window
                  .groupby('region')['sales']
                  .agg(['sum', 'count', 'mean'])
                  .round(2)
                  .reset_index()
                  .rename(columns={'sum':'total_sales',
                                   'count':'order_count',
                                   'mean':'avg_order_value'}))

print(f"\n    Daily revenue avg : ${daily['actual_revenue'].mean():,.2f}")
print(f"    Daily order avg   : {daily['order_count'].mean():.1f} orders")


# ════════════════════════════════════════════════════════════════════════════
# PART 2: 60-DAY FORECAST
# ════════════════════════════════════════════════════════════════════════════
print("\n>>> PART 2: Generating 60-day forecast...")

# Base: average daily revenue from the rolling window
avg_daily_revenue = daily['actual_revenue'].mean()

# Growth rate: 1% per month = ~0.033% per day
# This is a simple assumption — good enough for an intern portfolio
daily_growth_rate = 0.00033

# Build 60 future rows, one per day
forecast_dates   = [today + timedelta(days=i) for i in range(1, 61)]
forecast_revenue = [
    round(avg_daily_revenue * (1 + daily_growth_rate * i), 2)
    for i in range(1, 61)
]

df_forecast = pd.DataFrame({
    'date'            : forecast_dates,
    'forecast_revenue': forecast_revenue,
    'data_type'       : 'Forecast'
})

print(f"    Base daily revenue : ${avg_daily_revenue:,.2f}")
print(f"    Day 1 forecast     : ${forecast_revenue[0]:,.2f}")
print(f"    Day 60 forecast    : ${forecast_revenue[-1]:,.2f}")
print(f"    Total projected    : ${sum(forecast_revenue):,.2f}")


# ════════════════════════════════════════════════════════════════════════════
# COMBINE: Historical + Forecast into one Power BI table
# ════════════════════════════════════════════════════════════════════════════
daily['data_type']        = 'Historical'
daily['forecast_revenue'] = None  # empty for historical rows

df_combined = pd.concat([
    daily[['date', 'actual_revenue', 'rolling_7d_avg',
           'order_count', 'data_type', 'forecast_revenue']],
    df_forecast[['date', 'forecast_revenue', 'data_type']]
], ignore_index=True)


# ════════════════════════════════════════════════════════════════════════════
# SAVE ALL OUTPUTS
# ════════════════════════════════════════════════════════════════════════════
print("\n>>> Saving files...")

daily.to_csv('data/processed/historical_window.csv', index=False)
df_forecast.to_csv('data/processed/forecast_60day.csv', index=False)
df_combined.to_csv('output/combined_for_powerbi.csv', index=False)
monthly_by_cat.to_csv('output/monthly_category_sales.csv', index=False)
region_summary.to_csv('output/region_summary.csv', index=False)

print("    data/processed/historical_window.csv")
print("    data/processed/forecast_60day.csv")
print("    output/combined_for_powerbi.csv       <-- main Power BI file")
print("    output/monthly_category_sales.csv")
print("    output/region_summary.csv")
print("\nForecasting complete! Move to script 04 to verify with a chart.")
