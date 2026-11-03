"""Reproducible synthetic pharmacy data expansion. Source of truth = supplied daily inventory CSV.
No real patient or pharmacy data. Seed=20261026. Run from project root: python scripts/build_data.py PATH_TO_ORIGINAL
"""
from __future__ import annotations
import csv, json, random, shutil, collections, math, sys
from datetime import date,timedelta,datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; DATA.mkdir(parents=True,exist_ok=True)
R=random.Random(20261026)
SRC=Path(sys.argv[1]) if len(sys.argv)>1 else DATA/'inventory_snapshots_daily.csv'
if not SRC.exists(): raise FileNotFoundError(SRC)
ORIGINAL=DATA/'inventory_snapshots_daily.csv'
if SRC.resolve()!=ORIGINAL.resolve(): shutil.copyfile(SRC,ORIGINAL)

def read_csv(p):
  with open(p,newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def write_csv(name,rows,cols=None):
  p=DATA/name
  if cols is None: cols=list(rows[0])
  with open(p,'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');w.writeheader();w.writerows(rows)
  return p

def money(x): return f'{x:.2f}'

inventory=read_csv(ORIGINAL)
inventory.sort(key=lambda r:(r['SnapshotDate'],r['StoreID'],r['DrugID']))
assert len(inventory)==34275
stores=[{'StoreID':f'STR{i:03d}','StoreName':name,'Region':region,'StoreType':typ} for i,(name,region,typ) in enumerate([
 ('Central Pharmacy','Central','Urban'),('Riverside Pharmacy','West','Suburban'),('Eastside Pharmacy','East','Urban'),('Northpoint Pharmacy','North','Suburban'),('Southgate Pharmacy','South','Urban')],1)]
write_csv('dim_stores.csv',stores)
suppliers=[{'SupplierID':f'SUP{i:03d}','SupplierName':name,'TargetLeadTimeDays':tgt} for i,(name,tgt) in enumerate([('Supplier A',6),('Supplier B',7),('Supplier C',5),('Supplier D',8),('Supplier E',9)],1)]
write_csv('dim_suppliers.csv',suppliers)
costs={}
for r in inventory:
  q=int(r['ClosingStock'])
  if q>0 and r['DrugID'] not in costs:
    costs[r['DrugID']]=round(float(r['ClosingInventoryValueUSD'])/q,2)
assert len(costs)==15
cats=['Routine Care','Wellness','Seasonal','Preventive Care','Specialty']
drugs=[]
for i,drug in enumerate(sorted(costs)):
  cost=costs[drug]
  retail=round(cost*(1.38+0.06*(i%5)),2)
  sup=suppliers[i%5]['SupplierID']
  drugs.append({'DrugID':drug,'DrugName':f'Medicine {i+1:02d} (Synthetic)','ProductCategory':cats[i%5], 'UnitCostUSD':money(cost),'UnitPriceUSD':money(retail),'SupplierID':sup,'ReorderLeadTimeDays':suppliers[i%5]['TargetLeadTimeDays']})
write_csv('dim_drugs.csv',drugs)
bydrug={r['DrugID']:r for r in drugs}
bystore={r['StoreID']:r for r in stores}
bysupplier={r['SupplierID']:r for r in suppliers}

# Split exact daily quantities into 27,314 distinct synthetic transaction rows.
positive=[(i,int(r['DispensedQuantity'])) for i,r in enumerate(inventory) if int(r['DispensedQuantity'])>0]
TARGET_TRANSACTIONS=27314
assert len(positive) <= TARGET_TRANSACTIONS <= sum(q for _,q in positive)
alloc=[i for i,q in positive for j in range(q-1)]
R.shuffle(alloc)
extra=collections.Counter(alloc[:TARGET_TRANSACTIONS-len(positive)])
transactions=[]; by_daily_revenue=collections.defaultdict(float); by_daily_cogs=collections.defaultdict(float); daily_counts=collections.Counter()
for i,q in positive:
  r=inventory[i]; k=1+extra[i]
  splits=sorted(R.sample(range(1,q),k-1)) if k>1 else []
  qtyparts=[b-a for a,b in zip([0]+splits,splits+[q])]
  assert sum(qtyparts)==q
  p=bydrug[r['DrugID']]; cost=float(p['UnitCostUSD']); price=float(p['UnitPriceUSD'])
  key=(r['SnapshotDate'],r['StoreID'],r['DrugID'])
  for qty in qtyparts:
    n=len(transactions)+1
    hour=9+(n*7)%12; minute=(n*13)%60
    gross=round(qty*price,2); cogs=round(qty*cost,2)
    transactions.append({'TransactionID':f'TXN{n:06d}','DispensedAt':f"{r['SnapshotDate']} {hour:02d}:{minute:02d}:00",'DispenseDate':r['SnapshotDate'],'StoreID':r['StoreID'],'DrugID':r['DrugID'],'UnitsDispensed':qty,'UnitSellingPriceUSD':money(price),'UnitCostUSD':money(cost),'RevenueUSD':money(gross),'COGSUSD':money(cogs),'GrossProfitUSD':money(round(gross-cogs,2))})
    by_daily_revenue[key]+=gross;by_daily_cogs[key]+=cogs;daily_counts[key]+=1
assert len(transactions)==TARGET_TRANSACTIONS
write_csv('dispensing_transactions.csv',transactions)

orders=[]; delivered=collections.defaultdict(int)
for r in inventory:
  recv=int(r['ReceivedQuantity'])
  if recv==0: continue
  p=bydrug[r['DrugID']]; sup=bysupplier[p['SupplierID']]
  actual=date.fromisoformat(r['SnapshotDate'])
  target=int(sup['TargetLeadTimeDays'])
  lag=max(2,target+R.choice([-2,-1,0,0,0,1,2,3,5]))
  ordered=actual-timedelta(days=lag); expected=ordered+timedelta(days=target)
  n=len(orders)+1
  orders.append({'PurchaseOrderID':f'PO{n:05d}','StoreID':r['StoreID'],'DrugID':r['DrugID'],'SupplierID':p['SupplierID'],'OrderDate':str(ordered),'ExpectedDeliveryDate':str(expected),'ActualDeliveryDate':str(actual),'OrderQuantity':recv,'ReceivedQuantity':recv,'OrderStatus':'Received','ActualLeadTimeDays':lag,'OnTimeFlag':int(actual<=expected),'OrderValueUSD':money(recv*float(p['UnitCostUSD']))})
  delivered[(r['SnapshotDate'],r['StoreID'],r['DrugID'])]+=recv
assert len(orders)==401
# ten pending orders, tracked as of the final inventory snapshot; not counted as received
for j in range(10):
  s=stores[j%5];p=drugs[(j*2+1)%15]; sup=bysupplier[p['SupplierID']]
  ordered=date(2026,8,23)+timedelta(days=j%7)
  expected=ordered+timedelta(days=int(sup['TargetLeadTimeDays'])+6)
  orders.append({'PurchaseOrderID':f'PO{len(orders)+1:05d}','StoreID':s['StoreID'],'DrugID':p['DrugID'],'SupplierID':p['SupplierID'],'OrderDate':str(ordered),'ExpectedDeliveryDate':str(expected),'ActualDeliveryDate':'','OrderQuantity':(j%4+1)*40,'ReceivedQuantity':0,'OrderStatus':'Pending','ActualLeadTimeDays':'','OnTimeFlag':'','OrderValueUSD':money((j%4+1)*40*float(p['UnitCostUSD']))})
write_csv('purchase_orders.csv',orders)

# One demand row per store/medicine/day; shortage is a clear *simulation assumption*.
demand=[];daily=[]
for r in inventory:
  day=r['SnapshotDate'];key=(day,r['StoreID'],r['DrugID'])
  stock=int(r['ClosingStock']); qty=int(r['DispensedQuantity'])
  lost=(1+(sum(map(ord,day+r['StoreID']+r['DrugID']))%3)) if stock==0 else 0
  requested=qty+lost
  demand.append({'DemandDate':day,'StoreID':r['StoreID'],'DrugID':r['DrugID'],'RequestedUnits':requested,'FulfilledUnits':qty,'UnfulfilledUnits':lost,'FulfillmentStatus':'Unfulfilled' if lost else 'Fully Fulfilled'})
  p=bydrug[r['DrugID']]; s=bystore[r['StoreID']]; price=float(p['UnitPriceUSD']); cost=float(p['UnitCostUSD']);revenue=round(qty*price,2);cogs=round(qty*cost,2)
  assert math.isclose(revenue,by_daily_revenue[key],abs_tol=0.0001)
  assert math.isclose(cogs,by_daily_cogs[key],abs_tol=0.0001)
  daily.append({
    'Date':day,'YearMonth':day[:7],'Year':int(day[:4]),'MonthNumber':int(day[5:7]),'StoreID':r['StoreID'],'StoreName':s['StoreName'],'Region':s['Region'], 'StoreType':s['StoreType'],
    'DrugID':r['DrugID'],'DrugName':p['DrugName'],'ProductCategory':p['ProductCategory'],'SupplierID':p['SupplierID'],
    'OpeningStock':r['OpeningStock'],'ReceivedQuantity':r['ReceivedQuantity'],'DispensedQuantity':qty,'AdjustmentQuantity':r['AdjustmentQuantity'],'ClosingStock':stock,
    'ReorderLevel':r['ReorderLevel'],'StockStatus':r['StockStatus'],'StockoutFlag':int(stock==0),'BelowReorderFlag':int(stock<int(r['ReorderLevel'])),'EstimatedDaysOfCover':r['EstimatedDaysOfCover'],
    'InventoryValueUSD':r['ClosingInventoryValueUSD'],'RequestedUnits':requested,'FulfilledUnits':qty,'UnfulfilledUnits':lost,
    'EstimatedLostSalesUSD':money(lost*price),'TransactionCount':daily_counts[key],'UnitPriceUSD':money(price),'UnitCostUSD':money(cost),
    'RevenueUSD':money(revenue),'COGSUSD':money(cogs),'GrossProfitUSD':money(revenue-cogs)
  })
write_csv('demand_daily.csv',demand)
write_csv('tableau_fact_daily.csv',daily)

transactions_enriched=[]
for x in transactions:
 s=bystore[x['StoreID']];p=bydrug[x['DrugID']]
 transactions_enriched.append({**x,'StoreName':s['StoreName'],'Region':s['Region'],'DrugName':p['DrugName'],'ProductCategory':p['ProductCategory'],'YearMonth':x['DispenseDate'][:7]})
write_csv('tableau_transactions.csv',transactions_enriched)
po_enriched=[]
for o in orders:
 s=bystore[o['StoreID']];p=bydrug[o['DrugID']];sup=bysupplier[o['SupplierID']]
 po_enriched.append({**o,'StoreName':s['StoreName'],'DrugName':p['DrugName'],'ProductCategory':p['ProductCategory'],'SupplierName':sup['SupplierName'],'TargetLeadTimeDays':sup['TargetLeadTimeDays']})
write_csv('tableau_supplier.csv',po_enriched)
# cleaning practice file is intentionally NOT a source for reporting.
practice=[dict(x) for x in transactions_enriched[:80]]
practice[3]['DrugID']='';practice[9]['RevenueUSD']='bad_value';practice[18]['StoreID']='STR999'
practice[23]['UnitsDispensed']='-2';practice.append(dict(practice[6]))
write_csv('practice_dirty_transactions.csv',practice)

summary={
 'source_inventory_records':len(inventory),'inventory_dates':len({x['SnapshotDate'] for x in inventory}), 'date_range':[inventory[0]['SnapshotDate'],inventory[-1]['SnapshotDate']],
 'dispensing_transactions':len(transactions),'dispensed_units':sum(int(x['DispensedQuantity']) for x in inventory),
 'inventory_receipts':sum(int(x['ReceivedQuantity']) for x in inventory),'purchase_orders':len(orders), 'received_orders':401,'pending_orders':10,
 'inventory_snapshots':len(daily), 'stores':len(stores),'medicines':len(drugs),
 'stockout_store_medicine_days':sum(x['StockoutFlag'] for x in daily),
 'below_reorder_store_medicine_days':sum(x['BelowReorderFlag'] for x in daily),
 'requested_units':sum(x['RequestedUnits'] for x in daily), 'unfulfilled_units':sum(x['UnfulfilledUnits'] for x in daily),
 'revenue_usd':money(sum(float(x['RevenueUSD']) for x in daily)), 'gross_profit_usd':money(sum(float(x['GrossProfitUSD']) for x in daily)),
 'closing_inventory_value_usd':money(sum(float(x['InventoryValueUSD']) for x in daily if x['Date']==daily[-1]['Date'])),
 'synthetic_note':'All augmented transactions, sales prices, demand requests, supplier delivery timing, and business names are SIMULATED; daily inventory movements are preserved from the previously generated input file.'
}
(ROOT/'analysis'/'generation_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
