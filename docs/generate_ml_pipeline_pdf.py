from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether

OUTPUT = "docs/AQI_ML_Pipeline_and_Model_Comparison_Guide.pdf"

styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    name="CoverPre", fontName="Helvetica-Bold", fontSize=9.5, leading=13,
    alignment=TA_CENTER, textColor=colors.HexColor("#176b60")
))
styles.add(ParagraphStyle(
    name="CoverTitle", fontName="Helvetica-Bold", fontSize=19, leading=24,
    alignment=TA_CENTER, textColor=colors.HexColor("#12352f")
))
styles.add(ParagraphStyle(
    name="CoverSubtitle", fontName="Helvetica", fontSize=10.5, leading=14.5,
    alignment=TA_CENTER, textColor=colors.HexColor("#344c48")
))
styles.add(ParagraphStyle(
    name="CoverURL", fontName="Courier-Bold", fontSize=8.5, leading=11.5,
    alignment=TA_CENTER, textColor=colors.HexColor("#0f5146")
))

styles.add(ParagraphStyle(
    name="H1X", fontName="Helvetica-Bold", fontSize=12.5, leading=16,
    textColor=colors.HexColor("#176b60"), spaceBefore=10, spaceAfter=4, keepWithNext=True
))
styles.add(ParagraphStyle(
    name="H2X", fontName="Helvetica-Bold", fontSize=9.5, leading=13,
    textColor=colors.HexColor("#203b38"), spaceBefore=6, spaceAfter=2.5, keepWithNext=True
))
styles.add(ParagraphStyle(
    name="BodyX", fontName="Helvetica", fontSize=8.3, leading=11.6,
    textColor=colors.HexColor("#243130"), alignment=TA_JUSTIFY, spaceAfter=3
))
styles.add(ParagraphStyle(
    name="SmallX", fontName="Helvetica", fontSize=7.2, leading=9.2,
    textColor=colors.HexColor("#53615f")
))
styles.add(ParagraphStyle(
    name="Callout", fontName="Helvetica-Oblique", fontSize=8, leading=11,
    textColor=colors.HexColor("#134e44"), backColor=colors.HexColor("#eef5f2"),
    borderPadding=5, spaceBefore=3, spaceAfter=4
))
styles.add(ParagraphStyle(
    name="CodeSnippet", fontName="Courier", fontSize=6.5, leading=8.4,
    textColor=colors.HexColor("#143b35"), backColor=colors.HexColor("#f0f5f2"),
    borderPadding=4.5, spaceBefore=2.5, spaceAfter=3.5
))

styles.add(ParagraphStyle(
    name="TableHeader", fontName="Helvetica-Bold", fontSize=7.2, leading=9.5,
    textColor=colors.white, alignment=TA_LEFT
))
styles.add(ParagraphStyle(
    name="TableCell", fontName="Helvetica", fontSize=6.8, leading=9.2,
    textColor=colors.HexColor("#243130"), alignment=TA_LEFT
))
styles.add(ParagraphStyle(
    name="TableCellBold", fontName="Helvetica-Bold", fontSize=6.8, leading=9.2,
    textColor=colors.HexColor("#12352f"), alignment=TA_LEFT
))

def P(text, style="BodyX"):
    return Paragraph(text, styles[style])

def bullet(text):
    return Paragraph("<b>•</b> " + text, styles["BodyX"])

def make_table(data, widths=None, header_bg="#173b37"):
    formatted_data = []
    for row_idx, row in enumerate(data):
        formatted_row = []
        for col_idx, cell in enumerate(row):
            if isinstance(cell, str):
                if row_idx == 0:
                    formatted_row.append(Paragraph(cell, styles["TableHeader"]))
                elif col_idx == 0:
                    formatted_row.append(Paragraph(cell, styles["TableCellBold"]))
                else:
                    formatted_row.append(Paragraph(cell, styles["TableCell"]))
            else:
                formatted_row.append(cell)
        formatted_data.append(formatted_row)
        
    t = Table(formatted_data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor(header_bg)),
        ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#becbc6")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f4f7f5")]),
        ("LEFTPADDING", (0,0), (-1,-1), 4.5),
        ("RIGHTPADDING", (0,0), (-1,-1), 4.5),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    return t

doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=52, bottomMargin=52
)
story = []

# --- TITLE BLOCK ---
story += [
    P("TECHNICAL MACHINE LEARNING SPECIFICATION & VIVA DEEP DIVE", "CoverPre"),
    Spacer(1, 4),
    P("Machine Learning Architecture, Model Comparison & Code Walkthrough", "CoverTitle"),
    Spacer(1, 4),
    P("From Raw CPCB Ingestion & Strict Past Lags to Multi-Model Evaluation and FastAPI Inference", "CoverSubtitle"),
    Spacer(1, 4),
    P("Project: Can Delhi Teach Surat? | AQI Research Lab", "CoverURL"),
    Spacer(1, 8),
]

pipeline_summary = [
    ["ML Stage", "Primary Source File", "Mathematical / Algorithmic Core", "Key Artifact / Output"],
    ["1. Ingestion & Cleaning", "src/data_utils.py", "Schema alias regex lookup, date sorting, <=3-day interpolation", "Clean chronological city-day dataframe"],
    ["2. Past-Only Features", "src/data_utils.py", "Autoregressive lags (1,2,3,7), rolling 3/7 stats, cyclic harmonics", "29 engineered feature columns (no city IDs)"],
    ["3. Temporal Split", "src/train.py", "Forward-chaining time split (Train < 2025, Test == 2025)", "210,725 train rows vs 28,149 test rows"],
    ["4. Model Candidates", "src/train.py", "Ridge vs. Random Forest vs. XGBoost vs. Persistence", "Trained sklearn pipelines with median imputation"],
    ["5. Evaluation", "src/evaluate.py", "RMSE, MAE, R², 6-band CPCB category accuracy, Macro-F1", "Multi-metric comparison matrix"],
    ["6. Model Serialization", "src/train.py", "Joblib serialization + JSON metadata audit trail", "best_model.joblib & metadata.json"],
    ["7. Live API Serving", "backend/main.py", "FastAPI inference with automatic 7-day lag reconstruction", "REST endpoints: /predict & /explain"],
    ["8. Transfer Matrix", "src/experiments.py", "Zero-shot cross-city evaluation and few-shot calibration (30/60/90d)", "results/transfer_matrix.csv & few_shot.csv"]
]
story += [make_table(pipeline_summary, widths=[80, 95, 185, 155]), Spacer(1, 8)]

# --- SECTION 1: DATA CLEANING & NORMALIZATION ---
story += [
    P("1. Data Ingestion, Cleaning & Normalization (src/data_utils.py)", "H1X"),
    P("Real-world Indian air quality data from state and central pollution boards (CPCB) arrives in heterogeneous CSV schemas. The first stage transforms unstructured tabular records into a standardized, sorted, chronological time series:"),
    bullet("<b>Schema Aliasing (<code>normalize_columns</code>):</b> Maps variable headers (e.g. <code>area</code>, <code>location</code>, <code>station</code> -> <code>city</code>; <code>aqi_value</code>, <code>index</code>, <code>AQI</code> -> <code>aqi</code>) using regex string normalization."),
    bullet("<b>Date Parsing & Sorting:</b> Parses dates with <code>dayfirst=True</code> to prevent lexicographical month-day inversion. Rows are deduplicated on <code>(city, date)</code> and sorted chronologically."),
    bullet("<b>Short-Gap Linear Interpolation:</b> To preserve physical time series continuity without hallucinating synthetic trends, missing dates within a city are linearly interpolated <i>only if the gap is <= 3 consecutive days</i>. Larger gaps are retained as missing."),
    Spacer(1, 4),
    P("<b>Core Data Cleaning Code Snippet:</b>", "SmallX"),
    P("""# src/data_utils.py
def load_daily_data(data_path: str | Path | None = None) -> pd.DataFrame:
    source = Path(data_path) if data_path else RAW_DATA_DIR / "aqi.csv"
    frame = normalize_columns(pd.read_csv(source))
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce", dayfirst=True)
    frame["city"] = frame["city"].astype("string").str.strip()
    frame["aqi"] = pd.to_numeric(frame["aqi"], errors="coerce")
    frame = frame.dropna(subset=["city", "date"])
    frame = frame.drop_duplicates(["city", "date"], keep="last")
    return frame.sort_values(["city", "date"]).reset_index(drop=True)""", "CodeSnippet")
]

story += [PageBreak()]

# --- SECTION 2: FEATURE ENGINEERING ---
story += [
    P("2. Strict Past-Only Feature Engineering (src/data_utils.py & src/config.py)", "H1X"),
    P("To prevent lookahead data leakage, every sample feature must only use observations strictly prior to the forecast window. The pipeline produces <b>29 feature columns</b>:"),
    Spacer(1, 4)
]

feat_table = [
    ["Feature Group", "Included Columns", "Mathematical Definition & Purpose"],
    ["AQI Autoregressive Lags", "aqi_today, aqi_lag_1, aqi_lag_2, aqi_lag_3, aqi_lag_7", "AQI(t), AQI(t-1), AQI(t-2), AQI(t-3), AQI(t-7). Captures immediate persistence and week-over-week recurrence."],
    ["PM2.5 Lags", "pm25_today, pm25_lag_1, pm25_lag_2, pm25_lag_3, pm25_lag_7", "Fine particulate concentration lags. Key driver of respiratory toxicity."],
    ["Rolling Statistics", "aqi_rolling_mean_3, aqi_rolling_mean_7, aqi_rolling_std_3, aqi_rolling_std_7", "3-day and 7-day trailing mean and standard deviation. Quantifies multi-day pollution stagnation and atmospheric dispersion."],
    ["Cyclical Calendar Harmonics", "month_sin, month_cos, weekday_sin, weekday_cos", "sin(2*pi*m/12), cos(2*pi*m/12), sin(2*pi*w/7), cos(2*pi*w/7). Encodes annual winter inversions and weekend traffic patterns cyclically."],
    ["Optional Pollutants & Weather", "pm10, no2, so2, co, o3, temp, humidity, wind, pressure", "Surface meteorological parameters and secondary criteria gaseous pollutants."]
]
story += [make_table(feat_table, widths=[100, 140, 275]), Spacer(1, 6)]

story += [
    P("<b>The Shift Logic (No Future Leakage):</b>", "H2X"),
    P("In pandas, features are created using <code>city_frame['aqi'].shift(lag)</code> where <code>lag >= 0</code>, while the forecasting target is shifted backwards: <code>city_frame['target'] = city_frame['aqi'].shift(-1)</code>. Thus, sample <i>t</i> predicts target <i>t+1</i> using only past information."),
    Spacer(1, 4),
    P("<b>Why City Identity is Excluded:</b>", "H2X"),
    P("<code>CITY_COLUMN ('city')</code> is <b>never</b> included in <code>FEATURE_COLUMNS</code>. If one-hot city indicators were provided, tree algorithms would learn local sensor biases rather than meteorological dynamics, completely preventing zero-shot cross-city transfer to new cities."),
    Spacer(1, 4),
    P("<b>Feature Formulation Code:</b>", "SmallX"),
    P("""# src/data_utils.py (inside build_features)
aqi = city_frame['aqi'].astype(float)
city_frame['aqi_today'] = aqi
for lag in (1, 2, 3, 7):
    city_frame[f'aqi_lag_{lag}'] = aqi.shift(lag)
for window in (3, 7):
    city_frame[f'aqi_rolling_mean_{window}'] = aqi.rolling(window).mean()
    city_frame[f'aqi_rolling_std_{window}'] = aqi.rolling(window).std()

# Target: strictly next day's AQI
city_frame['target'] = aqi.shift(-1)
city_frame['target_date'] = city_frame['date'].shift(-1)

# Calendar harmonics (cyclical continuity)
city_frame['month_sin'] = np.sin(2 * np.pi * city_frame['date'].dt.month / 12)
city_frame['month_cos'] = np.cos(2 * np.pi * city_frame['date'].dt.month / 12)
city_frame['weekday_sin'] = np.sin(2 * np.pi * city_frame['date'].dt.weekday / 7)
city_frame['weekday_cos'] = np.cos(2 * np.pi * city_frame['date'].dt.weekday / 7)""", "CodeSnippet")
]

story += [PageBreak()]

# --- SECTION 3: MODEL COMPARISON & TRAINING ---
story += [
    P("3. Multi-Model Candidates & Training Architecture (src/train.py)", "H1X"),
    P("The project constructs scikit-learn pipelines with a median imputer for candidate models, tested against a naive persistence baseline:"),
    Spacer(1, 4)
]

candidate_desc = [
    ["Model Paradigm", "Pipeline Architecture & Hyperparameters", "Theoretical Role in Experiment"],
    ["Persistence Baseline", "y_hat(t+1) = y(t). Evaluated directly on aqi_today.", "Autoregressive benchmark. In meteorology, persistence often achieves high accuracy; an ML model must beat it to justify deployment."],
    ["Ridge Regression", "make_pipeline(SimpleImputer(strategy='median'), StandardScaler(), Ridge(alpha=10.0))", "L2-regularized linear model. Tests whether air quality dynamics are purely linear combinations of lags and weather."],
    ["Random Forest", "make_pipeline(SimpleImputer(strategy='median'), RandomForestRegressor(n_estimators=300, min_samples_leaf=2, max_features=0.8, random_state=42, n_jobs=-1))", "Bagging ensemble of decision trees. Reduces variance, models non-linear interactions, and handles feature collinearity."],
    ["XGBoost Regressor (Selected Best)", "make_pipeline(SimpleImputer(strategy='median'), XGBRegressor(n_estimators=400, max_depth=5, learning_rate=0.04, subsample=0.85, colsample_bytree=0.85, objective='reg:squarederror', random_state=42, n_jobs=-1))", "Gradient boosting ensemble. Optimizes 2nd-order Taylor loss expansions; excels at capturing sharp winter inversion thresholds."]
]
story += [make_table(candidate_desc, widths=[100, 230, 185]), Spacer(1, 8)]

story += [
    P("4. Empirical Model Comparison Results (Held-Out Test Year: 2025)", "H1X"),
    P("The models were trained on <b>210,725 rows</b> (pre-2025 across 291 cities) and evaluated on <b>28,149 unseen rows</b> in the held-out test year 2025. Here are the exact audited scores from <code>models/metadata.json</code>:"),
    Spacer(1, 4)
]

empirical_results = [
    ["Evaluated Model", "MAE (pts)", "RMSE (pts)", "R² Score", "Category Accuracy", "Macro-F1", "Verdict"],
    ["Persistence Baseline", "21.20", "32.59", "0.6546", "73.19%", "0.5434", "Naïve benchmark (Today -> Tomorrow)"],
    ["Ridge Regression", "20.35", "29.93", "0.7086", "73.14%", "0.4891", "Good linear baseline, low computational load"],
    ["Random Forest", "20.55", "30.12", "0.7049", "73.11%", "0.4942", "High memory footprint (~140MB serialized)"],
    ["XGBoost (WINNER)", "20.22", "29.82", "0.7107", "73.97%", "0.5025", "SELECTED: Lowest RMSE/MAE, highest R² & Accuracy"]
]
story += [make_table(empirical_results, widths=[105, 55, 60, 50, 75, 55, 115]), Spacer(1, 6)]

story += [
    P("<b>Why XGBoost Was Selected:</b>"),
    bullet("<b>Lowest Generalization Error:</b> Achieved the lowest held-out RMSE (<b>29.82</b>) and lowest MAE (<b>20.22 AQI points</b>)."),
    bullet("<b>Highest Explanatory Power:</b> Captured <b>71.07%</b> of variance ($R^2 = 0.7107$) on unseen 2025 test data, outperforming Ridge (70.86%) and Random Forest (70.49%)."),
    bullet("<b>Superior Threshold Handling:</b> Air quality suffers from sudden non-linear shifts (stubble burning, festive fireworks, temperature inversions). XGBoost's depth-5 trees with shrinkage (learning rate = 0.04) model step functions without exploding predictions."),
    bullet("<b>Production Efficiency:</b> The serialized model weighs only <b>1.1 MB</b> (vs 140+ MB for Random Forest), allowing sub-millisecond FastAPI responses on free Render instances.")
]

story += [PageBreak()]

# --- SECTION 4: CODE OF TRAINING & SELECTION ---
story += [
    P("5. Model Selection & Serialization Code (src/train.py)", "H1X"),
    P("How candidates are trained, evaluated on the chronological split, and the winner saved to disk:"),
    Spacer(1, 4),
    P("""# src/train.py
def train(data_path: str | None = None, test_year: int | None = None) -> dict:
    raw = load_daily_data(data_path)
    samples = build_features(raw)
    
    # Chronological holdout: Test year strictly separated
    year = test_year or int(samples["target_date"].dt.year.max())
    train_mask = samples["target_date"].dt.year < year
    test_mask = samples["target_date"].dt.year == year
    train_rows, test_rows = samples.loc[train_mask], samples.loc[test_mask]

    x_train, y_train = train_rows[FEATURE_COLUMNS], train_rows["target"]
    x_test, y_test = test_rows[FEATURE_COLUMNS], test_rows["target"]

    # Benchmark: Persistence
    scores = [{"model": "Persistence", **regression_metrics(y_test, test_rows["aqi_today"])}]
    fitted = {}

    for name, estimator in candidates().items():
        estimator.fit(x_train, y_train)
        prediction = np.clip(estimator.predict(x_test), 0, None)
        scores.append({"model": name, **regression_metrics(y_test, prediction)})
        fitted[name] = estimator

    # Automated selection of best model by lowest RMSE
    selected = min((s for s in scores if s["model"] != "Persistence"), key=lambda s: s["rmse"])
    best = fitted[selected["model"]]

    # Persist serialized model artifact and experiment metadata
    joblib.dump(best, MODEL_PATH)              # models/best_model.joblib
    METADATA_PATH.write_text(json.dumps(metadata, indent=2))
    return metadata""", "CodeSnippet"),
    Spacer(1, 6),

    P("6. Metrics Computation Code (src/evaluate.py)", "H1X"),
    P("How numeric accuracy and official CPCB band classifications are computed:"),
    Spacer(1, 4),
    P("""# src/evaluate.py
def aqi_category(value: float) -> str:
    if value <= 50:  return "Good"
    if value <= 100: return "Satisfactory"
    if value <= 200: return "Moderate"
    if value <= 300: return "Poor"
    if value <= 400: return "Very Poor"
    return "Severe"

def regression_metrics(actual, predicted) -> dict[str, float]:
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    actual_bands = [aqi_category(v) for v in actual]
    predicted_bands = [aqi_category(v) for v in predicted]
    labels = ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]
    return {
        "mae": float(mean_absolute_error(actual, predicted)),
        "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
        "r2": float(r2_score(actual, predicted)) if len(actual) > 1 else float("nan"),
        "category_accuracy": float(accuracy_score(actual_bands, predicted_bands)),
        "macro_f1": float(f1_score(actual_bands, predicted_bands, labels=labels, average="macro", zero_division=0)),
    }""", "CodeSnippet")
]

story += [PageBreak()]

# --- SECTION 5: INFERENCE & EXPERIMENTS ---
story += [
    P("7. Live Inference & Feature Importance Serving (backend/main.py)", "H1X"),
    P("How the trained XGBoost model is loaded into memory and invoked for single-click predictions:"),
    Spacer(1, 4),
    P("""# backend/main.py
@lru_cache(maxsize=1)
def _model():
    return joblib.load(MODEL_PATH)  # Cached in memory

@app.post("/predict")
def predict(request: ForecastRequest):
    # If client only provides city name, backend automatically reconstructs 7-day history:
    if request.aqi_today is None:
        frame = _data()
        selected = frame[frame["city"].str.casefold() == request.city.casefold()].sort_values("date")
        recent = selected.tail(7)["aqi"].astype(float).tolist()
        values["aqi_today"] = float(recent[-1])
        values["aqi_lag_1"] = float(recent[-2])
        values["aqi_lag_2"] = float(recent[-3])
        values["aqi_lag_3"] = float(recent[-4])
        values["aqi_lag_7"] = float(recent[0])
    
    # Compute rolling statistics and calendar harmonics
    row = {col: values.get(col, np.nan) for col in FEATURE_COLUMNS}
    row["aqi_rolling_mean_3"] = float(np.mean([values["aqi_today"], values["aqi_lag_1"], values["aqi_lag_2"]]))
    row["aqi_rolling_mean_7"] = float(np.mean(recent))
    row["month_sin"] = float(np.sin(2 * np.pi * today.month / 12))
    row["month_cos"] = float(np.cos(2 * np.pi * today.month / 12))

    # Invoke model
    model = _model()
    estimate = max(0.0, float(model.predict(pd.DataFrame([row], columns=FEATURE_COLUMNS))[0]))
    category = aqi_category(estimate)
    return {"city": request.city, "forecast_aqi": round(estimate, 1), "category": category, ...}""", "CodeSnippet"),
    Spacer(1, 6),

    P("8. Cross-City Transfer & Few-Shot Adaptation (src/experiments.py)", "H1X"),
    P("The experimental core testing whether models trained on one city can predict unseen cities:"),
    bullet("<b>Zero-Shot Transfer (<code>run_transfer</code>):</b> Trains an estimator exclusively on <code>train_city</code> and evaluates it on <code>test_city</code> without any retraining."),
    bullet("<b>Few-Shot Adaptation (<code>run_few_shot</code>):</b> Tests how adding 30, 60, or 90 days of local target-city adaptation data reduces transfer error:"),
    Spacer(1, 4),
    P("""# src/experiments.py
def run_few_shot(data_path=None, test_year=None, days=(30, 60, 90)):
    # Evaluates error reduction when a globally trained model receives local fine-tuning:
    for city in sorted(test_rows["city"].unique()):
        global_train = train_rows[train_rows["city"] != city]
        for adaptation_days in (0, *days):
            local_adaptation = local_history.tail(adaptation_days) if adaptation_days else pd.DataFrame()
            training = pd.concat([global_train, local_adaptation], ignore_index=True)
            estimator = _estimator().fit(training[FEATURE_COLUMNS], training["target"])
            predictions = estimator.predict(local_test[FEATURE_COLUMNS])
            rows.append({"city": city, "local_days": adaptation_days, **_scores(local_test['target'], predictions)})""", "CodeSnippet")
]

def add_header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#65736f"))
    canvas.drawString(40, A4[1] - 25, "Can Delhi Teach Surat? | AQI Research Lab — ML Pipeline & Code Specification")
    canvas.drawRightString(A4[0] - 40, A4[1] - 25, "Core ML Pipeline Guide")
    canvas.setStrokeColor(colors.HexColor("#d5deda"))
    canvas.setLineWidth(0.5)
    canvas.line(40, A4[1] - 30, A4[0] - 40, A4[1] - 30)
    canvas.line(40, 36, A4[0] - 40, 36)
    canvas.drawString(40, 22, "Technical Code Specification · Machine Learning Engineering Lifecycle")
    canvas.drawRightString(A4[0] - 40, 22, f"Page {doc.page}")
    canvas.restoreState()

doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
print("SUCCESS: Cleanly generated " + OUTPUT)
