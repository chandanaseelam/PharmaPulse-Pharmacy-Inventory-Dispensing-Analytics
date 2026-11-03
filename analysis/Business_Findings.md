# Findings and recommendations — simulated pharmacy portfolio case

**Coverage:** June 1, 2025 – August 31, 2026 (15 months, 457 days, 5 stores, 15 anonymous synthetic products). Every number below is computed from the included generated data.

## Executive overview

- **49,889 units dispensed** in 27,314 synthetic transaction events, generating **$661,172.04 in modeled sales** and **$218,493.34 in modeled gross profit**, or a **33.05% gross margin**. Revenue/margin cannot be interpreted as actual financial performance because pricing and transaction-level events are simulated.
- **190 store–medicine–days had zero closing stock** (0.554% of 34,275 inventory day records), while **3,629 store–medicine–days fell below reorder threshold** (10.588%). This reveals a broad early-warning population, not merely outright zero-stock events.
- **49,889 of 50,267 modeled requested units** were fulfilled (**99.248%**), leaving **378 simulated unmet units**. These unfulfilled requests were generated as an assumption on stockout days, not observed demand.
- Of **401 received simulated purchase orders**, **214 arrived on/before expected date** (53.37% on-time). Ten additional synthetic orders remain pending at the end of the reporting window.
- Closing inventory on **August 31, 2026** totaled **6,760 units**, worth **$61,340.50** at modeled unit costs.

## Finding 1 — Riverside has the most stockout exposure

Riverside Pharmacy recorded **58 stockout days** (30.5% of the 190), at a **0.846% stockout rate**. Central had 51 (0.744%), Northpoint 42 (0.613%), Southgate 22 (0.321%), and Eastside 17 (0.248%).

**Action to evaluate:** inspect location-specific reorder thresholds and delivery lead times, starting with Riverside; compare with the lower-risk Eastside branch. **Not established:** shortages were caused by a particular supplier or staffing issue.

## Finding 2 — Low-stock flags are much more common than zero stock

There were **3,629 below-reorder records** versus 190 zero-closing-stock records. A stockout dashboard alone would miss much of the advance-warning signal.

**Action to evaluate:** prioritize a risk table based on `BelowReorderFlag`, `EstimatedDaysOfCover`, and current closing balance, with an easy date/store filter.

## Finding 3 — Sales contribution differs from availability exposure

Northpoint's **$135,615.83** modeled revenue was the largest among branches; Riverside generated **$132,438.45** while having the most stockout days. Revenue ranking does not, by itself, explain availability differences.

**Action to evaluate:** show revenue, stockout rate, and demand fulfillment side by side rather than ranking locations on a single KPI.

## Finding 4 — Supplier timelines warrant review within this scenario

Simulated on-time delivery was **53.37% overall**, with Supplier D at **46.97%** (31/66) and Supplier B at **60.92%** (53/87). These figures reflect the generated lead-time assumptions.

**Action to evaluate:** explore a higher service-level scenario and adjust expected lead-time assumptions to see how reorder buffers might change. Do not make real supplier selection decisions based on this fictitious ranking.

## Finding 5 — The first simulated month is an outlier for stockouts

June 2025 contributed **72 of 190** stockout store-product-days (37.9% of the total), with a June stockout rate of **3.2%**. The generation period begins June 1, so initialization assumptions may create early-period effects.

**Action to evaluate:** use June as a baseline sensitivity check, compare subsequent periods, and avoid presenting it as proof of actual seasonal disruption.

## What is not demonstrated

This dataset does not prove that a real business lost $5,968.15 in sales, that purchase-order interventions reduced stockouts, or that pharmacy operations improved after the analysis. An experimental rollout and independently measured before/after period would be needed for such claims.
