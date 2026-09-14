---
name: databricks-evaluation
description: Verify Databricks access and choose a safe execution path for evaluation work. Use when Codex needs to confirm authentication, inspect configured profiles, run a minimal SQL statement, run a Python Spark validation on Databricks, diagnose Databricks Connect or uvx issues, or capture environment-specific Databricks context for future reuse.
---

# Databricks Evaluation

Use this skill to validate that Databricks is reachable from the current environment and to choose the least fragile execution path.

## Quick Start

1. Check auth first.
2. Prefer the smallest read-only validation that answers the request.
3. Prefer SQL Statement Execution for a trivial connectivity test.
4. Use an on-cluster notebook task for Python Spark validation when Databricks Connect is unreliable.
5. Read [references/local-context.md](references/local-context.md) for environment-specific details that were already observed in this workspace.

## Auth Checks

Run lightweight checks before attempting execution:

```bash
which databricks
env | rg '^(DATABRICKS|DBX)'
awk '/^\[/{print} /^host[[:space:]]*=/{print}' ~/.databrickscfg
databricks auth profiles --profile DEFAULT
databricks current-user me --profile DEFAULT
```

If profiles are valid and `current-user me` succeeds, treat workspace auth as confirmed.

## SQL Validation Path

Use this path for the smallest possible "hello world" check.

1. List warehouses.
2. Pick a running warehouse.
3. Submit `SELECT 'hello world' AS message` through the SQL Statement Execution API.

Useful commands:

```bash
databricks warehouses list --profile DEFAULT
databricks api post /api/2.0/sql/statements/ --profile DEFAULT --json '{"warehouse_id":"<warehouse-id>","statement":"SELECT '\''hello world'\'' AS message","wait_timeout":"10s"}'
```

Prefer this path when the user asks whether Databricks access works, whether SQL is reachable, or wants a non-invasive smoke test.

## Python Spark Validation Path

Use this path when the user specifically asks for Python Spark on Databricks.

### Preferred path

Submit a temporary Python notebook to an existing cluster and fetch the notebook result with `jobs get-run-output`.

Workflow:

1. Create a workspace folder if needed.
2. Import a minimal notebook that uses `SparkSession.builder.getOrCreate()`.
3. Execute `spark.sql("SELECT 'hello world' AS message")`.
4. Return the result via `dbutils.notebook.exit(...)`.
5. Submit it as a one-off job on an existing cluster.
6. Fetch the task run output.

This is more reliable than Databricks Connect when local package versions or Spark Connect handshakes are uncertain.

### Fallback path

Use `uvx` with `databricks-connect`, but only after checking the cluster runtime and pinning a matching client version. If the cluster is on `15.4.x`, do not use the latest `databricks-connect`; pin `15.4.*` instead.

Commands to inspect compatibility:

```bash
databricks clusters list --profile DEFAULT
databricks clusters get <cluster-id> --profile DEFAULT
```

When `uvx` is sandboxed, redirect its writable paths into `/tmp`:

```bash
UV_CACHE_DIR=/tmp/uv-cache UV_TOOL_DIR=/tmp/uv-tools ...
```

## Reporting

When you finish, report:

- Whether auth worked
- Which profile was used
- Which execution path succeeded
- The concrete warehouse or cluster id used
- The returned result or the exact blocking error

Keep the report short and operational.
