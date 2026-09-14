# Local Context

This reference captures environment-specific Databricks facts that were directly observed during setup and smoke testing in this workspace. Re-check them if the environment may have changed.

## Workspace Auth

- CLI path: `/opt/homebrew/bin/databricks`
- `~/.databrickscfg` exists
- Observed profiles:
  - `DEFAULT`
  - `dbc-29a8e8d0-5a51`
  - `vector-personal`
  - `bidmachine`
- Observed workspace host:
  - `https://dbc-29a8e8d0-5a51.cloud.databricks.com`
- `databricks auth profiles` reported these profiles as valid
- `databricks current-user me --profile DEFAULT` succeeded for `a.petrov@appodeal.com`

## SQL Warehouse Context

- Running warehouses observed:
  - `4e5d3aab6fd0560b` `sql-warehouse-small`
  - `7abeea5c8e7fad2a` `sql-warehouse-ops-2x-small`
- Minimal SQL statement execution succeeded on warehouse `4e5d3aab6fd0560b`
- Returned value:

```text
hello world
```

## Python Spark Context

- Running cluster observed for evaluation:
  - `0403-145958-20tgrrsu` `vector-cluster-ops-ag-models`
- Observed runtime:
  - `15.4.x-scala2.12`
- Reliable Python Spark validation path:
  - import a temporary workspace notebook
  - submit a one-off job to the existing cluster
  - fetch `jobs get-run-output`
- Observed successful notebook-task validation:
  - submit run `614141793577014`
  - task run `150015426969109`
  - notebook result `hello world`

## uvx / Databricks Connect Notes

- Local `uv run` environment in this repo did not have `pyspark`, `databricks.connect`, or `databricks.sdk`
- `uvx` worked after redirecting writable state:

```bash
UV_CACHE_DIR=/tmp/uv-cache UV_TOOL_DIR=/tmp/uv-tools
```

- Unpinned `uvx --with databricks-connect` installed `18.1.2`, which was incompatible with the `15.4.x` cluster runtime
- For this cluster family, pin `databricks-connect==15.4.*`
- One failed Databricks Connect attempt reported:
  - `Cluster id or serverless are required but were not specified.`
- A later failed attempt confirmed version skew:
  - `Unsupported combination of Databricks Runtime & Databricks Connect versions: 15.4 < 18.1.2`
