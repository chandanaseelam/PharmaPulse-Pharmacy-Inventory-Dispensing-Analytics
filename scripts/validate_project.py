"""Check relational consistency and metric reconciliation. Uses only Python stdlib."""
import csv, json, collections, math, sys
from pathlib import Path
from datetime import date
R=Path(__file__).resolve().parents[1]
def read(name):
 with (R/'data'/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
snap=read('inventory_snapshots_daily.csv');fact=read('tableau_fact_daily.csv');txn=read('dispensing_transactions.csv');po=read('purchase_orders.csv');dem=read('demand_daily.csv');prod=read('dim_drugs.csv');store=read('dim_stores.csv');sup=read('dim_suppliers.csv')
checks=[]
def check(label,ok):
 checks.append((label,bool(ok)))
 if not ok: print('FAIL:',label)
keys=lambda x:(x['Date'],x['StoreID'],x['DrugID'])
validdrug={x['DrugID'] for x in prod};validstore={x['StoreID'] for x in store};validsup={x['SupplierID'] for x in sup}
check('34,275 inventory fact snapshots',len(snap)==len(fact)==34275)
check('75 store-product combinations each of 457 days',len({x['SnapshotDate'] for x in snap})==457 and len({(x['StoreID'],x['DrugID']) for x in snap})==75)
check('Unique store-medicine-day keys',len({keys(x) for x in fact})==len(fact))
check('Unique transaction IDs',len({x['TransactionID'] for x in txn})==len(txn)==27314)
check('Unique purchase order IDs',len({x['PurchaseOrderID'] for x in po})==len(po)==411)
check('All foreign keys exist',all(x['DrugID'] in validdrug and x['StoreID'] in validstore for x in fact+txn+po+dem) and all(x['SupplierID'] in validsup for x in po))
check('Daily stock equation',all(int(x['OpeningStock'])+int(x['ReceivedQuantity'])+int(x['AdjustmentQuantity'])-int(x['DispensedQuantity'])==int(x['ClosingStock']) for x in snap))
check('No negative closing stock',all(int(x['ClosingStock'])>=0 for x in snap))
check('Stockout flag correct',all(int(x['StockoutFlag'])==(int(x['ClosingStock'])==0) for x in fact))
check('Below-reorder flag correct',all(int(x['BelowReorderFlag'])==(int(x['ClosingStock'])<int(x['ReorderLevel'])) for x in fact))
check('Dispensed units sum = 49,889',sum(int(x['UnitsDispensed']) for x in txn)==sum(int(x['DispensedQuantity']) for x in fact)==49889)
check('Transactions never zero/negative',all(int(x['UnitsDispensed'])>0 for x in txn))
txnqty=collections.Counter();txnrev=collections.defaultdict(float)
for t in txn:
 k=(t['DispenseDate'],t['StoreID'],t['DrugID']);txnqty[k]+=int(t['UnitsDispensed']);txnrev[k]+=float(t['RevenueUSD'])
check('All daily transaction quantities equal inventory dispensing',all(txnqty[keys(f)]==int(f['DispensedQuantity']) for f in fact))
check('Revenue reconciliation to cents',all(abs(txnrev[keys(f)]-float(f['RevenueUSD']))<0.001 for f in fact))
check('Revenue = COGS + gross profit',all(abs(float(t['RevenueUSD'])-float(t['COGSUSD'])-float(t['GrossProfitUSD']))<0.001 for t in txn))
check('Demand requested = fulfilled + unfulfilled',all(int(x['RequestedUnits'])==int(x['FulfilledUnits'])+int(x['UnfulfilledUnits']) for x in dem))
check('Demand daily aligned to inventory and no overfulfillment',all(int(x['FulfilledUnits'])==int(f['DispensedQuantity']) and int(x['RequestedUnits'])>=int(f['DispensedQuantity']) for x,f in zip(dem,fact)))
rcv=collections.Counter()
for o in po:
 if o['OrderStatus']=='Received':rcv[(o['ActualDeliveryDate'],o['StoreID'],o['DrugID'])]+=int(o['ReceivedQuantity'])
check('Every receipt reconciles to a received purchase order',all(rcv[keys(f)]==int(f['ReceivedQuantity']) for f in fact))
check('All pending purchase orders have zero receipts',all(int(o['ReceivedQuantity'])==0 and o['ActualDeliveryDate']=='' for o in po if o['OrderStatus']=='Pending'))
check('Stock movements join continuously by store and medicine',all(int(a['ClosingStock'])==int(b['OpeningStock']) for seq in (None,) for a,b in ((l[i],l[i+1]) for l in ([x for x in snap if x['StoreID']==s and x['DrugID']==d] for s in sorted(validstore) for d in sorted(validdrug)) for i in range(len(l)-1))))
check('No missing values in reporting facts',all(all(str(v).strip() for v in x.values()) for x in fact))
status='PASSED' if all(ok for _,ok in checks) else 'FAILED'
log=[f'PHARMACY ANALYTICS DATA VALIDATION: {status}',f'{sum(ok for _,ok in checks)}/{len(checks)} checks passed','',*(('PASS' if ok else 'FAIL')+'  '+label for label,ok in checks),'', 'NOTE: Data is synthetic; validation establishes internal consistency, not real-world provenance.']
(R/'analysis'/'validation_report.txt').write_text('\n'.join(log)+'\n',encoding='utf8')
print('\n'.join(log))
if status!='PASSED':sys.exit(1)
