# Investigation Recipes

Use these recipes after the skill triggers. Keep the default DSP scope unless the user overrides it.
Treat the last 7 days as the standard analysis window, and use a previous-7-day comparison by default.
Assume required tokens and credentials are already available unless a concrete command fails for auth.
When exporting BI data for downstream work, prefer parquet as the analysis format.

## Daily Trend Query

Use `$appgrowth-bi` with:

- `start=14d`
- `end=0d`
- `by=["time_1d"]`
- `query="flavor IN ('tricky', 'tricky_light') AND role = 'revenue_ops'"`
- `filter_data=["flavor","role"]`
- `date_column="bid_timestamp"`

Recommended measures:

```json
[
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
]
```

## Driver Split Queries

After identifying the broken day or window, rerun with one of:

- `by=["bundle"]`
- `by=["app"]`
- `by=["campaign_id"]`
- `by=["country"]`
- `by=["bundle","country"]` when the problem is likely geo mix

Keep the same measures so the decomposition stays comparable.

## DuckDB Checks

Use DuckDB to quantify contribution after saving BI output. If the initial export is CSV, convert it to parquet first.

CSV to parquet:

```bash
uvx --with pandas --with pyarrow python -c "
import pandas as pd
df = pd.read_csv('/tmp/dsp_daily.csv')
df.to_parquet('/tmp/dsp_daily.parquet', index=False)
"
```

Top negative ROAS contributors:

```sql
SELECT
  bundle,
  sum(gross_spend) AS gross_spend,
  sum(revenue) AS revenue,
  sum(profit) AS profit,
  sum(revenue) / nullif(sum(gross_spend), 0) AS roas
FROM read_parquet('/tmp/dsp_daily.parquet')
GROUP BY 1
ORDER BY profit ASC
LIMIT 20;
```

Platform vs advertiser ROAS by segment:

```sql
SELECT
  campaign_id,
  avg(roas) AS platform_roas,
  avg(advertiser_revenue_roas_d0) AS advertiser_roas_d0,
  avg(advertiser_revenue_roas_d7) AS advertiser_roas_d7
FROM read_parquet('/tmp/dsp_daily.parquet')
GROUP BY 1
ORDER BY advertiser_roas_d7 ASC NULLS LAST
LIMIT 20;
```

## Local Cohort Export

Use the local endpoint when a specific tag needs cohort-level confirmation.

Request pattern:

```bash
curl "http://127.0.0.1:4000/cohorts?tag=<exact_tag>&window=<days>&offset=<days_back>&lookback=3"
```

Available output columns:

- `campaign_id`
- `advertiser_revenue`
- `impressions`
- `gross_spend`
- `installs`
- `ecpi`
- `cpi`

Treat this endpoint as a targeted diagnostic tool for a known tag, not a broad discovery tool.

## Cohortful Handoff

Use Cohortful when you already have a narrowed export and need stronger analysis on cohort or user-level data.

Rules:

- Prefer `aggregated=false` for row-level exports.
- Use low-cardinality explanatory features such as `country`, `bundle`, `campaign_id`, `creative`, or `channel`.
- Do not use near-unique identifiers like `user_id` or `device_id` as model features.

Minimal upload example:

```bash
curl -X POST "https://app.cohortful.com/api/v1/datasets" \
  -H "Authorization: Bearer $TOKEN" \
  -F "name=dsp-ua-investigation" \
  -F "aggregated=false" \
  -F "features[]=country" \
  -F "features[]=campaign_id" \
  -F "arpu_name=advertiser_revenue" \
  -F "spend_name=gross_spend" \
  -F "installs_name=installs" \
  -F "file=@/tmp/export.csv;type=text/csv"
```

## Output Pattern

Summaries should name:

1. The failing metric.
2. The segment driving the change.
3. Whether the issue is volume, cost, platform ROAS, advertiser ROAS, or a combination.
4. The shortest next query that would confirm or falsify the leading hypothesis.
