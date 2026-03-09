import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

# ── Load outputs from script 03 ───────────────────────────────────────────────
hist     = pd.read_csv('data/processed/historical_window.csv', parse_dates=['date'])
fore     = pd.read_csv('data/processed/forecast_60day.csv',    parse_dates=['date'])
cat_data = pd.read_csv('output/monthly_category_sales.csv')
region   = pd.read_csv('output/region_summary.csv')
clean    = pd.read_csv('data/processed/superstore_clean.csv',  parse_dates=['order_date'])

# ── Figure layout: 2 rows x 2 columns ────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('Superstore Sales Analytics Dashboard — Verification Chart',
             fontsize=15, fontweight='bold', color='#0D1F3C', y=1.01)
fig.patch.set_facecolor('#F0F8FF')

# ────────────────────────────────────────────────────────────────────────────
# CHART 1: Revenue Trend + Forecast (top-left)
# ────────────────────────────────────────────────────────────────────────────
ax1 = axes[0, 0]
ax1.set_facecolor('#F8FBFF')

ax1.fill_between(hist['date'], hist['actual_revenue'],
                 alpha=0.15, color='#00B4D8')
ax1.plot(hist['date'], hist['actual_revenue'],
         color='#00B4D8', alpha=0.5, linewidth=1, label='Daily Revenue')
ax1.plot(hist['date'], hist['rolling_7d_avg'],
         color='#0D1F3C', linewidth=2.5, label='7-Day Moving Avg')
ax1.plot(fore['date'], fore['forecast_revenue'],
         color='#FF9F1C', linewidth=2.5, linestyle='--', label='60-Day Forecast')

# Divider line at the boundary
ax1.axvline(x=hist['date'].max(), color='#999', linestyle=':', linewidth=1.2)
ax1.text(hist['date'].max(), ax1.get_ylim()[1] if ax1.get_ylim()[1] != 1.0 else 5000,
         ' Forecast →', fontsize=8, color='#FF9F1C', va='top')

ax1.set_title('Rolling 6-Month Revenue + 60-Day Forecast', fontweight='bold', fontsize=10)
ax1.set_ylabel('Revenue (USD)')
ax1.legend(fontsize=8)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=30)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
ax1.grid(axis='y', alpha=0.3)

# ────────────────────────────────────────────────────────────────────────────
# CHART 2: Sales by Category (top-right)
# ────────────────────────────────────────────────────────────────────────────
ax2 = axes[0, 1]
ax2.set_facecolor('#F8FBFF')

cat_totals = (clean.groupby('category')['sales']
              .sum()
              .sort_values(ascending=True))

colors_bar = ['#00B4D8', '#0096C7', '#0D1F3C']
bars = ax2.barh(cat_totals.index, cat_totals.values, color=colors_bar, edgecolor='white')

for bar, val in zip(bars, cat_totals.values):
    ax2.text(bar.get_width() + 1000, bar.get_y() + bar.get_height()/2,
             f'${val:,.0f}', va='center', fontsize=9, color='#0D1F3C')

ax2.set_title('Total Sales by Category', fontweight='bold', fontsize=10)
ax2.set_xlabel('Revenue (USD)')
ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1000:.0f}K'))
ax2.grid(axis='x', alpha=0.3)

# ────────────────────────────────────────────────────────────────────────────
# CHART 3: Sales by Region (bottom-left)
# ────────────────────────────────────────────────────────────────────────────
ax3 = axes[1, 0]
ax3.set_facecolor('#F8FBFF')

region_sorted = region.sort_values('total_sales', ascending=False)
bar_colors = ['#0D1F3C', '#0096C7', '#00B4D8', '#48CAE4']
bars2 = ax3.bar(region_sorted['region'], region_sorted['total_sales'],
                color=bar_colors, edgecolor='white', width=0.6)

for bar, val in zip(bars2, region_sorted['total_sales']):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 500,
             f'${val:,.0f}', ha='center', fontsize=8.5, color='#0D1F3C')

ax3.set_title('Total Sales by Region', fontweight='bold', fontsize=10)
ax3.set_ylabel('Revenue (USD)')
ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1000:.0f}K'))
ax3.grid(axis='y', alpha=0.3)

# ────────────────────────────────────────────────────────────────────────────
# CHART 4: Monthly Orders Trend (bottom-right)
# ────────────────────────────────────────────────────────────────────────────
ax4 = axes[1, 1]
ax4.set_facecolor('#F8FBFF')

monthly = (clean.groupby(clean['order_date'].dt.to_period('M'))
           .size()
           .reset_index(name='order_count'))
monthly['order_date'] = monthly['order_date'].dt.to_timestamp()

ax4.plot(monthly['order_date'], monthly['order_count'],
         color='#06D6A0', linewidth=2.5, marker='o', markersize=4)
ax4.fill_between(monthly['order_date'], monthly['order_count'],
                 alpha=0.15, color='#06D6A0')

ax4.set_title('Monthly Order Volume Trend', fontweight='bold', fontsize=10)
ax4.set_ylabel('Number of Orders')
ax4.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
plt.setp(ax4.xaxis.get_majorticklabels(), rotation=30)
ax4.grid(axis='y', alpha=0.3)

# ── Save & show ───────────────────────────────────────────────────────────────
plt.tight_layout()
plt.savefig('output/verification_dashboard.png', dpi=150, bbox_inches='tight',
            facecolor='#F0F8FF')
print("Chart saved → output/verification_dashboard.png")
print("If all 4 charts look sensible, your pipeline is working correctly!")
plt.show()
