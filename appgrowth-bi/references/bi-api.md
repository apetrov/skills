# Appgrowth BI API Reference

## Endpoint

- URL: `https://app.appgrowth.com/bi2/`
- Method: `POST`
- Header: `Authorization: <BI_API_KEY>`

## Request Contract

Send a JSON object with BI query parameters. Include `format` when needed.

Example body:

```json
{
  "start": "30d",
  "end": "0d",
  "by": ["bundle"],
  "measures": ["revenue", "gross_spend", "installs"],
  "date_column": "bid_timestamp",
  "format": "parquet"
}
```

## Response Parsing

- `csv`: parse with `pandas.read_csv`
- `parquet`: parse with `pandas.read_parquet`
- `json`: parse with `pandas.json_normalize`

## Canonical Python Shape

```python
response = requests.post(
    "https://app.appgrowth.com/bi2/",
    headers={"Authorization": os.environ["BI_API_KEY"]},
    json=params,
)
```

## Common Parameters

- Date range: `start`, `end` (relative like `30d`/`0d` or absolute dates)
- Grouping: `by`, `pivot`
- Metrics: `measures`, `metric` (pivot metric)
- Filters: `filter_data`, `query`, `having`
- Events and derived event metrics: `events`, `event_metrics`, `action_metrics`
- Output controls: `format`, `date_column`

## Parameter Table

| Name | Type | Default value | Description | Acceptable values | Example |
| --- | --- | --- | --- | --- | --- |
| `start` | `string` | `1d` | Start of interval. | Date string or timedelta pattern. | `"1d"`, `"1w"`, `"2025-07-01"` |
| `end` | `string` | `0d` | End of interval. | Date string or timedelta pattern. | `"0d"`, `"1w"`, `"2025-07-01"` |
| `by` | `list[string]` | `["time_1d"]` | Split columns. | Dimension ids from `references/bi-catalog.json`. | `["bundle", "time_1d"]` |
| `pivot` | `list[string]` | `[]` | Columns used in `pandas.pivot_table`. | Dimension ids from `references/bi-catalog.json`. | `["country"]` |
| `metric` | `string` | `""` | Value column used in `pandas.pivot_table`. | Measure ids from `references/bi-catalog.json`. | `"revenue"` |
| `query` | `string` | `""` | Raw SQL query for ClickHouse. Conditions with `OR` must be enclosed in parentheses. | Valid ClickHouse boolean expression. | `payload__tag='123456789_iOS' AND (role='ag_playbook' OR role='exp')` |
| `having` | `string` | `""` | Pandas query applied to the result dataframe via `df.query(having, engine="python")`. | Valid pandas query expression. | `impressions > 0`, `(impressions > 0) & (clicks > 0)` |
| `events` | `list[string]` | `[]` | List of ad events. | Event ids supported by BI. | `["video_click", "image_click"]` |
| `event_metrics` | `list[string]` | `[]` | List of ad event metrics. | Event metric ids supported by BI. | `["postbanner_ctr", "video_ctr"]` |
| `measures` | `list[string]` | BI defaults | Measures returned by the query. | Measure ids from `references/bi-catalog.json`; defaults come from `default_measures_ids`. | `["impressions", "clicks", "gross_spend", "cpi", "advertiser_revenue_roas_d0"]` |
| `action_metrics` | `dict[string, list[string]]` | `{}` | Metrics requested per separated action. | Mapping of action id to supported metric ids. | `{"100": ["count", "cpa", "advertiser_roas_d0"]}` |
| `concentrate_dims` | `list[string]` | `[]` | Filter out rows that are least common by measure across dims. Selected dimension must also appear in `by`. | Dimension ids from `references/bi-catalog.json`. | `["country"]` |
| `concentrate_measure` | `string` | `""` | Measure used by concentration. Must also appear in `measures`. | Measure ids from `references/bi-catalog.json`. | `"gross_spend"` |
| `concentrate_mass` | `float` | `None` | Mass threshold used in concentration. | Float from `0` to `1`. | `0.9` |
| `date_column` | `string` | `"timestamp"` | Date column used to aggregate data. | `"timestamp"`, `"bid_timestamp"` | `"bid_timestamp"` |
| `format` | `string` | `"json"` | Response format. | `"csv"`, `"json"`, `"parquet"` | `"parquet"` |

## Quick Examples

- Revenue by bundle for last 30 days:
  - `start=30d`, `end=0d`, `by=["bundle"]`, `measures=["revenue"]`
- Revenue by day for last 30 days:
  - `start=30d`, `end=0d`, `by=["time_1d"]`, `measures=["revenue"]`

## Failure Mode

If HTTP status is not `200`, treat the call as failed and surface status code plus response body.

## Full Parameter Example

```python
params = {
    "start": "2025-07-01",
    "end": "2025-07-03",
    "by": ["payload__tag", "time_1d"],
    "measures": [
        "impressions",
        "clicks",
        "installs",
        "gross_spend",
        "revenue",
        "advertiser_revenue_d0",
        "advertiser_revenue_roas_d0",
    ],
    "date_column": "bid_timestamp",
    "format": "parquet",
}
```

Equivalent CLI usage:

```bash
uvx --with pandas --with pyarrow --with requests \
  python scripts/query_bi.py \
  --params-json '{"start":"2025-07-01","end":"2025-07-03","by":["payload__tag","time_1d"],"measures":["impressions","clicks","installs","gross_spend","revenue","advertiser_revenue_d0","advertiser_revenue_roas_d0"],"date_column":"bid_timestamp","format":"parquet"}'
```
