#!/usr/bin/env python3
import argparse
import io
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import requests


DEFAULT_BI_URL = "https://app.appgrowth.com/bi2/"
SUPPORTED_FORMATS = ("csv", "parquet", "json")


@dataclass
class BI:
    url: str
    token: str
    fmt: str = "parquet"

    readers = {
        "csv": lambda res: pd.read_csv(io.StringIO(res.text)),
        "parquet": lambda res: pd.read_parquet(io.BytesIO(res.content)),
        "json": lambda res: pd.json_normalize(res.json()),
    }

    def get(self, **params) -> pd.DataFrame:
        if "format" not in params:
            params["format"] = self.fmt
        if self.fmt not in SUPPORTED_FORMATS:
            raise ValueError("Unsupported format. Use 'csv', 'parquet', or 'json'.")

        response = requests.post(
            self.url,
            headers={"Authorization": self.token},
            json=params,
            timeout=120,
        )
        if response.status_code != 200:
            raise ValueError(
                f"Failed to fetch data: {response.status_code} - {response.text}"
            )

        return self.readers[self.fmt](response)


def parse_value(raw: str) -> Any:
    lowered = raw.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered == "null":
        return None

    try:
        if raw.startswith("0") and raw != "0" and not raw.startswith("0."):
            return raw
        return int(raw)
    except ValueError:
        pass

    try:
        return float(raw)
    except ValueError:
        pass

    if raw.startswith("[") or raw.startswith("{"):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw

    return raw


def parse_key_values(items: list[str]) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Invalid --param '{item}'. Expected key=value.")
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"Invalid --param '{item}'. Key is empty.")
        params[key] = parse_value(value.strip())
    return params


def write_output(df: pd.DataFrame, output: Path, fmt: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "csv":
        df.to_csv(output, index=False)
    elif fmt == "parquet":
        df.to_parquet(output, index=False)
    elif fmt == "json":
        df.to_json(output, orient="records")
    else:
        raise ValueError(f"Unsupported output format: {fmt}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Query Appgrowth BI and print/save tabular results."
    )
    parser.add_argument("--url", default=DEFAULT_BI_URL, help="BI endpoint URL")
    parser.add_argument(
        "--token-env",
        default="BI_API_KEY",
        help="Environment variable containing BI API token",
    )
    parser.add_argument(
        "--format",
        default="parquet",
        choices=SUPPORTED_FORMATS,
        help="Response format requested from BI",
    )
    parser.add_argument(
        "--param",
        action="append",
        default=[],
        help="Request parameter in key=value format (repeatable)",
    )
    parser.add_argument(
        "--params-json",
        help="Raw JSON object merged into request params",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional output path (extension should match --format)",
    )
    parser.add_argument(
        "--head",
        type=int,
        default=20,
        help="Rows to print as preview (default: 20)",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    token = os.getenv(args.token_env)
    if not token:
        raise SystemExit(f"Missing {args.token_env}. Export it before running.")

    params = parse_key_values(args.param)
    if args.params_json:
        try:
            parsed_json = json.loads(args.params_json)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid --params-json: {exc}") from exc
        if not isinstance(parsed_json, dict):
            raise SystemExit("--params-json must decode to a JSON object")
        params.update(parsed_json)

    client = BI(url=args.url, token=token, fmt=args.format)
    df = client.get(**params)

    print(f"rows={len(df)} cols={len(df.columns)} format={args.format}")
    if args.head > 0:
        print(df.head(args.head).to_string(index=False))

    if args.output:
        write_output(df, args.output, args.format)
        print(f"saved={args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
