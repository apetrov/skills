---
name: preliminary-data-analysis
description: Conduct preliminary data analysis on datasets from files, databases, warehouses, APIs, or other external services. Use when Codex needs to inspect data shape and quality, profile columns, compute summary metrics, identify anomalies, compare segments, or produce an initial analytical readout before deeper modeling or reporting.
---

# Preliminary Data Analysis

Perform a fast, reproducible first-pass analysis on available data. Preserve external inputs locally in a session-scoped `/tmp` workspace, prefer parquet for stored extracts, and use `duckdb` or `pandas` via `uvx` for the analysis.

## Workflow

1. Define the analysis slice before pulling data.
2. Create a session directory in `/tmp` and keep all temporary artifacts there.
3. Save a local copy of any externally loaded data before transforming it.
4. Convert working datasets to parquet unless there is a strong reason not to.
5. Run the first-pass analysis with `duckdb` or `pandas` via `uvx`.
6. Summarize findings, caveats, and recommended next checks.

## Session Workspace

Create one task-scoped directory under `/tmp` for the current session. Use a short task slug plus the date in `YYYYMMDD` form.

Example:

```text
/tmp/campaign-analysis-20260324
```

Rules:

- Avoid using the local repo directory for temporary analysis files.
- Put raw extracts, parquet conversions, notebooks, SQL files, intermediate outputs, and charts inside the `/tmp` session directory.
- Reuse the same session directory for the same analysis task unless isolation is needed.
- Prefer descriptive slugs such as `campaign-analysis`, `revenue-audit`, or `funnel-dropoff`.

## Data Preservation

When loading data from an external service, persist a local copy immediately in the `/tmp` session directory before doing substantial analysis.

Prefer this order:

1. Save the raw or closest-available extract.
2. Convert the working copy to parquet.
3. Run transformations against the parquet copy when practical.

Avoid CSV unless the source only provides CSV or another tool strictly requires it. If CSV is unavoidable, keep it only as an ingest artifact and create a parquet working copy as early as possible.

## Analysis Tools

Prefer one of these:

- `duckdb` for fast SQL-style exploration, joins, aggregations, and parquet-native workflows.
- `pandas` via `uvx` for Python-based profiling, reshaping, lightweight statistical checks, or charting.

Choose the simplest tool that matches the task:

- Use `duckdb` first when the work is tabular, SQL-friendly, or primarily based on parquet files.
- Use `pandas` when Python-specific logic or custom inspection is more efficient.
- Combine them when helpful, but avoid unnecessary duplication.

## Minimum First Pass

Unless the user asks for something narrower, cover these checks:

- Row count and time range.
- Grain and key columns.
- Column types and null rates.
- Basic distributions for important numeric fields.
- Cardinality and top values for important categorical fields.
- Duplicate checks at the likely business key.
- Obvious outliers, discontinuities, or missing partitions.
- A short list of hypotheses or follow-up questions.

## Output Expectations

Keep the result concise and decision-oriented:

- State what data was analyzed and where it came from.
- State what was preserved locally in `/tmp`.
- Report the main summary metrics and any anomalies.
- Call out data quality concerns and confidence limits.
- Recommend the next two or three analyses if the user wants a deeper pass.

## Command Patterns

Use these as defaults and adapt as needed.

Create the session workspace:

```bash
mkdir -p /tmp/<task-slug>-YYYYMMDD
```

Explore parquet with DuckDB:

```bash
duckdb -c "SELECT * FROM '/tmp/<task-slug>-YYYYMMDD/data.parquet' LIMIT 10;"
```

Use pandas via uvx:

```bash
uvx --with pandas --with pyarrow python - <<'PY'
import pandas as pd
df = pd.read_parquet('/tmp/<task-slug>-YYYYMMDD/data.parquet')
print(df.head())
print(df.describe(include='all'))
PY
```

If additional libraries are needed for parsing or parquet support, add them explicitly to the `uvx --with ...` invocation. For pandas parquet reads, include a parquet engine such as `pyarrow`.
