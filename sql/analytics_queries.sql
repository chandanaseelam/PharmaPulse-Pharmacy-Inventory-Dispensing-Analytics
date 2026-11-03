-- Pharmacy Inventory & Dispensing Analytics | SQLite-compatible analysis
-- All data beyond the starting daily inventory file is SIMULATED.
-- Reporting grain = one row per date x store x medicine in tableau_fact_daily.
-- Do NOT sum inventory values across days; use the most recent snapshot in scope.

-- KPI overview (all dates)
SELECT
  SUM(DispensedQuantity) AS dispensed_units,
  ROUND(SUM(RevenueUSD),2) AS sales_revenue_usd,
  ROUND(SUM(COGSUSD),2) AS cogs_usd,
  ROUND(SUM(GrossProfitUSD),2) AS gross_profit_usd,
  ROUND(100.0*SUM(GrossProfitUSD)/NULLIF(SUM(RevenueUSD),0),2) AS gross_margin_pct,
  SUM(StockoutFlag) AS stockout_store_medicine_days,
  ROUND(100.0*SUM(StockoutFlag)/COUNT(*),2) AS stockout_pct,
  SUM(BelowReorderFlag) AS below_reorder_store_medicine_days,
  ROUND(100.0*SUM(FulfilledUnits)/NULLIF(SUM(RequestedUnits),0),2) AS fulfillment_pct
FROM tableau_fact_daily;

-- Latest inventory value: aggregate ONLY the final date, not entire time-series
SELECT Date, ROUND(SUM(InventoryValueUSD),2) AS inventory_value_usd,
       SUM(ClosingStock) AS on_hand_units
FROM tableau_fact_daily
WHERE Date=(SELECT MAX(Date) FROM tableau_fact_daily)
GROUP BY Date;

-- Monthly revenue growth and margin
WITH m AS (
 SELECT YearMonth AS month, SUM(RevenueUSD) revenue, SUM(GrossProfitUSD) profit,
 SUM(DispensedQuantity) units FROM tableau_fact_daily GROUP BY YearMonth
), with_prev AS (
 SELECT *, LAG(revenue) OVER (ORDER BY month) prev_revenue FROM m
)
SELECT month, ROUND(revenue,2) revenue_usd, ROUND(profit,2) gross_profit_usd, units,
ROUND(100.0*profit/NULLIF(revenue,0),2) gross_margin_pct,
ROUND(100.0*(revenue-prev_revenue)/NULLIF(prev_revenue,0),2) mom_revenue_pct
FROM with_prev ORDER BY month;

-- Store segmentation
SELECT StoreName, SUM(DispensedQuantity) units_dispensed,
ROUND(SUM(RevenueUSD),2) revenue_usd, SUM(StockoutFlag) stockout_days,
ROUND(100.0*SUM(StockoutFlag)/COUNT(*),2) stockout_pct,
SUM(UnfulfilledUnits) unfulfilled_units
FROM tableau_fact_daily GROUP BY StoreName ORDER BY revenue_usd DESC;

-- Product/category mix
SELECT ProductCategory, SUM(DispensedQuantity) units_dispensed,
ROUND(SUM(RevenueUSD),2) revenue_usd,
ROUND(SUM(GrossProfitUSD),2) gross_profit_usd,
SUM(StockoutFlag) stockout_days
FROM tableau_fact_daily GROUP BY ProductCategory ORDER BY revenue_usd DESC;

-- Highest-revenue medicines
SELECT DrugID, DrugName, ProductCategory,
SUM(DispensedQuantity) units, ROUND(SUM(RevenueUSD),2) revenue_usd,
SUM(StockoutFlag) stockout_days FROM tableau_fact_daily
GROUP BY DrugID,DrugName,ProductCategory ORDER BY revenue_usd DESC LIMIT 10;

-- Supplier fulfillment rates (received orders only)
SELECT SupplierName, COUNT(*) received_orders,
SUM(OnTimeFlag) on_time_orders,
ROUND(100.0*SUM(OnTimeFlag)/NULLIF(COUNT(*),0),2) on_time_pct,
ROUND(AVG(ActualLeadTimeDays),2) avg_lead_days,
ROUND(SUM(OrderValueUSD),2) received_order_value_usd
FROM tableau_supplier WHERE OrderStatus='Received'
GROUP BY SupplierName ORDER BY on_time_pct ASC;

-- Store and category replenishment risk
SELECT StoreName, ProductCategory, SUM(StockoutFlag) stockout_days,
SUM(BelowReorderFlag) below_reorder_days,
SUM(UnfulfilledUnits) unmet_units,
ROUND(SUM(EstimatedLostSalesUSD),2) hypothetical_lost_sales_usd
FROM tableau_fact_daily GROUP BY StoreName,ProductCategory
ORDER BY stockout_days DESC,below_reorder_days DESC;

-- VALIDATION query: sum of transaction units must equal daily fact units
SELECT (SELECT SUM(UnitsDispensed) FROM dispensing_transactions) txn_units,
       (SELECT SUM(DispensedQuantity) FROM tableau_fact_daily) daily_units;
