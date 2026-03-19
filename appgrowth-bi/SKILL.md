---
name: appgrowth-bi
description: Query Appgrowth BI (`https://app.appgrowth.com/bi2/`) and return structured results for analysis. Use when asked to fetch dashboard/business metrics from Appgrowth BI (for example revenue by bundle, period breakdowns, cohort slices), especially when the task requires authenticated API calls with `BI_API_KEY`, tabular output, and quick summaries.
---

# Appgrowth BI

Fetch BI data from the Appgrowth BI endpoint and turn it into usable tables.
This skill is intended for use outside the appgrowth repo; repo code is used only as source-of-truth reference for available BI fields.

## Quick Workflow

1. Collect query intent and convert it into BI request parameters.
2. Run `scripts/query_bi.py` with `BI_API_KEY` from the environment.
3. Save results to a file when downstream analysis is needed.
4. Summarize key findings (totals, deltas, top segments) from the returned table.

## Run Queries

Set credentials in environment:

```bash
export BI_API_KEY="<token>"
```

Run with explicit key/value params:

```bash
uvx --with pandas --with pyarrow --with requests \
  python scripts/query_bi.py \
  --param start=30d \
  --param end=0d \
  --param by='["bundle"]' \
  --param measures='["revenue","gross_spend","installs"]' \
  --param date_column=bid_timestamp \
  --output /tmp/revenue_by_bundle_30d.parquet
```

Run with JSON params:

```bash
uvx --with pandas --with pyarrow --with requests \
  python scripts/query_bi.py \
  --params-json '{"start":"30d","end":"0d","by":["bundle"],"measures":["revenue","gross_spend","installs"],"date_column":"bid_timestamp"}' \
  --format parquet
```

## Parameter Guidance

- Use BI2-style parameters:
  - `start`, `end`
  - `by`, `pivot`, `metric` (pivot metric)
  - `measures`, `events`, `event_metrics`, `action_metrics`
  - `filter_data`, `query`, `having`
  - `date_column` (`bid_timestamp` or `timestamp`)
  - `concentrate_dims`, `concentrate_measure`, `concentrate_mass`
- Prefer `start=30d`, `end=0d` for “last 30d” unless explicit dates are given.
- Use `by` and `measures` as JSON lists.
- Filter dimensions in `query` with SQL-style expressions when the field is available in BI filters, for example:
  - `query="flavor IN ('flavor1', 'flavor2')"`
- Filter post-aggregation/frame values in `having` only for local dataframe filtering after the API response, for example:
  - `having="impressions > 0 and clicks > 0"`
- Do not use `having` for backend dimension filters like `role`, `flavor`, `bundle`, or `country`; put those in `query` instead.
- Include fields referenced by `query` or `having` in `filter_data` so BI exposes them for filtering, for example:
  - `filter_data=['flavor', 'role']`
- `scripts/query_bi.py` sends these values as a JSON POST body to `https://app.appgrowth.com/bi2/`.
- Use `--format csv` when parquet dependencies are unavailable.
- Save to `--output` for reproducibility before doing derived analysis.
- For the full request parameter table with defaults, accepted values, and examples, read `references/bi-api.md`.

Example request payload combining flavor and role filters:

```json
{
  "start": "2026-03-09",
  "end": "2026-03-10",
  "by": ["time_1d"],
  "query": "flavor IN ('flavor1', 'flavor2') AND role = 'revenue_ops'",
  "measures": [
    "impressions",
    "clicks",
    "uniq_clicks",
    "installs",
    "billing_actions",
    "optimization_events",
    "gross_spend",
    "revenue",
    "profit",
    "roas",
    "margin",
    "cr",
    "uniq_cr",
    "ipm",
    "cpm",
    "cpi",
    "ecpm",
    "ecpc",
    "ecpi",
    "raw_price",
    "bid_floor",
    "bid_cpi",
    "bid_cpa",
    "target_cpa",
    "advertiser_revenue_roas",
    "advertiser_revenue_roas_d0",
    "advertiser_revenue_roas_d1",
    "advertiser_revenue_roas_d3",
    "advertiser_revenue_roas_d7",
    "ad_revenue_arpu_d0"
  ],
  "filter_data": ["flavor", "role"],
  "date_column": "bid_timestamp"
}
```

Equivalent CLI call:

```bash
uvx --with pandas --with pyarrow --with requests \
  python scripts/query_bi.py \
  --params-json "{\"start\":\"2026-03-09\",\"end\":\"2026-03-10\",\"by\":[\"time_1d\"],\"query\":\"flavor IN ('flavor1', 'flavor2') AND role = 'revenue_ops'\",\"measures\":[\"impressions\",\"clicks\",\"uniq_clicks\",\"installs\",\"billing_actions\",\"optimization_events\",\"gross_spend\",\"revenue\",\"profit\",\"roas\",\"margin\",\"cr\",\"uniq_cr\",\"ipm\",\"cpm\",\"cpi\",\"ecpm\",\"ecpc\",\"ecpi\",\"raw_price\",\"bid_floor\",\"bid_cpi\",\"bid_cpa\",\"target_cpa\",\"advertiser_revenue_roas\",\"advertiser_revenue_roas_d0\",\"advertiser_revenue_roas_d1\",\"advertiser_revenue_roas_d3\",\"advertiser_revenue_roas_d7\",\"ad_revenue_arpu_d0\"],\"filter_data\":[\"flavor\",\"role\"],\"date_column\":\"bid_timestamp\"}"
```

## Available Metrics And Dimensions

- Canonical source for available fields is BIAdapter/BI2 domain definitions in appgrowth repo (guidance only, not required at runtime).
- Use these concepts in requests:
  - dimensions from BI2 `DIMENSIONS` (for `by`, `pivot`, `filter_data` keys)
  - metrics from BI2 `MEASURES` (for `measures`, and `metric` when pivoting)
  - defaults from BI2 `DEFAULT_MEASURES_IDS`
- Prefer using `references/bi-catalog.json` in this skill as the local snapshot of available fields.
- Common metrics to start:
  - `impressions`, `clicks`, `installs`, `gross_spend`, `revenue`, `profit`, `roas`, `margin`
- Common dimensions to start:
  - `bundle`, `campaign_id`, `app`, `country`, `time_1d`
- Important validation rules:
  - `dau` requires both `app` and `country` in `by`
  - `approx_qps` requires `by=["app","country"]`
  - `target_margin` and `uptime` require `campaign_id` in `by`
  - `fcst_profit` and `fcst_revenue` require `by=["time_1d"]`

## Refresh Catalog From appgrowth-py

Run this only when you need to refresh available BI fields in this skill.

1. Open the appgrowth repo and ensure BI dependencies are installed (for example `make http-install`).
2. Export catalog from BI2 constants:

```bash
cd /path/to/appgrowth-py
python3 - <<'PY'
import json
from appgrowth.domain.bi2 import DIMENSIONS, MEASURES, DEFAULT_MEASURES_IDS

payload = {
  "source": "appgrowth/domain/bi2.py",
  "dimensions_count": len(DIMENSIONS),
  "measures_count": len(MEASURES),
  "default_measures_ids": list(DEFAULT_MEASURES_IDS),
  "dimensions": [
    {
      "id": k,
      "title": v.get("title"),
      "group": v.get("group"),
      "filterable": v.get("filterable"),
      "external": v.get("external"),
    }
    for k, v in sorted(DIMENSIONS.items())
  ],
  "measures": [
    {
      "id": k,
      "title": v.get("title"),
      "group": v.get("group"),
      "format": v.get("format"),
      "default": bool(v.get("default")),
      "external": bool(v.get("external", False)),
    }
    for k, v in sorted(MEASURES.items())
  ],
}

print(json.dumps(payload, indent=2))
PY
```

3. Save output to this skill file:
   - `references/bi-catalog.json`
4. Update `SKILL.md` date note if needed and keep query examples unchanged.

## Output and Analysis

- The script prints shape and a preview by default.
- Use `--head N` to control preview rows.
- Use `--output` to persist full results for later steps.
- For follow-up analysis, you can use Python via `uvx` or query the saved file with DuckDB.

Analyze a saved parquet file with Python:

```bash
uvx --with pandas --with pyarrow python -c "
import pandas as pd
df = pd.read_parquet('/tmp/revenue_by_bundle_30d.parquet')
print(df.groupby('bundle', dropna=False)[['revenue', 'gross_spend']].sum().sort_values('revenue', ascending=False).head(20))
"
```

Analyze a saved parquet file with DuckDB:

```bash
duckdb -c "
SELECT bundle, sum(revenue) AS revenue, sum(gross_spend) AS gross_spend
FROM read_parquet('/tmp/revenue_by_bundle_30d.parquet')
GROUP BY 1
ORDER BY revenue DESC
LIMIT 20;
"
```

## Resources

- Query client and CLI: `scripts/query_bi.py`
- API notes and examples: `references/bi-api.md`
- Generated field catalog snapshot: `references/bi-catalog.json`
