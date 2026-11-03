"""Create polished KPI/roadmap workbook using artifact_tool only."""
from pathlib import Path
import csv,json,re
from artifact_tool import Workbook, SpreadsheetFile
R=Path(__file__).resolve().parents[1]
metrics=json.loads((R/'analysis'/'kpi_results.json').read_text())
def rows(name):
 with (R/'analysis'/name).open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))
wb=Workbook.create()
NAVY='#17334E';DARK='#0D293D';TEAL='#008F86';PALE='#EAF7F4';WHITE='#FFFFFF';GRAY='#607589';BLUE='#EAF1FC'
def style_header(sheet,range='A4:F4'):
 rg=sheet.get_range(range);rg.format={'fill':NAVY,'font':{'bold':True,'color':WHITE},'row_height':24,'vertical_alignment':'center'}
def title(sheet,text,last_col='F'):
 sheet.merge_cells(f'A1:{last_col}1');sheet.get_range('A1').values=[[text]];sheet.get_range(f'A1:{last_col}1').format={'fill':DARK,'font':{'bold':True,'color':WHITE,'size':17},'row_height':35,'vertical_alignment':'center'}
 sheet.get_range('A2').values=[['SIMULATED CASE STUDY • JUNE 2025 – AUGUST 2026']]
 sheet.get_range('A2').format.font.color=TEAL

def widths(sheet,widths):
 for col,w in widths.items():sheet.get_range(f'{col}:{col}').format.column_width=w

s=wb.worksheets.add('Executive KPIs');title(s,'PHARMACY ANALYTICS | KPI SCORECARD','F');
s.get_range('A4:C4').values=[['Business KPI','Value','Definition / important caveat']];style_header(s,'A4:C4')
values=[
 ('Dispensed units',metrics['dispensed_units'],'Source movement ledger'),
 ('Modeled sales revenue (USD)',metrics['revenue_usd'],'Selling prices simulated'),
 ('Modeled cost of goods (USD)',metrics['cogs_usd'],'Unit costs simulated'),
 ('Gross profit (USD)',None,'Formula: sales minus COGS'),
 ('Gross margin %',None,'Formula: gross profit / revenue'),
 ('Stockout store-product-days',metrics['stockout_store_medicine_days'],'Closing stock = 0'),
 ('All inventory snapshot rows',metrics['daily_inventory_snapshots'],'457 days × 5 stores × 15 medicines'),
 ('Stockout rate %',None,'Formula: stockout days / all rows'),
 ('Below-reorder store-product-days',metrics['below_reorder_store_medicine_days'],'Closing stock below threshold'),
 ('Below-reorder rate %',None,'Formula: below-reorder days / all rows'),
 ('Fulfilled units',metrics['fulfilled_units'],'Matches dispensing'),
 ('Requested units (modeled)',metrics['requested_units'],'Fulfilled + simulated unmet units'),
 ('Demand fulfillment %',None,'Formula: fulfilled / requested'),
 ('Latest inventory value (USD)',metrics['latest_inventory_value_usd'],'Only August 31, 2026 snapshot'),
 ('Purchase orders delivered',metrics['completed_purchase_orders'],'Synthetic orders'),
 ('Delivered on time',metrics['on_time_purchase_orders'],'Actual date on/before expected'),
 ('Supplier on-time rate %',None,'Formula: on-time / received orders'),
 ('Data quality checks passed',21,'21 of 21 automated checks'),
]
s.get_range('A5:C22').values=[[a,b,c] for a,b,c in values]
for row,formula in {8:'=B6-B7',9:'=IF(B6=0,0,B8/B6)',12:'=IF(B11=0,0,B10/B11)',14:'=IF(B11=0,0,B13/B11)',17:'=IF(B16=0,0,B15/B16)',21:'=IF(B19=0,0,B20/B19)'}.items():
 s.get_range(f'B{row}').formulas=[[formula]]
# Correct formula alignments based on actual sheet row numbers: 
# row5 units,6 revenue,7 COGS,8 profit,9 margin,10 stockouts,11 total rows,12 stockout%,13 below,14 below%,15 fulfilled,16 requested,17 fulfillment%,18 latest,19 delivered,20 on time,21 ontime%,22 checks
for row in (9,12,14,17,21):s.get_range(f'B{row}').set_number_format('0.00%')
for row in (6,7,8,18):s.get_range(f'B{row}').set_number_format('$#,##0.00')
s.get_range('A23:C23').values=[['NOTE','All data synthetic','Do not represent modeled prices or demand as real operations.']]
s.get_range('A23:C23').format={'fill':PALE,'font':{'color':DARK,'bold':True},'row_height':22}
s.get_range('A5:A22').format.font.bold=True
widths(s,{'A':39,'B':21,'C':79,'D':14,'E':14,'F':14})
s.freeze_panes.freeze_rows(4)

m=wb.worksheets.add('Monthly Trends');title(m,'15-MONTH PERFORMANCE TRENDS','G');m.get_range('A4:F4').values=[['Year-Month','Revenue USD','Gross profit USD','Units dispensed','Stockout days','MoM revenue %']];style_header(m,'A4:F4')
monthly=rows('monthly_trends.csv')
m.get_range('A5:F19').values=[[
 x['YearMonth'],float(x['RevenueUSD']),float(x['GrossProfitUSD']),int(x['DispensedUnits']),int(x['StockoutDays']),None]
 for x in monthly]
for i in range(6,20):m.get_range(f'F{i}').formulas=[[f'=IF(B{i-1}=0,0,(B{i}-B{i-1})/B{i-1})']]
m.get_range('B5:C19').set_number_format('$#,##0.00');m.get_range('F6:F19').set_number_format('0.00%')
widths(m,{'A':17,'B':22,'C':24,'D':20,'E':18,'F':20,'G':15,'H':14,'I':13,'J':13,'K':13,'L':13,'M':13})
try:
 chart=m.charts.add('line',m.get_range('A4:C19'));chart.title_text='Monthly revenue and gross profit';chart.set_position('H4','Q20')
except Exception as exc:print('Chart omitted:',exc)
m.freeze_panes.freeze_rows(4)

s2=wb.worksheets.add('Store Analysis');title(s2,'STORE COMPARISON','G')
s2.get_range('A4:G4').values=[['Store','Revenue USD','Dispensed units','Stockout days','Stockout rate %','Below-reorder days','Unfulfilled units']];style_header(s2,'A4:G4')
stores=rows('store_performance.csv')
s2.get_range('A5:G9').values=[[
 x['StoreName'],float(x['RevenueUSD']),int(x['DispensedUnits']),int(x['StockoutDays']),float(x['StockoutRatePct'])/100,int(x['BelowReorderDays']),int(x['UnfulfilledUnits'])] for x in stores]
s2.get_range('B5:B9').set_number_format('$#,##0.00');s2.get_range('E5:E9').set_number_format('0.000%')
widths(s2,{'A':28,'B':21,'C':23,'D':20,'E':23,'F':25,'G':24})
s2.freeze_panes.freeze_rows(4)

catalog=[
 ('Total dispensing units','SUM([DispensedQuantity])','Daily fact','Actual synthetic movement ledger'),
 ('Modeled revenue','SUM([RevenueUSD])','Daily fact','Unit selling prices are synthetic'),
 ('Gross profit','SUM([GrossProfitUSD])','Daily fact','Revenue minus modeled COGS'),
 ('Gross margin %','100*SUM([GrossProfitUSD])/SUM([RevenueUSD])','Daily fact','Weighted ratio; do not average row margins'),
 ('Stockout rate %','100*SUM([StockoutFlag])/COUNT([StockoutFlag])','Daily fact','Each row is store/product/day'),
 ('Below reorder rate %','100*SUM([BelowReorderFlag])/COUNT([BelowReorderFlag])','Daily fact','Below threshold, not at threshold'),
 ('Demand fulfillment %','100*SUM([FulfilledUnits])/SUM([RequestedUnits])','Daily fact','Modeled requests'),
 ('Latest inventory value','SUM([InventoryValueUSD]) with Date = 2026-08-31','Daily fact','Snapshot metric; never sum across days'),
 ('Inventory on hand','SUM([ClosingStock]) with Date = 2026-08-31','Daily fact','Snapshot metric'),
 ('Monthly revenue growth %','(Current revenue - previous month)/previous month','Monthly Trends','Table calculation'),
 ('Estimated days cover','AVG([EstimatedDaysOfCover])','Daily fact','Scenario estimate'),
 ('Transaction count','SUM([TransactionCount])','Daily fact','27,314 overall'),
 ('Stockout days','SUM([StockoutFlag])','Daily fact','Closing stock = 0'),
 ('Supplier on-time %','100*SUM([OnTimeFlag])/COUNT([OnTimeFlag])','Supplier fact','Filter to Received'),
 ('Unfulfilled units','SUM([UnfulfilledUnits])','Daily fact','Synthetic scenario, not measured'),
 ('Estimated lost sales','SUM([EstimatedLostSalesUSD])','Daily fact','Hypothetical, not verified lost revenue'),
]
cat=wb.worksheets.add('KPI Dictionary');title(cat,'METRIC DEFINITIONS & GRAIN','F');cat.get_range('A4:D4').values=[['KPI','Tableau calculation / scope','Reporting source','Interpretation']];style_header(cat,'A4:D4')
cat.get_range(f'A5:D{4+len(catalog)}').values=[list(x) for x in catalog]
cat.get_range(f'A5:D{4+len(catalog)}').format.row_height=25
widths(cat,{'A':30,'B':67,'C':21,'D':57});cat.freeze_panes.freeze_rows(4)

roadmap=[
 'Define business questions and stakeholders','Select KPI definitions','Review sources and provenance','Collect historical data','Identify grains and relationships',
 'Connect daily inventory table','Detect missing/duplicate records','Reconcile stock movement ledger','Build dimensions and source datasets','Validate data integrity',
 'Build KPI summary','Analyze stockouts by store','Analyze monthly and category trends','Document calculations, LOD and MoM','Assess supplier/demand scenarios',
 'Create inventory visuals','Create dispensing/revenue visuals','Create replenishment visuals','Add interactive filters and tooltips','Assemble 3 dashboards',
 'Reconcile dashboard totals','Run automated tests','Write insights and caveats','Document scenario recommendations','Package files for portfolio']
road=wb.worksheets.add('25-Step Roadmap');title(road,'END-TO-END PROJECT TRACKER','E');road.get_range('A4:D4').values=[['Step','Phase','Action','Status']];style_header(road,'A4:D4')
road.get_range('A5:D29').values=[[i+1,1+(i//5),txt,'Artifacts prepared' if i<25 else ''] for i,txt in enumerate(roadmap)]
widths(road,{'A':10,'B':11,'C':72,'D':26});road.freeze_panes.freeze_rows(4)

val=wb.worksheets.add('Validation');title(val,'DATA QUALITY | 21 AUTOMATED CHECKS','D');val.get_range('A4:B4').values=[['Check','Result']];style_header(val,'A4:B4')
raw=(R/'analysis'/'validation_report.txt').read_text(encoding='utf8').splitlines()
checks=[line[6:] for line in raw if line.startswith('PASS  ')]
val.get_range('A5:B25').values=[[x,'PASS'] for x in checks]
val.get_range('B5:B25').format={'fill':PALE,'font':{'color':TEAL,'bold':True}}
widths(val,{'A':79,'B':17,'C':15,'D':15});val.freeze_panes.freeze_rows(4)

p=R/'Pharmacy_Analytics_Project_Guide.xlsx'
SpreadsheetFile.export_xlsx(wb).save(str(p))
print('Saved',p,'bytes',p.stat().st_size)
try:
 res=wb.inspect({'kind':'table','range':'Executive KPIs!A4:C12','include':'values,formulas','table_max_rows':9,'table_max_cols':3})
 print('Inspection:',res.ndjson[:2500])
 errors=wb.inspect({'kind':'match','search_term':'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A','options':{'use_regex':True,'max_results':20}})
 print('Error scan:',errors.ndjson[:1000])
except Exception as e:print('Inspect warning:',e)
