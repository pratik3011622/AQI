# Analysis notebooks

Keep exploratory work reproducible and point notebooks at files under `data/raw/` or generated outputs under `results/`. Do not commit raw datasets unless their licence permits redistribution.

Suggested sequence:

1. `01_eda.ipynb` — source, date range, city coverage, missingness, AQI distributions, and documented city selection.
2. `02_cleaning_features.ipynb` — inspect the transformations implemented in `src/data_utils.py`; avoid maintaining a second conflicting feature pipeline.
3. `03_baselines_models.ipynb` — inspect chronological holdout metrics from `src/train.py` and residuals.
4. `04_cross_city.ipynb` — visualize `results/transfer_matrix.csv` and report city-pair coverage.
5. `05_few_shot_explainability.ipynb` — plot adaptation results and add SHAP only after choosing the final model and evaluation protocol.

Record the dataset version, citation, licence, and any exclusions in notebook output or accompanying notes. Notebooks are not yet populated; the scripts are the current source of truth.
