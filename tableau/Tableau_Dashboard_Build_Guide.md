# Tableau — optional expansion guide

This guide provides a **plan for additional Tableau inventory and supplier dashboards**, not a description of the currently published Tableau workbook. The working `PharmaPulse_Sales_Tableau_Window_Fixed_v2.twbx` file already has three **sales/dispensing** dashboards and was opened and published in Tableau Public by the project author. See [`README.md`](README.md) for the working workbook. Inventory and supplier dashboards are currently available in the Plotly HTML app, and the Tableau instructions below are future extensions.

## Connect your CSV

1. Open Tableau Public / Tableau Desktop → **Connect → Text File**.
2. Pick `data/tableau_fact_daily.csv` from this project.
3. Verify `Date = Date`, `YearMonth = String`, `StoreName`, `ProductCategory`, `DrugName` are dimensions, and USD/flags are measures.
4. Create calculated fields from `Tableau_Calculated_Fields.md`.
5. **Do not join the transaction rows directly to the daily fact**. Start with one table. Add `data/tableau_supplier.csv` as its own data source for supplier charts.

## Dashboard 1: Inventory Overview

**Recommended size:** 1400×900; layout 2×2 sheets with KPI cards on top; use dark/white consistent formatting.

| Worksheet | Columns | Rows | Marks | Important note |
|---|---|---|---|---|
| Inventory Value by Store | `SUM(InventoryValueUSD)` | StoreName | Horizontal bar | Filter `Date` to **2026-08-31**, or build a date-context-aware latest value calc |
| Units on Hand by Category | ProductCategory | `SUM(ClosingStock)` | Vertical bar | Filter to one snapshot date |
| Low Stock by Store | `SUM(BelowReorderFlag)` | StoreName | Horizontal bar | Full historical range; not unique products |
| Stockout by Month | YearMonth | `SUM(StockoutFlag)` | Bar / line | Count of store-product-days with zero closing stock |

**KPI cards:** Latest inventory value, latest units on hand, historical stockout %, historical below-reorder %.

**Important:** Do not sum `InventoryValueUSD` across all 457 days; that would be a meaningless accumulated inventory valuation. Use the date-filtered sum.

## Dashboard 2: Dispensing & Revenue

| Worksheet | Columns | Rows | Marks | Purpose |
|---|---|---|---|---|
| Revenue trend | YearMonth | `SUM(RevenueUSD)` | Line | Compare months |
| Gross profit trend | YearMonth | `SUM(GrossProfitUSD)` | Line | Compare month-to-month profit |
| Revenue by category | `SUM(RevenueUSD)` | ProductCategory | Bar | Category contribution |
| Top products | `SUM(RevenueUSD)` | DrugName | Horizontal bar | Top 10 synthetic product identifiers |

**KPI cards:** `SUM(DispensedQuantity)`, `SUM(RevenueUSD)`, `SUM(GrossProfitUSD)`, **Gross margin %**.

**Analysis extension:** Add MoM revenue growth and calculate average modeled transaction value. All financial figures are fictional pricing scenarios.

## Dashboard 3: Risk & Replenishment

| Worksheet | Columns | Rows | Marks | Purpose |
|---|---|---|---|---|
| Store × category stockouts | ProductCategory | StoreName | Square heat map, color `SUM(StockoutFlag)` | Locate exposure |
| Unmet demand trend | YearMonth | `SUM(UnfulfilledUnits)` | Line | Scenario unmet units |
| Below-reorder trend | YearMonth | `SUM(BelowReorderFlag)` | Line | Inventory early warning |
| Supplier on-time % | SupplierName | On-time % | Bar | Separate **tableau_supplier.csv** source; filter to Received |

**KPI cards:** Stockout days, below-reorder days, demand fulfillment %, supplier on-time %.

**Analysis extension:** Add the `[p Days of Cover Threshold]` parameter and a calculated risk label.

## Filters and interactions

1. Add **StoreName** (multiple values), **ProductCategory** (multiple values), and **Date / YearMonth** to each dashboard.
2. Set filters to apply to **all worksheets using the same data source**. Supplier worksheets need their own corresponding filters because they use the separate supplier table.
3. Enable **Use as Filter** on store and category charts to cross-filter the other worksheets where appropriate.
4. Add tooltip details: record count, revenue, stockouts and ratio definitions.
5. Display currency as USD, ratios as percentages, and source notes identifying all content as simulated.
6. Test a filtered location: Riverside stockout days should be **58** across all dates when no other filters are set.
7. Test the dashboard-wide stockout rate: **0.554%** with all filters cleared.

## QA / sign-off

- Compare KPIs against `analysis/kpi_results.json`.
- Make sure historical inventory values are never incorrectly summed as stock value.
- Ensure no multiplying joins to dispensing transactions/purchase orders.
- Verify one store and one product filter, before and after reset.
- Verify line-chart months are chronological.
- Open and save the `.twbx` in Tableau Desktop/Public before uploading it to GitHub or Tableau Public.
