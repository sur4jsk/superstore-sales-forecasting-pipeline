# ── 02_etl_pipeline.py ────────────────────────────────────────────────────────
# ETL = Extract, Transform, Load
# This is the core data engineering script.
#
# EXTRACT  : Read raw Superstore CSV
# TRANSFORM: Clean it, fix data types, add useful columns
# LOAD     : Save a clean version ready for analysis
# ─────────────────────────────────────────────────────────────────────────────

import pandas as pd

# ════════════════════════════════════════════════════════════════════════════
# EXTRACT — Read the raw data
# ════════════════════════════════════════════════════════════════════════════
print(">>> EXTRACT: Loading raw data...")
df = pd.read_csv('data/raw/train.csv')
print(f"    Loaded {len(df):,} rows, {len(df.columns)} columns")


# ════════════════════════════════════════════════════════════════════════════
# TRANSFORM — Clean and enrich the data
# ════════════════════════════════════════════════════════════════════════════
print("\n>>> TRANSFORM: Cleaning data...")

# ── 1. Fix column names: remove spaces, make lowercase ───────────────────────
df.columns = (df.columns
              .str.strip()           # remove leading/trailing spaces
              .str.lower()           # make lowercase
              .str.replace(' ', '_') # replace spaces with underscores
              .str.replace('-', '_') # replace hyphens with underscores
              )
print("    Column names standardised")

# ── 2. Convert date columns from text to actual dates ────────────────────────
df['order_date'] = pd.to_datetime(df['order_date'], dayfirst=True)
df['ship_date']  = pd.to_datetime(df['ship_date'],  dayfirst=True)
print("    Date columns converted")

# ── 3. Remove duplicate rows ─────────────────────────────────────────────────
before = len(df)
df = df.drop_duplicates()
print(f"    Duplicates removed: {before - len(df)} rows dropped")

# ── 4. Drop rows where critical values are missing ───────────────────────────
before = len(df)
df = df.dropna(subset=['order_date', 'sales', 'region', 'category'])
print(f"    Null rows removed: {before - len(df)} rows dropped")

# ── 5. Make sure Sales is a number (float) ───────────────────────────────────
df['sales'] = pd.to_numeric(df['sales'], errors='coerce').round(2)

# ── 6. Add time-based columns (very useful in Power BI) ──────────────────────
df['year']         = df['order_date'].dt.year
df['month_num']    = df['order_date'].dt.month
df['month_name']   = df['order_date'].dt.strftime('%b')   # Jan, Feb...
df['quarter']      = df['order_date'].dt.quarter           # 1, 2, 3, 4
df['quarter_label']= 'Q' + df['quarter'].astype(str)      # Q1, Q2...
df['week_num']     = df['order_date'].dt.isocalendar().week.astype(int)
df['day_name']     = df['order_date'].dt.strftime('%A')    # Monday, Tuesday...
df['is_weekend']   = df['order_date'].dt.weekday >= 5     # True/False

# ── 7. Calculate shipping duration in days ───────────────────────────────────
df['shipping_days'] = (df['ship_date'] - df['order_date']).dt.days

# ── 8. Add a sales size label (useful for segmentation) ──────────────────────
def label_sale(value):
    if value < 50:
        return 'Small'
    elif value < 300:
        return 'Medium'
    else:
        return 'Large'

df['sale_size'] = df['sales'].apply(label_sale)

# ── 9. Month-Year label for easy Power BI axis labels ────────────────────────
df['month_year'] = df['order_date'].dt.strftime('%b %Y')  # Jan 2017

print("    Calculated columns added:")
print("    year, month_num, month_name, quarter, quarter_label,")
print("    week_num, day_name, is_weekend, shipping_days,")
print("    sale_size, month_year")


# ════════════════════════════════════════════════════════════════════════════
# LOAD — Save the clean data
# ════════════════════════════════════════════════════════════════════════════
print("\n>>> LOAD: Saving clean data...")

output_path = 'data/processed/superstore_clean.csv'
df.to_csv(output_path, index=False)

print(f"    Saved to: {output_path}")
print(f"    Final shape: {df.shape[0]:,} rows x {df.shape[1]} columns")

# ── Quick summary ─────────────────────────────────────────────────────────────
print("\n>>> SUMMARY:")
print(f"    Total Sales Revenue : ${df['sales'].sum():,.2f}")
print(f"    Avg Order Value     : ${df['sales'].mean():,.2f}")
print(f"    Date Range          : {df['order_date'].min().date()} → {df['order_date'].max().date()}")
print(f"    Regions             : {sorted(df['region'].unique())}")
print(f"    Categories          : {sorted(df['category'].unique())}")
print("\nETL complete! Move to script 03 next.")
