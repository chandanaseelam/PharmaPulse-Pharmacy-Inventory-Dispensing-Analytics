"""Build a fully offline, filterable 3-dashboard Plotly HTML companion to Tableau materials."""
from pathlib import Path
import csv,json
from plotly.offline import get_plotlyjs
R=Path(__file__).resolve().parents[1]
with (R/'data'/'tableau_fact_daily.csv').open(newline='',encoding='utf8') as f:d=list(csv.DictReader(f))
with (R/'data'/'tableau_supplier.csv').open(newline='',encoding='utf8') as f:p=list(csv.DictReader(f))
# Compact tuples reduce the standalone HTML footprint
rows=[]
for x in d:
 rows.append([x['Date'],x['YearMonth'],x['StoreName'],x['ProductCategory'],x['DrugName'],
 int(x['ClosingStock']),float(x['InventoryValueUSD']),int(x['StockoutFlag']),int(x['BelowReorderFlag']),
 int(x['DispensedQuantity']),float(x['RevenueUSD']),float(x['GrossProfitUSD']),int(x['RequestedUnits']),int(x['FulfilledUnits']),int(x['UnfulfilledUnits']),int(x['TransactionCount'])])
pos=[]
for x in p:
 pos.append([x['ActualDeliveryDate'] or x['OrderDate'],x['StoreName'],x['ProductCategory'],x['SupplierName'],int(x['OnTimeFlag']) if x['OnTimeFlag'] else None,x['OrderStatus']])
meta={'period':['2025-06','2026-08'],'stores':sorted(set(x[2] for x in rows)), 'categories':sorted(set(x[3] for x in rows)), 'allRows':len(rows)}
repl={'__PLOTLY_JS__':get_plotlyjs(),'__ROWS__':json.dumps(rows,separators=(',',':')), '__POS__':json.dumps(pos,separators=(',',':')), '__META__':json.dumps(meta,separators=(',',':'))}
html=(R/'dashboards'/'dashboard_template.html').read_text(encoding='utf8')
for a,b in repl.items():html=html.replace(a,b)
(R/'dashboards'/'Pharmacy_Analytics_Interactive_Dashboards.html').write_text(html,encoding='utf8')
print('Dashboard HTML bytes:',len(html.encode('utf8')))
