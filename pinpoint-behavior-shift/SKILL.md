---
name: pinpoint-behavior-shift
description: Compare two disjoint impression cohorts and identify what changed by turning "before vs after" into a classification problem. Use when Codex needs to explain a behavior shift, campaign shift, traffic mix change, creative mix change, or delivery change from impression-level parquet data, and should fetch or receive two cohort parquet files, label them `0` and `1`, train a classifier without time leakage, and report the most important separating features.
---

# Pinpoint Behavior Shift

## Overview

Fetch or receive two disjoint parquet datasets, label them `0` and `1`, train a classifier to predict the label from impression-level features, and treat the strongest separators as the answer to "what changed?"

Read [references/method.md](references/method.md) for the recipe and [references/impressions_endpoint.md](references/impressions_endpoint.md) for the endpoint contract and schema.

## Workflow

1. Confirm the two cohorts are disjoint.
2. Fetch or locate one parquet file for label `0` and one parquet file for label `1`.
3. Choose the feature list to model.
4. Exclude time-leaking or identifier-only features before modeling.
5. Train a classifier and evaluate whether the two cohorts are actually separable.
6. Return the top grouped features and the top concrete feature values that separate label `0` from label `1`.

## Ask For Missing Inputs

If the user did not specify both cohorts, ask for the missing pieces.

Each cohort needs either:

- a parquet file path

or, if the agent must fetch it:

- `start`
- `end`
- optional raw ClickHouse `query`
- optional `limit`

The script also needs an explicit feature list. Ask for it or choose it deliberately from the known schema.

Treat date ranges or filter clauses as invalid if the two cohorts overlap. The point is to compare two distinct slices.

## Fetch The Data

The bundled script does not know about the API. The agent is responsible for fetching parquet files first, then passing file paths to the script.

Use the local endpoint described in [references/impressions_endpoint.md](references/impressions_endpoint.md).

Typical fetch pattern:

```bash
curl 'http://127.0.0.1:4000/impressions?start=2026-03-01&end=2026-03-07&query=campaign_id%20%3D%2063880&limit=50000' \
  --output tmp/cohort-0.parquet

curl 'http://127.0.0.1:4000/impressions?start=2026-03-08&end=2026-03-14&query=campaign_id%20%3D%2063880&limit=50000' \
  --output tmp/cohort-1.parquet
```

Increase the limits when possible. The endpoint defaults to `100`, which is usually too small for a stable answer.

Then run the bundled script:

```bash
uvx --from cpython --with pandas --with pyarrow --with scikit-learn python scripts/pinpoint_behavior_shift.py \
  --parquet-0 tmp/cohort-0.parquet \
  --parquet-1 tmp/cohort-1.parquet \
  --features app city model os_version raw_price sessionduration prior_tag_impressions_count install \
  --out-dir tmp/pinpoint-behavior-shift
```

## Model The Shift

Apply the article's recipe:

1. Label the first cohort as `0`.
2. Label the second cohort as `1`.
3. Pass an explicit feature list to the script.
4. Do not use time as a feature.
5. Train a classifier on impression-level features.
6. Rank importances to see what changed.

Use the bundled script unless there is a strong reason not to. The script:

- reads two parquet files provided by the agent
- only uses the features explicitly passed by the agent
- combines both cohorts into one labeled dataset
- excludes `bid_date` to avoid time leakage
- excludes `uuid` because it is an identifier, not a useful explanatory feature
- treats IDs such as `campaign_id` and `creative_id` as categorical
- trains a random forest on one-hot encoded features
- writes grouped and concrete importances to CSV

## Interpret The Output

Do not stop at raw importances. Explain them.

When reporting results:

- start with whether the classifier meaningfully separated the cohorts
- mention which features were included in the model
- report the headline metric from `metrics.json`
- use `grouped_feature_importance.csv` to answer which feature families changed
- use `encoded_feature_importance.csv` to answer which specific values changed
- tie the top features back to a plausible operational story

Examples:

- `app` rose to the top: traffic mix changed across apps
- `creative_theme` rose to the top: the creative mix changed
- `seller_name` or `display_manager` rose to the top: supply mix changed
- `city`, `language`, `make`, or `model` rose to the top: audience/device mix changed
- `install` rose to the top: post-impression outcome balance changed

## Output Contract

Return:

- the cohort definitions you used
- the parquet files you analyzed
- the command you ran
- the output directory
- the classifier quality metric
- the top grouped features
- the top concrete feature values
- any important assumptions or leakage risks

If the classifier cannot separate the cohorts much better than chance, say that clearly. Weak separability means the observed shift may be small, noisy, or happening in features not present in the dataset.
