"""Load normalized CSVs into portable SQLite and export verified BI summaries."""
from pathlib import Path
import sqlite3, csv, json, collections
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; ANA=ROOT/'analysis'
DB=ROOT/'pharmacy_analytics.sqlite'
DB.unlink(missing_ok=True)
conn=sqlite3.connect(DB)
sets={
 'tableau_fact_daily':'tableau_fact_daily.csv','tableau_supplier':'tableau_supplier.csv',
 'tableau_transactions':'tableau_transactions.csv', 'dispensing_transactions':'dispensing_transactions.csv',
 'dim_stores':'dim_stores.csv', 'dim_drugs':'dim_drugs.csv', 'dim_suppliers':'dim_suppliers.csv',
 'demand_daily':'demand_daily.csv', 'purchase_orders':'purchase_orders.csv'}
intcol=set('Year MonthNumber OpeningStock ReceivedQuantity DispensedQuantity AdjustmentQuantity ClosingStock ReorderLevel StockoutFlag BelowReorderFlag RequestedUnits FulfilledUnits UnfulfilledUnits TransactionCount UnitsDispensed OrderQuantity OnTimeFlag ActualLeadTimeDays ReorderLeadTimeDays TargetLeadTimeDays'.split())
realcol=set('EstimatedDaysOfCover ClosingInventoryValueUSD InventoryValueUSD UnitCostUSD UnitPriceUSD UnitSellingPriceUSD RevenueUSD COGSUSD GrossProfitUSD OrderValueUSD EstimatedLostSalesUSD'.split())
for table,file in sets.items():
 with (DATA/file).open(newline='',encoding='utf8') as f:
  rd=csv.DictReader(f);fields=rd.fieldnames
  cols=[f'"{c}" '+('INTEGER' if c in intcol else 'REAL' if c in realcol else 'TEXT') for c in fields]
  conn.execute('CREATE TABLE "'+table+'" ('+', '.join(cols)+')')
  sql='INSERT INTO "'+table+'" VALUES ('+','.join(['?']*len(fields))+')'
  batch=[]
  for x in rd:
   row=[None if x[c]=='' else int(x[c]) if c in intcol else float(x[c]) if c in realcol else x[c] for c in fields]
   batch.append(row)
   if len(batch)>=1000:conn.executemany(sql,batch);batch=[]
  if batch:conn.executemany(sql,batch)
conn.execute('CREATE UNIQUE INDEX idx_daily_key ON tableau_fact_daily(Date,StoreID,DrugID)')
conn.execute('CREATE UNIQUE INDEX idx_txn_key ON dispensing_transactions(TransactionID)')
conn.execute('CREATE INDEX idx_date ON tableau_fact_daily(Date)')
conn.execute('CREATE INDEX idx_supplier_status ON tableau_supplier(SupplierID,OrderStatus)')
conn.commit()
queries={
 'monthly_trends':'''WITH m AS (SELECT YearMonth, SUM(RevenueUSD) revenue, SUM(GrossProfitUSD) profit, SUM(DispensedQuantity) units, SUM(UnfulfilledUnits) lost_units, SUM(StockoutFlag) stockout_days, SUM(BelowReorderFlag) low_stock_days, SUM(StockoutFlag)*100.0/COUNT(*) stockout_rate FROM tableau_fact_daily GROUP BY YearMonth), prev AS (SELECT *,LAG(revenue) OVER(ORDER BY YearMonth) previous_revenue FROM m) SELECT YearMonth,ROUND(revenue,2) AS RevenueUSD,ROUND(profit,2) AS GrossProfitUSD,units AS DispensedUnits,lost_units AS UnfulfilledUnits,stockout_days AS StockoutDays,low_stock_days AS BelowReorderDays,ROUND(stockout_rate,3) AS StockoutRatePct,ROUND(100.0*(revenue-previous_revenue)/NULLIF(previous_revenue,0),2) AS RevenueMoMPct FROM prev ORDER BY YearMonth''',
 'store_performance':'''SELECT StoreID,StoreName,ROUND(SUM(RevenueUSD),2) RevenueUSD,ROUND(SUM(GrossProfitUSD),2) GrossProfitUSD,SUM(DispensedQuantity) DispensedUnits,SUM(StockoutFlag) StockoutDays,SUM(BelowReorderFlag) BelowReorderDays,ROUND(100.0*SUM(StockoutFlag)/COUNT(*),3) StockoutRatePct,SUM(UnfulfilledUnits) UnfulfilledUnits,ROUND(100.0*SUM(FulfilledUnits)/NULLIF(SUM(RequestedUnits),0),3) FulfillmentRatePct FROM tableau_fact_daily GROUP BY StoreID,StoreName ORDER BY RevenueUSD DESC''',
 'category_performance':'''SELECT ProductCategory,ROUND(SUM(RevenueUSD),2) RevenueUSD,ROUND(SUM(GrossProfitUSD),2) GrossProfitUSD,SUM(DispensedQuantity) DispensedUnits,SUM(StockoutFlag) StockoutDays,SUM(BelowReorderFlag) BelowReorderDays FROM tableau_fact_daily GROUP BY ProductCategory ORDER BY RevenueUSD DESC''',
 'drug_performance':'''SELECT DrugID,DrugName,ProductCategory,ROUND(SUM(RevenueUSD),2) RevenueUSD,ROUND(SUM(GrossProfitUSD),2) GrossProfitUSD,SUM(DispensedQuantity) DispensedUnits,SUM(StockoutFlag) StockoutDays,SUM(BelowReorderFlag) BelowReorderDays,SUM(UnfulfilledUnits) UnfulfilledUnits FROM tableau_fact_daily GROUP BY DrugID,DrugName,ProductCategory ORDER BY RevenueUSD DESC''',
 'risk_matrix':'''SELECT StoreName,ProductCategory,SUM(StockoutFlag) StockoutDays,SUM(BelowReorderFlag) BelowReorderDays,SUM(UnfulfilledUnits) UnfulfilledUnits,ROUND(SUM(EstimatedLostSalesUSD),2) EstimatedLostSalesUSD FROM tableau_fact_daily GROUP BY StoreName,ProductCategory ORDER BY StockoutDays DESC''',
 'supplier_performance':'''SELECT SupplierID,SupplierName,COUNT(*) CompletedOrders,SUM(OnTimeFlag) OnTimeOrders,ROUND(100.0*SUM(OnTimeFlag)/COUNT(*),2) OnTimePct,ROUND(AVG(ActualLeadTimeDays),2) AvgLeadDays,ROUND(SUM(OrderValueUSD),2) ReceivedOrderValueUSD FROM tableau_supplier WHERE OrderStatus='Received' GROUP BY SupplierID,SupplierName ORDER BY OnTimePct''',
 'latest_inventory_by_store':'''SELECT Date,StoreName,ROUND(SUM(InventoryValueUSD),2) InventoryValueUSD,SUM(ClosingStock) OnHandUnits,SUM(StockoutFlag) StockoutProducts,SUM(BelowReorderFlag) BelowReorderProducts FROM tableau_fact_daily WHERE Date=(SELECT MAX(Date) FROM tableau_fact_daily) GROUP BY Date,StoreName ORDER BY InventoryValueUSD DESC'''
}
for title,query in queries.items():
 cur=conn.execute(query);cols=[a[0] for a in cur.description]
 with (ANA/(title+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.writer(f);w.writerow(cols);w.writerows(cur.fetchall())

q=conn.execute('''SELECT SUM(DispensedQuantity),SUM(RevenueUSD),SUM(COGSUSD),SUM(GrossProfitUSD),SUM(StockoutFlag),COUNT(*),SUM(BelowReorderFlag),SUM(FulfilledUnits),SUM(RequestedUnits),SUM(UnfulfilledUnits),SUM(EstimatedLostSalesUSD) FROM tableau_fact_daily''').fetchone()
latest=conn.execute('SELECT ROUND(SUM(InventoryValueUSD),2),SUM(ClosingStock) FROM tableau_fact_daily WHERE Date=(SELECT MAX(Date) FROM tableau_fact_daily)').fetchone()
sup=conn.execute('SELECT COUNT(*),SUM(OnTimeFlag),AVG(ActualLeadTimeDays) FROM tableau_supplier WHERE OrderStatus="Received"').fetchone()
pending=conn.execute('SELECT COUNT(*) FROM tableau_supplier WHERE OrderStatus="Pending"').fetchone()[0]
metrics={
 'dataset_type':'Synthetic portfolio case study (not real pharmacy operations)',
 'period':'2025-06-01 to 2026-08-31','transactions':conn.execute('SELECT COUNT(*) FROM dispensing_transactions').fetchone()[0],
 'stores':5,'medicines':15,'daily_inventory_snapshots':q[5],
 'dispensed_units':q[0], 'revenue_usd':round(q[1],2),'cogs_usd':round(q[2],2),'gross_profit_usd':round(q[3],2),
 'gross_margin_pct':round(100*q[3]/q[1],2),'stockout_store_medicine_days':q[4],
 'stockout_rate_pct':round(100*q[4]/q[5],3),'below_reorder_store_medicine_days':q[6],
 'below_reorder_rate_pct':round(100*q[6]/q[5],3), 'fulfilled_units':q[7],'requested_units':q[8],
 'unfulfilled_units':q[9], 'demand_fulfillment_pct':round(100*q[7]/q[8],3),
 'estimated_lost_sales_usd':round(q[10],2),'estimated_lost_sales_note':'Synthetic estimate, not observed lost revenue',
 'latest_inventory_date':'2026-08-31','latest_inventory_value_usd':round(latest[0],2),'latest_onhand_units':latest[1],
 'completed_purchase_orders':sup[0],'on_time_purchase_orders':sup[1],
 'supplier_on_time_pct':round(100*sup[1]/sup[0],2),'avg_delivery_lead_days':round(sup[2],2),
 'pending_purchase_orders':pending
}
(ANA/'kpi_results.json').write_text(json.dumps(metrics,indent=2),encoding='utf8')
with (ANA/'kpi_results.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['KPI','Value']);w.writerows((k,v) for k,v in metrics.items())
print(json.dumps(metrics,indent=2))
conn.close()
