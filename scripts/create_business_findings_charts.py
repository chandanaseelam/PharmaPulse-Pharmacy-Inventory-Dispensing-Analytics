"""Reproducible PharmaPulse Business Findings charts (fully synthetic data).
Run from project root: python scripts/create_business_findings_charts.py
Requires: pandas, matplotlib
"""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
OUT = ROOT / 'analysis' / 'images'
OUT.mkdir(parents=True, exist_ok=True)

fact = pd.read_csv(DATA / 'tableau_fact_daily.csv', parse_dates=['Date'])
purchase = pd.read_csv(DATA / 'tableau_supplier.csv')


def finish(fig, filename):
    fig.text(0.01, 0.008, 'Source: PharmaPulse synthetic pharmacy dataset | Store-medicine-day / purchase order grain as indicated',
             fontsize=8, color='dimgray')
    fig.savefig(OUT / filename, dpi=170, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'Saved analysis/images/{filename}')

# Chart 1: stockout counts and relative stockout rates at the store-medicine-day grain
stores = fact.groupby('StoreName', as_index=False).agg(
    StockoutDays=('StockoutFlag', 'sum'), Rows=('StockoutFlag', 'size')
)
stores['StockoutRate'] = 100 * stores['StockoutDays'] / stores['Rows']
stores = stores.sort_values('StockoutDays')
fig, ax = plt.subplots(figsize=(9.6, 5.3))
ax.barh(stores['StoreName'].str.replace(' Pharmacy', '', regex=False), stores['StockoutDays'])
for y, (_, r) in enumerate(stores.iterrows()):
    ax.text(r['StockoutDays'] + 1, y, f"{int(r['StockoutDays'])}  ({r['StockoutRate']:.3f}%)", va='center', fontsize=10)
ax.set_xlim(0, stores['StockoutDays'].max() * 1.35)
ax.set_xlabel('Stockout store–medicine–days')
ax.set_title('Stockout exposure by pharmacy store', fontweight='bold', loc='left')
ax.grid(axis='x', alpha=.15)
ax.set_axisbelow(True)
fig.tight_layout(rect=[0, .035, 1, 1])
finish(fig, '01_store_stockout_exposure.png')

# Chart 2: counts of daily conditions; low-stock and zero-stock flags can overlap
counts = [int(fact['BelowReorderFlag'].sum()), int(fact['StockoutFlag'].sum())]
n = len(fact)
fig, ax = plt.subplots(figsize=(8.9, 5.3))
bars = ax.bar(['Below reorder threshold', 'Zero closing stock'], counts, width=.6)
for bar, count in zip(bars, counts):
    ax.text(bar.get_x() + bar.get_width()/2, count + 55, f'{count:,} ({100*count/n:.2f}%)',
            ha='center', va='bottom', fontweight='bold')
ax.set_ylim(0, max(counts)*1.20)
ax.set_ylabel('Store–medicine–day records')
ax.set_title('Inventory early-warning vs. stockout signals', fontweight='bold', loc='left')
ax.text(.02,.96,'These are overlapping indicators, not mutually exclusive categories.',
        transform=ax.transAxes, ha='left', va='top', color='dimgray', fontsize=9)
ax.grid(axis='y', alpha=.15); ax.set_axisbelow(True)
fig.tight_layout(rect=[0,.035,1,1])
finish(fig, '02_inventory_early_warning.png')

# Chart 3: correct denominator = received purchase orders, not all purchase orders
received = purchase[purchase['OrderStatus'] == 'Received'].copy()
supplier = received.groupby('SupplierName', as_index=False).agg(
    ReceivedOrders=('PurchaseOrderID','nunique'), OnTimeOrders=('OnTimeFlag','sum')
)
supplier['OnTimeRate'] = 100*supplier['OnTimeOrders']/supplier['ReceivedOrders']
supplier = supplier.sort_values('OnTimeRate')
fig, ax = plt.subplots(figsize=(9.7,5.3))
ax.barh(supplier['SupplierName'], supplier['OnTimeRate'])
for y, (_, r) in enumerate(supplier.iterrows()):
    ax.text(r['OnTimeRate'] + 1, y, f"{r['OnTimeRate']:.2f}%  ({int(r['OnTimeOrders'])}/{int(r['ReceivedOrders'])})", va='center', fontsize=10)
ax.set_xlim(0,80)
ax.set_xlabel('On-time deliveries among received orders (%)')
ax.set_title('Supplier on-time delivery performance', fontweight='bold', loc='left')
ax.grid(axis='x', alpha=.15); ax.set_axisbelow(True)
fig.tight_layout(rect=[0,.035,1,1])
finish(fig, '03_supplier_on_time_delivery.png')

# Chart 4: stores ranked by modeled revenue
sales = fact.groupby('StoreName', as_index=False)['RevenueUSD'].sum().sort_values('RevenueUSD')
fig, ax = plt.subplots(figsize=(9.7,5.3))
ax.barh(sales['StoreName'].str.replace(' Pharmacy','',regex=False),sales['RevenueUSD'])
for y, (_, r) in enumerate(sales.iterrows()):
    ax.text(r['RevenueUSD'] + 900, y, f"${r['RevenueUSD']:,.0f}",va='center')
ax.set_xlim(0,sales['RevenueUSD'].max()*1.23)
ax.set_xlabel('Modeled revenue (USD)')
ax.set_title('Modeled revenue by store', fontweight='bold', loc='left')
ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
fig.tight_layout(rect=[0,.035,1,1])
finish(fig, '04_store_revenue.png')

# Chart 5: date axis, proper monthly aggregation of modeled revenue
monthly = fact.groupby(fact['Date'].dt.to_period('M'))['RevenueUSD'].sum().sort_index()
fig, ax = plt.subplots(figsize=(10.8,5.2))
ax.plot(monthly.index.to_timestamp(), monthly.values,marker='o', linewidth=2)
ax.set_ylabel('Modeled revenue (USD)')
ax.set_title('Monthly pharmacy revenue (synthetic)', fontweight='bold',loc='left')
ax.grid(alpha=.15);ax.set_axisbelow(True)
fig.autofmt_xdate()
fig.tight_layout(rect=[0,.035,1,1])
finish(fig, '05_monthly_revenue_trend.png')

print('\nReconciled totals:')
print(f"Inventory rows: {len(fact):,} | stockout flags: {counts[1]:,} | below-reorder flags: {counts[0]:,}")
print(f"Supplier received orders: {len(received):,} | supplier on-time orders: {int(received['OnTimeFlag'].sum()):,}")
print(f"Modeled sales revenue: ${fact['RevenueUSD'].sum():,.2f}")
