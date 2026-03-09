# Superstore Sales Forecasting Pipeline

## Overview
End-to-end data engineering pipeline that processes real Kaggle 
Superstore sales data and generates a 60-day rolling forecast.

## Tech Stack
Python | Pandas | Power BI | DAX | Git

## Dataset
Kaggle Superstore Sales Dataset — 9,800 rows

## How to Run
1. pip install pandas openpyxl matplotlib seaborn
2. python scripts/01_inspect_data.py
3. python scripts/02_etl_pipeline.py
4. python scripts/03_forecasting.py
5. python scripts/04_visualise.py
6. Load output/combined_for_powerbi.csv into Power BI

## Project Structure
data/raw/        - Raw Kaggle CSV
data/processed/  - Cleaned and transformed data
scripts/         - Python ETL and forecasting scripts
output/          - Power BI ready files and charts
