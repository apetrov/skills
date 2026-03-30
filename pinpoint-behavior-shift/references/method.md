# Method

Source article: "What Changed? Pin-pointing behavior shift" by Alexander Petrov, published November 10, 2025. The core idea is to turn "what changed?" into a binary classification problem and read the separating features from model importances.

## Recipe

1. Build one dataset for the old or control world and label it `0`.
2. Build one dataset for the new or treatment world and label it `1`.
3. Train a classifier to predict `0` vs `1` using impression-level features.
4. Never include time as a feature because it leaks the answer.
5. Read the top feature importances as the explanation of what changed.

## Practical Notes

- Prefer disjoint cohorts. Overlap weakens the interpretation.
- Prefer impression-level features such as geo, publisher, app, creative, campaign, device, and pricing attributes.
- Use grouped importance first for the broad answer, then specific feature values for the operational answer.
- If the classifier does not separate the cohorts, the shift is either weak, too noisy, or not represented in the available columns.

## Modeling Choice

The article recommends gradient-boosted trees for mixed tabular data and missing values, while its example code uses a random-forest pipeline. This skill's bundled script uses a random forest because it is widely available in `scikit-learn` and works cleanly with one-hot encoded categorical data in an ad hoc `uvx` environment. That is an implementation choice, not a claim that random forests are always best.
