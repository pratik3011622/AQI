# IEEE Paper Working Outline

Working title: **Can Delhi Teach Surat? Cross-City Generalization of Supervised Models for Next-Day AQI Forecasting in India**

This outline intentionally contains no fabricated findings or references. Replace prompts only after the data source and experiment results are verified.

## Abstract

150–200 words: problem, chosen dataset and date range, cities, chronological protocol, models, measured headline results, and limitations. Do not write performance claims before experiments finish.

## I. Introduction

- AQI forecasting context and motivation for cities with limited monitoring history.
- Limitation of random splits and single-city evaluations.
- Contributions: chronological comparison, cross-city transfer, and local-data adaptation with a deployed research prototype.

## II. Related Work

Summarize verified studies on Indian AQI prediction, temporal validation, cross-city transfer, and explainability. Add only references you have read and confirmed from the publisher or repository.

## III. Data and Preprocessing

- Dataset title, publisher/original source, version, download date, licence/terms, date range, and city coverage.
- City selection based on coverage; missingness table and short-gap handling.
- Optional weather source, variables, coordinates, merge procedure, and terms.
- If using 2015–2020 CPCB/Kaggle data, disclose the 2020 lockdown and analysis choice.

## IV. Methodology

- Target: next-calendar-day AQI.
- Past-only lags, trailing rolling statistics, pollutants/weather, and cyclical calendar features.
- Explicitly state that city identity is excluded from model inputs.
- Persistence, Ridge, Random Forest, and XGBoost baselines; chronological split and any validation/tuning protocol.
- Metrics: MAE, RMSE, R², AQI-category accuracy, and macro-F1.

## V. Experiments

- E1: within-city chronological holdout.
- E2: source-city × target-city transfer matrix; define leave-one-city-out protocol if used.
- E3: 0/30/60/90 days of target-city adaptation; define precisely which test observations remain unseen.
- E4: feature explanation method and sampling procedure; distinguish model importance from SHAP values.
- E5: AQI category errors and failure analysis.
- E6 (optional): pre-lockdown versus lockdown-period shift analysis.

## VI. Results

Insert only measured tables/figures from `results/`. Always compare against persistence and report sample counts with each result.

## VII. System Implementation

Describe the FastAPI endpoints, React dashboard, model artifact/versioning, and a verified deployment configuration. Include a system diagram and screenshots after deployment.

## VIII. Discussion and Limitations

Discuss dataset coverage and licence, temporal distribution shifts, missing observations, city representativeness, weather availability, uncertainty, and the non-advisory nature of the prototype.

## IX. Conclusion and Future Work

State findings supported by the experiments, then discuss additional cities, current data sources, spatial features, and calibrated uncertainty as future work.

## References

Use the IEEE conference template and verified source metadata. Dataset/API citations and access dates belong here. Never invent bibliographic details.
