---
name: dsp-ua-ops
description: Diagnose DSP user acquisition problems in volume, cost, platform ROAS, and advertiser ROAS. Use when acting as a DSP User Acquisition Manager, especially for Appgrowth BI investigations, default `role='revenue_ops'` and `flavor IN ('tricky', 'tricky_light')` scope, cohort-tag export from `http://localhost:4000/AGENT.md`, or Cohortful follow-up analysis.
---

# DSP UA Ops

Use this skill to investigate DSP performance regressions and explain what broke, where it broke, and what to check next.
Start with aggregated BI cuts, then escalate to cohort-tag export or Cohortful only when the BI split is not enough.

## Default Scope

Unless the user overrides it, assume:

- `role='revenue_ops'`
- `flavor IN ('tricky', 'tricky_light')`
- `date_column='bid_timestamp'`
- the typical analysis timeframe is the last 7 days
- required tokens and credentials are already present; do not spend time checking for them unless a request fails

When querying via `$appgrowth-bi`, prefer:

- `query="flavor IN ('tricky', 'tricky_light') AND role = 'revenue_ops'"`
- `filter_data=["flavor","role"]`

## Investigation Workflow

1. Define the comparison window.
If the user does not specify one, use the last 7 days as the main analysis window and compare it against the previous 7 days. For trend views, also pull daily data over the last 14 to 30 days.

2. Pull the top-line daily trend with `$appgrowth-bi`.
Start with `by=["time_1d"]` and measures covering the full funnel:
`impressions`, `clicks`, `uniq_clicks`, `installs`, `billing_actions`, `optimization_events`, `gross_spend`, `revenue`, `profit`, `roas`, `margin`, `cr`, `uniq_cr`, `ipm`, `cpm`, `cpi`, `ecpm`, `ecpc`, `ecpi`, `raw_price`, `bid_floor`, `bid_cpi`, `bid_cpa`, `target_cpa`, `advertiser_revenue_roas`, `advertiser_revenue_roas_d0`, `advertiser_revenue_roas_d1`, `advertiser_revenue_roas_d3`, `advertiser_revenue_roas_d7`, `ad_revenue_arpu_d0`.

3. Classify the problem before drilling in.

- Volume problem: impressions, clicks, installs, or optimization events drop.
- Cost problem: spend holds or rises while `cpm`, `cpi`, `ecpi`, `raw_price`, or bid metrics worsen.
- Platform ROAS problem: `revenue`, `profit`, `roas`, or `margin` deteriorate.
- Advertiser ROAS problem: `advertiser_revenue_roas` or the D0/D1/D3/D7 cuts deteriorate while platform metrics may still look stable.

4. Decompose by segment.
Use `bundle`, `app`, `campaign_id`, `country`, and `time_1d` first. If one split explains most of the delta, stop broad slicing and quantify that driver.

5. Escalate only when needed.
If the issue is concentrated in a specific cohort tag, use the local cohorts endpoint from `http://localhost:4000/AGENT.md`. If you need heavier cohort or feature analysis on exported data, use Cohortful.

6. Return a concise diagnosis.
State the broken metric, impacted segment, change magnitude, likely driver, confidence level, and the next confirming query if uncertainty remains.

## Analysis Heuristics

- Check volume first, then pricing, then monetization. Many ROAS drops are downstream of volume mix or rising CPI.
- Separate platform ROAS from advertiser ROAS explicitly. Do not treat them as interchangeable.
- Quantify contribution to the delta. Focus on the segment that explains the majority of change.
- If you export data from BI, convert or save it to parquet before running follow-up analysis whenever possible.
- Prefer saved BI outputs and DuckDB for follow-up calculations instead of repeating API calls.
- Use user-level or cohort-tag exports only after narrowing the target segment; do not export broad raw data by default.

## Tools

- Use `$appgrowth-bi` for all aggregated Appgrowth BI pulls.
- Use `uvx` and `duckdb` for local analysis on exported CSV or parquet files.
- Use `glow` when pretty-printing markdown summaries in the terminal helps readability.
- Read [references/investigation-recipes.md](references/investigation-recipes.md) for concrete query payloads and handoff commands.
