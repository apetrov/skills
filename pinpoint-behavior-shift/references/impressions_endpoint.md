# Impressions Endpoint

Use the local endpoint:

`GET http://127.0.0.1:4000/impressions`

## Query Parameters

- `start`: required, ISO date
- `end`: required, ISO date
- `query`: optional raw ClickHouse filter appended to the `WHERE` clause
- `limit`: optional, defaults to `100`

## Response Format

The response is parquet.

## Output Columns

- `ad_type`: String
- `app`: String
- `bid_date`: Date
- `campaign_id`: Int64
- `creative_theme`: String
- `creative_id`: Int64
- `city`: String
- `make`: String
- `model`: String
- `os_version`: String
- `payload__tag`: String
- `raw_price`: Float64
- `uuid`: String
- `display_manager`: String
- `seller_name`: String
- `prior_tag_impressions_count`: Int64
- `flavor`: String
- `sessionduration`: Int64
- `content_type`: String
- `bidding_strategy_name`: String
- `optimization_method`: String
- `optimization_value`: Float64
- `optimization_target`: String
- `optimization_window`: String
- `language`: String
- `install`: UInt8

## Modeling Guidance

- Pass an explicit feature list into the analysis script rather than modeling every available column by default.
- Exclude `bid_date` from features because the cohorts are defined by time and it leaks the target.
- Exclude `uuid` from features because it is an identifier, not an explanatory dimension.
- Treat `campaign_id` and `creative_id` as categorical identifiers.
- Treat `raw_price`, `prior_tag_impressions_count`, `sessionduration`, `optimization_value`, and `install` as numeric features unless there is a reason to override that choice.
