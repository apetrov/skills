---
name: csv-to-markdown
description: Convert CSV files to Markdown tables with numbers rounded to at most four decimal places and trailing zeros removed. Use when asked to turn CSV exports into readable Markdown tables.
---

Use the bundled Python standard-library script; no pandas or extra dependencies are needed.

```bash
python3 <skill-directory>/scripts/csv_to_markdown.py <input.csv> [more.csv ...]
```

Resolve the script path relative to this skill directory. Each input produces a sibling file with the same basename and a `.md` extension, replacing any existing output. Leave the CSV unchanged.

Formatting follows these defaults:
- Use the first CSV row as the table header.
- Round finite numeric values to four decimal places using Decimal formatting; remove trailing zeros and normalize negative zero to zero.
- Preserve empty cells and text, escape table pipes and backslashes, and render embedded line breaks as `<br>`.
- Read UTF-8 CSV with optional BOM using Python's CSV parser so quoted commas and newlines work correctly.

If the user requests different precision or special handling for numeric-looking identifiers, adapt the formatter for that request. Report a clickable link to each generated file. Copy to the clipboard only when requested.
