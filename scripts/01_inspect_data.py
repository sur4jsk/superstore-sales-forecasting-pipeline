# ── 01_inspect_data.py ────────────────────────────────────────────────────────
# STEP 1: Always inspect your data BEFORE touching it.
# This script tells you what columns exist, what types they are,
# how many nulls, and what the data looks like.
# Run this first and read the output carefully.
# ─────────────────────────────────────────────────────────────────────────────

import pandas as pd

# ── Load the raw Superstore CSV ───────────────────────────────────────────────
df = pd.read_csv('data/raw/train.csv')

print("=" * 60)
print("STEP 1: BASIC INFO")
print("=" * 60)
print(f"Total rows    : {len(df):,}")
print(f"Total columns : {len(df.columns)}")

print("\n" + "=" * 60)
print("STEP 2: COLUMN NAMES & DATA TYPES")
print("=" * 60)
print(df.dtypes)

print("\n" + "=" * 60)
print("STEP 3: MISSING VALUES PER COLUMN")
print("=" * 60)
print(df.isnull().sum())

print("\n" + "=" * 60)
print("STEP 4: FIRST 5 ROWS (preview)")
print("=" * 60)
print(df.head())

print("\n" + "=" * 60)
print("STEP 5: SALES COLUMN SUMMARY")
print("=" * 60)
print(df['Sales'].describe().round(2))

print("\n" + "=" * 60)
print("STEP 6: UNIQUE VALUES IN KEY COLUMNS")
print("=" * 60)
print(f"Regions    : {df['Region'].unique()}")
print(f"Categories : {df['Category'].unique()}")
print(f"Segments   : {df['Segment'].unique()}")
print(f"Ship Modes : {df['Ship Mode'].unique()}")

print("\n" + "=" * 60)
print("STEP 7: DATE RANGE")
print("=" * 60)
# Convert dates so we can find min/max
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
print(f"Earliest order : {df['Order Date'].min().date()}")
print(f"Latest order   : {df['Order Date'].max().date()}")
print(f"Date span      : {(df['Order Date'].max() - df['Order Date'].min()).days} days")

print("\nDone! Read all the output above before moving to script 02.")
