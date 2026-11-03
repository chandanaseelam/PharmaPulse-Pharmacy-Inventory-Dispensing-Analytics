# Tableau calculated fields — pharmacy business intelligence

**Primary connection:** `data/tableau_fact_daily.csv`. One row = a single `Date × StoreID × DrugID`. In Tableau, make `Date` a **Date**, `YearMonth` a **String dimension**, flags/quantities **integer measures**, and USD fields **numeric currency**. Table data is synthetic.

Create these via **Analysis → Create Calculated Field** (copy formula only, no Markdown fences):

## 1. Gross margin %

```tableau
IF SUM([RevenueUSD]) = 0 THEN 0
ELSE 100 * SUM([GrossProfitUSD]) / SUM([RevenueUSD]) END
```

Display as number with two decimals and a `%` suffix, **not** as Tableau's Percentage formatting (formula already multiplies by 100).

## 2. Stockout rate %

```tableau
100 * SUM([StockoutFlag]) / COUNT([StockoutFlag])
```

A zero closing-stock snapshot counts once per date/store/product.

## 3. Below-reorder rate %

```tableau
100 * SUM([BelowReorderFlag]) / COUNT([BelowReorderFlag])
```

## 4. Demand fulfillment rate %

```tableau
IF SUM([RequestedUnits]) = 0 THEN 0
ELSE 100 * SUM([FulfilledUnits]) / SUM([RequestedUnits]) END
```

## 5. Average modeled transaction value

```tableau
IF SUM([TransactionCount]) = 0 THEN 0
ELSE SUM([RevenueUSD]) / SUM([TransactionCount]) END
```

## 6. Month-over-month revenue growth % (table calculation)

```tableau
IF ISNULL(LOOKUP(SUM([RevenueUSD]), -1))
OR LOOKUP(SUM([RevenueUSD]), -1) = 0 THEN NULL
ELSE 100 * (SUM([RevenueUSD]) - LOOKUP(SUM([RevenueUSD]), -1))
     / ABS(LOOKUP(SUM([RevenueUSD]), -1)) END
```

Put discrete `YearMonth` (ascending) on Columns, then configure **Compute Using → Table Across**. This is a *table calculation* and depends on sort/order and worksheet partitioning.

## 7. Low-stock risk label (row-level)

```tableau
IF [ClosingStock] = 0 THEN "Out of stock"
ELSEIF [ClosingStock] < [ReorderLevel] THEN "Below reorder"
ELSE "At or above reorder" END
```

## 8. Revenue per dispensed unit

```tableau
IF SUM([DispensedQuantity]) = 0 THEN NULL
ELSE SUM([RevenueUSD]) / SUM([DispensedQuantity]) END
```

## 9. Fixed store-level unmet units (LOD example)

```tableau
{ FIXED [StoreID] : SUM([UnfulfilledUnits]) }
```

**Important:** FIXED LOD calculations ignore ordinary dimension filters unless they are added as context filters; this value repeats on each row, so do not SUM it across rows. In a store-level view use `MIN([Fixed store-level unmet units])` or `ATTR`.

## 10. Risk threshold parameter

Create an **Integer parameter** `[p Days of Cover Threshold]` with current value `14` and range `0–90`, step `1`. Then create:

```tableau
IF [BelowReorderFlag] = 1
AND [EstimatedDaysOfCover] <= [p Days of Cover Threshold]
THEN "Priority review" ELSE "Monitor" END
```

**Data qualification:** `EstimatedDaysOfCover` is a scenario estimate. It must not be represented as a proven future exhaustion date.

## 11. Latest inventory value (filter-aware, from primary fact)

Preferred for a dashboard controlled by date filters:

```tableau
IF [Date] = { FIXED : MAX([Date]) }
THEN [InventoryValueUSD] ELSE 0 END
```

Then show `SUM([Latest Inventory Value (filter-aware)])`. **Critical:** The FIXED LOD generally evaluates before ordinary dimension filters. If filters should redefine the latest snapshot date, add the relevant date/store/product filters to **Context** or use an appropriate separate scaffold. The experimental packaged workbook instead uses `LatestInventoryValueUSD`, which is explicitly fixed to **2026-08-31**; it should not be interpreted as a dynamically filtered latest date.

## 12. Simulated supplier on-time delivery % (second data source)

Connect `data/tableau_supplier.csv` **as a separate data source**. Filter `OrderStatus` to `Received`, then create:

```tableau
IF COUNT([OnTimeFlag]) = 0 THEN NULL
ELSE 100 * SUM([OnTimeFlag]) / COUNT([OnTimeFlag]) END
```

The `OnTimeFlag` is missing for Pending orders; never treat Pending as late or on time. Separate supplier table avoids a fanout join with daily fact.

## Audit values (all-store/all-time)

| KPI | Expected |
|---|---:|
| Stockout rate | 0.554% |
| Below-reorder rate | 10.588% |
| Gross margin | 33.05% |
| Demand fulfillment | 99.248% |
| Supplier on-time | 53.37% |
| Latest inventory (2026-08-31) | $61,340.50 |

**Formatting:** Since formulas multiply by 100, use Number (2 or 3 decimals) with a literal `%` suffix. If instead using native Tableau Percentage style, remove `100 *`.
