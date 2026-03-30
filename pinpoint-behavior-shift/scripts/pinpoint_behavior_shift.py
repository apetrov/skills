#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split

CATEGORICAL_COLUMNS = [
    "ad_type",
    "app",
    "campaign_id",
    "creative_theme",
    "creative_id",
    "city",
    "make",
    "model",
    "os_version",
    "payload__tag",
    "display_manager",
    "seller_name",
    "flavor",
    "content_type",
    "bidding_strategy_name",
    "optimization_method",
    "optimization_target",
    "optimization_window",
    "language",
]
NUMERIC_COLUMNS = [
    "raw_price",
    "prior_tag_impressions_count",
    "sessionduration",
    "optimization_value",
    "install",
]
EXCLUDED_COLUMNS = ["bid_date", "uuid"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare two impression cohorts and identify the main separating features."
    )
    parser.add_argument("--parquet-0", required=True)
    parser.add_argument("--parquet-1", required=True)
    parser.add_argument(
        "--features",
        required=True,
        nargs="+",
        help="Feature columns to include in the model.",
    )
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--top-n", type=int, default=20)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--out-dir", default="tmp/pinpoint-behavior-shift")
    return parser.parse_args()

def read_frame(parquet_path: str, label: int) -> pd.DataFrame:
    frame = pd.read_parquet(parquet_path)
    frame["label"] = label
    return frame


def resolve_features(requested_features: list[str]) -> tuple[list[str], list[str]]:
    categorical = [column for column in requested_features if column in CATEGORICAL_COLUMNS]
    numeric = [column for column in requested_features if column in NUMERIC_COLUMNS]
    unknown = [
        column for column in requested_features if column not in CATEGORICAL_COLUMNS + NUMERIC_COLUMNS + EXCLUDED_COLUMNS
    ]
    blocked = [column for column in requested_features if column in EXCLUDED_COLUMNS]

    if unknown:
        raise ValueError(f"Unknown feature columns: {', '.join(unknown)}")
    if blocked:
        raise ValueError(f"Excluded feature columns are not allowed: {', '.join(blocked)}")
    if not categorical and not numeric:
        raise ValueError("No usable features were provided.")

    return categorical, numeric


def ensure_columns(frame: pd.DataFrame, expected: list[str]) -> pd.DataFrame:
    missing = [column for column in expected if column not in frame.columns]
    for column in missing:
        frame[column] = pd.NA
    return frame


def prepare_features(
    frame: pd.DataFrame,
    categorical_columns: list[str],
    numeric_columns: list[str],
) -> tuple[pd.DataFrame, pd.Series]:
    expected = categorical_columns + numeric_columns
    frame = ensure_columns(frame.copy(), expected)

    parts = []
    if categorical_columns:
        categorical = (
            frame[categorical_columns]
            .astype("string")
            .fillna("__NA__")
        )
        parts.append(pd.get_dummies(categorical, prefix_sep="="))
    if numeric_columns:
        numeric = (
            frame[numeric_columns]
            .apply(pd.to_numeric, errors="coerce")
            .fillna(0.0)
        )
        parts.append(numeric)

    features = pd.concat(parts, axis=1)
    target = frame["label"].astype(int)
    return features, target


def split_base_feature(encoded_column: str) -> str:
    return encoded_column.split("=", 1)[0]


def fit_model(features: pd.DataFrame, target: pd.Series, test_size: float, random_state: int):
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=test_size,
        random_state=random_state,
        stratify=target,
    )

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=random_state,
        n_jobs=-1,
        class_weight="balanced_subsample",
    )
    model.fit(x_train, y_train)

    probabilities = model.predict_proba(x_test)[:, 1]
    predictions = model.predict(x_test)

    metrics = {
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
        "classification_report": classification_report(y_test, predictions, output_dict=True),
    }

    importances = pd.Series(model.feature_importances_, index=features.columns, name="importance")
    encoded_importances = (
        importances.sort_values(ascending=False)
        .rename_axis("feature")
        .reset_index()
    )
    grouped_importances = (
        importances.groupby(split_base_feature)
        .sum()
        .sort_values(ascending=False)
        .rename_axis("feature_group")
        .reset_index(name="importance")
    )

    return metrics, grouped_importances, encoded_importances


def write_outputs(
    out_dir: Path,
    args: argparse.Namespace,
    combined: pd.DataFrame,
    grouped_importances: pd.DataFrame,
    encoded_importances: pd.DataFrame,
    metrics: dict,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    grouped_path = out_dir / "grouped_feature_importance.csv"
    encoded_path = out_dir / "encoded_feature_importance.csv"
    metrics_path = out_dir / "metrics.json"
    cohorts_path = out_dir / "cohorts.json"
    sample_path = out_dir / "cohort_sizes.csv"

    grouped_importances.to_csv(grouped_path, index=False)
    encoded_importances.to_csv(encoded_path, index=False)
    pd.DataFrame(
        {
            "label": combined["label"].value_counts().sort_index().index,
            "rows": combined["label"].value_counts().sort_index().values,
        }
    ).to_csv(sample_path, index=False)

    cohorts = {
        "cohort_0": {
            "parquet_path": args.parquet_0,
            "label": 0,
        },
        "cohort_1": {
            "parquet_path": args.parquet_1,
            "label": 1,
        },
        "features": args.features,
    }

    metrics_path.write_text(json.dumps(metrics, indent=2))
    cohorts_path.write_text(json.dumps(cohorts, indent=2))


def main() -> int:
    args = parse_args()

    frame_0 = read_frame(args.parquet_0, 0)
    frame_1 = read_frame(args.parquet_1, 1)
    combined = pd.concat([frame_0, frame_1], ignore_index=True)

    if combined["label"].nunique() < 2:
        print("Expected both labels 0 and 1 to be present.", file=sys.stderr)
        return 1

    try:
        categorical_columns, numeric_columns = resolve_features(args.features)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 1

    features, target = prepare_features(combined, categorical_columns, numeric_columns)
    metrics, grouped_importances, encoded_importances = fit_model(
        features,
        target,
        test_size=args.test_size,
        random_state=args.random_state,
    )

    out_dir = Path(args.out_dir)
    write_outputs(
        out_dir=out_dir,
        args=args,
        combined=combined,
        grouped_importances=grouped_importances.head(args.top_n),
        encoded_importances=encoded_importances.head(args.top_n),
        metrics=metrics,
    )

    print(f"Rows: {len(combined)}")
    print(f"ROC AUC: {metrics['roc_auc']:.4f}")
    print(f"Output directory: {out_dir}")
    print("Top grouped features:")
    print(grouped_importances.head(args.top_n).to_string(index=False))
    print("Top encoded features:")
    print(encoded_importances.head(args.top_n).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
