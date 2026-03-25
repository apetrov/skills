---
name: pandas-style
description: "Refactor Python pandas DataFrame code into a chain-friendly, non-mutating style. Use when Codex needs to write, review, or rewrite pandas transformations and should prefer snake_case columns, `loc[lambda x: ...]` filtering, `assign(...)` for derived columns, dot notation for safe column access, and no `inplace` or direct dataframe mutation."
---

# Pandas Style

## Goal

Write pandas code as readable dataframe transformations instead of stepwise mutation.

## Rules

- Convert column names to snake_case before other dataframe operations.
- Prefer `df.loc[lambda x: ...]` for row filtering instead of `df[mask]`.
- Prefer `df.assign(...)` for adding or replacing columns.
- Prefer dot notation such as `df.column_name` for simple column access.
- Fall back to bracket notation only when the column name is not a valid identifier, conflicts with a dataframe attribute or method, or is provided dynamically.
- Avoid direct mutation such as `df[col] = ...`, `del df[col]`, `.insert(...)`, or `inplace=True`.
- Treat transformations as returning new dataframes.
- Preserve existing behavior while refactoring unless the user explicitly asks for semantic changes.

## Workflow

1. Rename columns to snake_case immediately after loading or receiving the dataframe.
2. Refactor filters to `loc[lambda x: ...]`.
3. Refactor derived columns to `assign(...)`.
4. Replace bracket column access with dot notation wherever it is safe.
5. Remove `inplace=True` and keep the returned dataframe.
6. Prefer short method chains over mutation-heavy intermediate steps.

## Patterns

### Normalize column names first

Put column names
```python
df = pd.read_csv("data.csv")
df = df.rename(columns={"Name": "name", "Age": "age", "City": "city"})
```

### Filter with `loc`

Bad:

```python
revenue[revenue["name"].fillna("") == self.name]
```

Good:

```python
revenue.loc[lambda x: x.name.fillna("") == self.name]
```

### Add columns with `assign`

Bad:

```python
revenue["foobar"] = 1
```

Good:

```python
revenue = revenue.assign(foobar=1)
```

### Prefer dot notation

Bad:

```python
revenue["age"]
```

Good:

```python
revenue.age
```

## Notes

- When `assign(...)` needs a value derived from the current dataframe, prefer callables: `df.assign(foobar=lambda x: x.a + x.b)`.
- When multiple transformations belong together, keep them in one chain if that improves readability.
- Do not introduce `.copy()` or temporary mutation unless the task specifically requires it for correctness.
