from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether

OUTPUT = "docs/AQI_Project_Viva_Guide.pdf"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleBig", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=26, leading=31, alignment=TA_CENTER, textColor=colors.HexColor("#12352f")))
styles.add(ParagraphStyle(name="H1X", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=colors.HexColor("#176b60"), spaceBefore=10, spaceAfter=8))
styles.add(ParagraphStyle(name="H2X", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=colors.HexColor("#203b38"), spaceBefore=8, spaceAfter=5))
styles.add(ParagraphStyle(name="BodyX", parent=styles["BodyText"], fontSize=9.2, leading=13, textColor=colors.HexColor("#263332")))
styles.add(ParagraphStyle(name="SmallX", parent=styles["BodyText"], fontSize=7.8, leading=10, textColor=colors.HexColor("#53615f")))
styles.add(ParagraphStyle(name="CodeX", parent=styles["Code"], fontName="Courier", fontSize=7.2, leading=9.5, textColor=colors.HexColor("#17342f"), backColor=colors.HexColor("#edf3ef"), borderPadding=7))

page_width = A4[0]

def P(text, style="BodyX"):
    return Paragraph(text, styles[style])

def table(data, widths=None, font=8):
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#173b37")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME", (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), font),
        ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#becbc6")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f3f6f4")]),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    return t

def bullet(text):
    return P("• " + text)


doc = SimpleDocTemplate(OUTPUT, pagesize=A4, rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42)
story = []

story += [Spacer(1, 0.8*inch), P("AQI NEXT-DAY FORECASTING DASHBOARD", "TitleBig"), Spacer(1, 0.15*inch), P("Complete Viva and Project Explanation Guide", "TitleBig"), Spacer(1, 0.25*inch)]
story += [P("Prepared from the actual workspace code, dataset, model metadata, and deployment configuration.", "SmallX"), Spacer(1, 0.25*inch)]
story += [table([["Project type", "Full-stack machine-learning application"], ["Goal", "Predict next-day AQI from recent AQI history"], ["Backend", "Python, FastAPI, XGBoost"], ["Frontend", "React, Vite, Recharts"], ["Deployment", "Render API and Vercel frontend"]], widths=[125, 330], font=9), PageBreak()] 

story += [P("1. Project in One Sentence", "H1X")]
story += [P("This project is an end-to-end AQI forecasting system that loads daily city-level air-quality data, cleans and normalizes it, creates strictly past-informed lag and rolling features, trains several regression models, selects the best model using a chronological test year, exposes the model through FastAPI, and presents city forecasts through a React dashboard.")]
story += [P("Why this is useful", "H2X"), bullet("It converts historical observations into next-day estimates."), bullet("It hides technical lag calculations from the end user."), bullet("It provides city history, model error, category, and city-comparison views."), bullet("It demonstrates the complete ML lifecycle: data → features → model → API → UI → deployment.")]
story += [P("What it does not claim", "H2X")]
story += [P("It is not an official CPCB forecast or medical advisory. It is a demonstration and learning project based on the available dataset. The user interface should present its output as an estimate, and the API includes a research/advisory disclaimer.")]

story += [P("2. Dataset Used", "H1X")]
story += [P("The active raw dataset is 235005 rows by 9 columns. It covers 291 cities over 2022-04-01 to 2025-04-30. The loaded raw data has four year groups:")]
story += [table([["Year", "Raw rows"], ["2022", "43,287"], ["2023", "77,008"], ["2024", "87,494"], ["2025", "27,216"]], widths=[120, 120], font=9)]
story += [P("Important: feature construction creates 238874 training samples. The sample count is not a second raw-data source; it is the count of valid date-city next-day labels after lag and rolling feature creation.")]
story += [P("Columns observed in the raw load", "H2X")]
story += [P("date, state, city, number_of_monitoring_stations, prominent_pollutants, aqi, air_quality_status, unit, and note.")]
story += [P("Meaning of the main columns", "H2X")]
story += [table([["Column", "Meaning", "Model use"], ["date", "Observation date", "Used for sorting and target-date split"], ["city", "City name", "Grouping; not sent as a model feature"], ["aqi", "Observed AQI", "Target and lag source"], ["prominent_pollutants", "Pollutants associated with the AQI", "Raw metadata; not currently a numeric model feature"], ["air_quality_status", "AQI category/status text", "Reference text, not the regression target"], ["state", "State name", "Not used as a model feature"], ["number_of_monitoring_stations", "Number of stations represented", "Available in raw data; not currently in FEATURE_COLUMNS"]], widths=[125, 145, 140], font=7.5)]

story += [P("3. Data Cleaning and Normalization", "H1X")]
story += [P("Cleaning starts in src/data_utils.py. The code does not assume that every AQI CSV has identical column names. It normalizes aliases before loading.")]
story += [P("Column alias normalization", "H2X")]
story += [P("Examples handled by the alias map: city/area/location → city; date/datetime/day → date; AQI/aqi_value/index → aqi; PM2.5/pm25 → pm25; and weather aliases for temperature, humidity, wind, rainfall, and pressure.")]
story += [P("Cleaning steps in sequence", "H2X")]
clean_steps = [
    ("1", "Find a valid CSV", "find_source() scans data/raw and verifies that city, date, and AQI columns exist."),
    ("2", "Normalize column names", "normalize_columns() maps common field-name variations to one internal schema."),
    ("3", "Convert dates", "pd.to_datetime(..., errors='coerce') converts valid dates; invalid dates become missing."),
    ("4", "Clean city names", "City values are converted to strings and whitespace is removed."),
    ("5", "Convert numeric fields", "Numeric-looking values are converted with errors='coerce', so bad values become missing."),
    ("6", "Remove invalid rows", "Rows without city or date are dropped."),
    ("7", "Remove duplicate city-date rows", "Duplicates keep the last observation for that city and date."),
    ("8", "Sort the data", "The final frame is sorted by city and date."),
]
story += [table([["#", "Step", "Explanation"]] + clean_steps, widths=[30, 125, 255], font=7.5)]

story += [P("Missing values", "H2X")]
story += [P("The raw load has no missing values in date, city, AQI, state, station count, pollutant text, status, or unit. The note column is completely missing (235005 missing values), so it is excluded by meaningful feature selection. Missing weather or pollutant columns can exist for the real data merge and are handled by median imputation during model fitting.")]

story += [P("4. Feature Engineering", "H1X")]
story += [P("Feature engineering is implemented in build_features(). It processes each city independently and creates only values that are known at time t to predict AQI at t+1. City names are retained for grouping and evaluation but are never added to the model feature matrix.")]
story += [P("Target and lag features", "H2X")]
story += [table([["Feature", "Definition"], ["aqi_today", "AQI at day t"], ["aqi_lag_1", "AQI at t-1"], ["aqi_lag_2", "AQI at t-2"], ["aqi_lag_3", "AQI at t-3"], ["aqi_lag_7", "AQI at t-7"], ["aqi_rolling_mean_3", "Mean AQI for the latest 3 observed values"], ["aqi_rolling_mean_7", "Mean AQI for the latest 7 observed values"], ["aqi_rolling_std_3", "Standard deviation over 3 values"], ["aqi_rolling_std_7", "Standard deviation over 7 values"], ["month_sin/cos", "Cyclical representation of month"], ["weekday_sin/cos", "Cyclical representation of weekday"], ["target", "AQI at t+1"]], widths=[160, 280], font=8)]

story += [P("How gaps are handled", "H2X")]
story += [P("The code creates a complete daily index for each city. Missing numeric values are interpolated by time only when the missing gap is inside the city series and no longer than 3 days. If a missing numeric gap is longer than 3 days, it is kept as missing and later handled by the pipeline's median imputer.")]
story += [P("Why the strict rule matters", "H2X")]
story += [P("Lag features use only previous observations. The target is shifted backward by one day. This prevents the model from seeing tomorrow’s value while constructing its input. It is equivalent to X(t) → AQI(t+1), not to training with future labels.")]
story += [P("Important sample counts", "H2X")]
story += [P("The 2025 test year in the model's feature table has 28149 test rows. The metadata says 210725 training rows and 28149 test rows. The total feature table 238874 comes from adding 210725 pre-2025 training rows and 28149 test rows.")]

story += [P("5. Train/Test Strategy", "H1X")]
story += [P("The project uses chronological holdout instead of random train-test splitting. The latest year, 2025, is used as the test year. All feature rows whose target date is before 2025 are training rows. This is important because AQI forecasting is time-dependent and random splitting could leak future patterns.")]
story += [table([["Item", "Value"], ["Test year", "2025"], ["Training rows", "210725"], ["Test rows", "28149"], ["Number of cities", "291"], ["Target", "AQI at t+1"]], widths=[160, 280], font=9)]
story += [P("The persistence baseline is included. It predicts tomorrow's AQI as today's AQI. Every machine-learning model must beat or match this baseline before being considered useful.")]

story += [P("6. Models Compared", "H1X")]
story += [P("The training pipeline compares Persistence, Ridge regression, Random Forest, and XGBoost. For each learner, missing values are median-imputed. Ridge additionally scales features. Predictions are clipped at zero because AQI cannot be negative.")]
story += [table([["Model", "How it works", "Viva summary"], ["Persistence", "Tomorrow = today", "Strong baseline and minimum benchmark"], ["Ridge", "Linear model with L2 penalty", "Fast, interpretable, and stable"], ["Random Forest", "Many decision trees", "Captures non-linear patterns"], ["XGBoost", "Gradient-boosted trees", "Best current RMSE and selected final model"]], widths=[95, 170, 175], font=7.8)]

story += [P("Exact 2025 holdout results", "H2X")]
story += [table([["Model", "MAE", "RMSE", "R²", "Category accuracy", "Macro F1"], ["XGBoost", "20.2201", "29.8203", "0.7107", "73.97%", "0.5025"], ["Ridge", "20.3459", "29.9308", "0.7086", "73.14%", "0.4891"], ["Random Forest", "20.5513", "30.1208", "0.7049", "73.11%", "0.4942"], ["Persistence", "21.1964", "32.5878", "0.6546", "73.19%", "0.5434"]], widths=[72, 58, 58, 52, 85, 55], font=7.2)]
story += [P("How to explain the metrics", "H2X")]
metrics = [
    ("MAE", "Average absolute difference between predicted and actual AQI. Lower is better."),
    ("RMSE", "Square-root of average squared error. Punishes large errors more strongly."),
    ("R²", "How much of the variance in the target is explained by the model. 1 is perfect."),
    ("Category accuracy", "Percentage of predictions assigned to the same AQI category as the actual value."),
    ("Macro F1", "Category quality averaged equally across AQI classes; useful for unequal category counts."),
]
story += [table([["Metric", "Meaning"]] + metrics, widths=[110, 330], font=8)]
story += [P("Selection rule", "H2X")]
story += [P("The selected model is the non-persistence estimator with the lowest held-out RMSE. In the saved metadata, XGBoost is the selected model.")]

story += [P("7. AQI Categories", "H1X")]
story += [table([["AQI range", "Category"], ["0–50", "Good"], ["51–100", "Satisfactory"], ["101–200", "Moderate"], ["201–300", "Poor"], ["301–400", "Very Poor"], ["401+", "Severe"]], widths=[130, 220], font=9)]
story += [P("In viva, explain that category boundaries are rounded into the six Indian AQI bands used by the project. The numeric prediction is first calculated, then aqi_category() converts it to one of these labels.")]

story += [P("8. City-Transfer Experiment", "H1X")]
story += [P("City transfer tests whether a model trained on one city can make useful predictions for another city. It differs from the normal prediction flow:")]
story += [bullet("Normal app prediction: the final XGBoost model is trained on all pre-2025 rows from all cities, then used for a selected city."), bullet("Transfer matrix: for each city, a Random Forest or selected experiment model is trained using that one city and tested on held-out 2025 observations from every city."), bullet("Few-shot adaptation: a model trained on other cities is combined with 0, 30, 60, or 90 local days from the target city.")]
story += [P("How to read the matrix", "H2X")]
story += [P("Rows show the training city. Columns show the testing city. A lower RMSE means better prediction. Diagonal cells test the model on the city from which it learned and are useful references, not pure city-transfer results. Off-diagonal cells are the cross-city transfer results.")]
story += [P("The page currently precomputes 8 supported cities and 64 pairing values. It serves a JSON artifact first, avoiding a long Random Forest retraining call on the hosted API.")]

story += [P("9. Backend API", "H1X")]
story += [P("backend/main.py creates the FastAPI application and connects it to the data, model, and evaluation code.")]
story += [table([["Endpoint", "Method", "Purpose"], ["/health", "GET", "Reports data and model readiness"], ["/cities", "GET", "Returns available cities"], ["/history/{city}", "GET", "Returns recent observations for charting"], ["/predict", "POST", "Predicts tomorrow's AQI"], ["/transfer-matrix", "GET", "Returns precomputed city-pair RMSE values"], ["/explain/{city}", "GET", "Returns model feature importance"]], widths=[130, 55, 255], font=8)]
story += [P("City-only prediction flow", "H2X")]
story += [P("When the frontend sends only {city}, the backend loads the latest 7 rows for that city and fills aqi_today and lag values automatically. It then creates the rolling means and standard deviations, cyclic month/weekday features, and model input frame. The XGBoost pipeline predicts one numeric AQI estimate. The API clips it to zero, converts it into a category, and adds a short advisory.")]
story += [P("CORS", "H2X")]
story += [P("CORS allows browser requests from configured frontend origins. The Render environment variable CORS_ORIGINS stores the Vercel domain. The backend also normalizes trailing slashes and permits Vercel-hosted preview origins through an origin regex.")]

story += [P("10. Frontend", "H1X")]
story += [P("frontend/src/App.jsx provides the user workflow. It uses useEffect to fetch health, city list, and history. It shows 7-day auto-filled AQI values, a city dropdown, prediction button, result card, chart, city comparison, and navigation for transfer, feature importance, and project method pages.")]
story += [P("VITE_API_URL", "H2X")]
story += [P("The frontend reads import.meta.env.VITE_API_URL and otherwise defaults to localhost port 8001 for local development. In Vercel, this variable is set to the Render API base URL. It is a Config value, not a Secret, because it is exposed to browser JavaScript and contains no password or private key.")]
story += [P("Frontend routes", "H2X")]
story += [P("There is a React single-page interface rather than separate HTML pages. State changes switch among Forecast, City transfer, What drives it, and Method views without a full page reload.")]

story += [P("11. Deployment", "H1X")]
story += [table([["Part", "Platform", "Configuration"], ["Backend", "Render", "pip install -r requirements.txt; uvicorn backend.main:app --host 0.0.0.0 --port $PORT"], ["Frontend", "Vercel", "Root: frontend; build: npm run build; output: dist"], ["API URL", "Environment variable", "VITE_API_URL=https://aqi-api-2026.onrender.com"], ["CORS", "Environment variable", "CORS_ORIGINS=https://aqi-etdki.vercel.app"]], widths=[85, 90, 265], font=8)]
story += [P("Free-tier behavior", "H2X")]
story += [P("Render’s free instance can spin down during inactivity and restart on the next request. It may take 50 seconds or more to wake. It can also be interrupted, so `/health` is the first check before a presentation. The frontend remains hosted on Vercel independently.")]

story += [P("12. Actual File and Code Reference", "H1X")]
story += [table([["Topic", "File", "Key code area"], ["Aliases and normalization", "src/data_utils.py", "normalize_columns(), find_source(), load_daily_data()"], ["Lag and rolling features", "src/data_utils.py", "build_features()"], ["Feature list", "src/config.py", "FEATURE_COLUMNS"], ["Model comparison", "src/train.py", "candidates(), train()"], ["Metrics", "src/evaluate.py", "regression_metrics(), aqi_category()"], ["Cross-city experiments", "src/experiments.py", "run_transfer(), run_few_shot()"], ["API endpoints", "backend/main.py", "health, predict, transfer_matrix, explain"], ["Request validation", "backend/schemas.py", "ForecastRequest"], ["UI state/API calls", "frontend/src/App.jsx", "useEffect, submitForecast, TrendChart"], ["Deployment", "render.yaml / frontend/vercel.json", "Build and routing configuration"]], widths=[110, 150, 180], font=7.4)]

story += [P("13. Common Viva Questions and Answers", "H1X")]
qa = [
    ("What is the objective?", "To predict next-day AQI for an Indian city from recent AQI history and supporting features."),
    ("What is the target variable?", "AQI at day t+1."),
    ("Why not random train-test split?", "Random splitting can include future values in training. A chronological split respects time order."),
    ("What is a lag feature?", "A feature using an earlier day's value, such as AQI from yesterday or seven days ago."),
    ("Why are lag features important?", "AQI has temporal dependence; recent values often help explain the next day's value."),
    ("What does median imputation do?", "It replaces missing numeric values with the median of their training column."),
    ("Which model performed best?", "XGBoost selected on held-out RMSE: 29.8203 versus Ridge 29.9308 and Random Forest 30.1208."),
    ("What is MAE?", "The average absolute difference between actual and predicted AQI."),
    ("What is RMSE?", "The square root of mean squared error; it gives more weight to large prediction errors."),
    ("What is R²?", "The proportion of target variance explained by the model; the selected model has 0.7107."),
    ("How is the app informed of a city?", "The user selects a city; the frontend sends city to the backend; the backend loads the latest 7 observations."),
    ("Why use city name as no model feature?", "To test and preserve a city-independent AQI pattern rather than memorizing city identity."),
    ("What is city transfer?", "Testing whether patterns learned in source cities help predictions in another city."),
    ("What is few-shot adaptation?", "Combining broad cross-city training with a small number of target-city observations."),
    ("What is Persistence?", "The baseline that predicts tomorrow as today."),
    ("Why is overfitting possible?", "Complex models can memorize city/year patterns. The 2025 chronological holdout helps identify generalization quality."),
    ("What are limitations?", "Data freshness, missing pollutant/weather coverage, no live source, and one aggregate AQI model across diverse cities."),
    ("What would you improve?", "Live data ingestion, uncertainty intervals, separate pollutant features, expanding-window validation, weather integration, and baseline comparisons."),
    ("Is the API prediction official?", "No. It is a machine-learning estimate for learning and demonstration."),
]
story += [table([["Question", "Suggested answer"]] + qa, widths=[145, 295], font=7.2)]

story += [P("14. Project Limitations and Honest Explanation", "H1X")]
story += [bullet("The active raw data ends at 2025-04-30, so it should not be described as a live forecast."), bullet("Most optional pollutant and weather fields are not populated in the active AQI dataset, so the model mainly relies on AQI history and derived time features."), bullet("XGBoost MAE is about 20.22 AQI points, so one exact number should not be presented as certain."), bullet("The holdout category accuracy is about 73.97%, but category accuracy does not measure numeric error."), bullet("City transfer matrix values are a research evaluation and should not be interpreted as causal evidence."), bullet("No city identity is included in the model feature matrix.")]

story += [P("15. Final 60-Second Viva Summary", "H1X")]
story += [P("Our project is a full-stack AQI forecasting system. The active dataset contains 235005 raw observations for 291 cities from April 2022 to April 2025. We normalize column names and dates, convert numeric fields, remove duplicates, sort observations, and create lag, rolling, and cyclic calendar features for each city. We keep the target as AQI at the next day, so features use only past information. We compare Persistence, Ridge, Random Forest, and XGBoost using a chronological split with 2025 as the test year. XGBoost is selected because it achieves the lowest held-out RMSE of 29.82, with 20.22 MAE and 71.07% R-squared. FastAPI serves health, city history, prediction, transfer, and explanation endpoints, and React presents the forecast and charts. The system is deployed with Render for the API and Vercel for the frontend. It is a learning prototype, not an official AQI or medical advisory.")]

story += [P("17. Code Walkthrough from Dataset to Deployment", "H1X")]
story += [P("This appendix explains the important code blocks. It is enough for a viva: first explain what the code does, then explain why it is necessary, and finally connect it to the output.")]

story += [P("17.1 src/data_utils.py — column alias normalization", "H2X")]
story += [P("Purpose: accept different AQI CSV column names and convert them into one fixed internal schema.", "SmallX")]
story += [P("def _key(value):<br/>    return re.sub(r'[^a-z0-9.]', '', str(value).strip().lower())<br/><br/>def normalize_columns(frame, require_aqi=True):<br/>    lookup = {_key(alias): canonical ...}<br/>    rename = {c: lookup[_key(c)] for c in frame.columns if _key(c) in lookup}<br/>    frame = frame.rename(columns=rename).copy()<br/>    required = {'city', 'date', 'aqi'} ...<br/>    if not required.issubset(frame.columns): raise ValueError(...)<br/>    return frame", "CodeX")]
story += [P("Viva explanation: the aliases allow files named city/area/location to be read as city and aqi_value/AQI/index to be read as AQI. This reduces manual data conversion and makes the loader flexible.")]

story += [P("17.2 src/data_utils.py — loading and cleaning", "H2X")]
story += [P("frame = normalize_columns(pd.read_csv(source))<br/>frame['date'] = pd.to_datetime(frame['date'], errors='coerce', dayfirst=True)<br/>frame['city'] = frame['city'].astype('string').str.strip()<br/>numeric = [column ...]<br/>for column in numeric:<br/>    frame[column] = pd.to_numeric(frame[column], errors='coerce')<br/>frame = frame.dropna(subset=['city', 'date'])<br/>frame = frame.drop_duplicates(['city', 'date'], keep='last')<br/>frame = frame.sort_values(['city', 'date']).reset_index(drop=True)", "CodeX")]
story += [P("Viva explanation: date conversion prevents lexicographic date sorting. errors='coerce' turns invalid numeric values into missing values. Duplicate city-date rows are reduced to the latest/last observation. Sorting makes lag creation chronological.")]

story += [P("17.3 src/data_utils.py — strict past feature construction", "H2X")]
story += [P("aqi = city_frame['aqi'].astype(float)<br/>city_frame['aqi_today'] = aqi<br/>for lag in (1, 2, 3, 7):<br/>    city_frame[f'aqi_lag_{lag}'] = aqi.shift(lag)<br/>for window in (3, 7):<br/>    city_frame[f'aqi_rolling_mean_{window}'] = aqi.rolling(window).mean()<br/>    city_frame[f'aqi_rolling_std_{window}'] = aqi.rolling(window).std()<br/>city_frame['target'] = aqi.shift(-1)<br/>city_frame['target_date'] = city_frame['date'].shift(-1)", "CodeX")]
story += [P("Viva explanation: shift(lag) moves previous values into the current row. shift(-1) creates tomorrow's AQI as target. A lag sample can use AQI(t-1) but never AQI(t+1), so future leakage is avoided.")]

story += [P("17.4 src/config.py — feature list", "H2X")]
story += [P("FEATURE_COLUMNS contains:<br/>aqi_today, aqi_lag_1/2/3/7,<br/>PM2.5 and PM2.5 lags, 3/7-day AQI rolling mean and standard deviation,<br/>optional pollutant fields, weather fields, and month/weekday sine-cosine features.", "CodeX")]
story += [P("Viva explanation: city name is intentionally excluded. If city name were a feature, the model could memorize city identity rather than learn general AQI dynamics.")]

story += [P("17.5 src/train.py — chronological split", "H2X")]
story += [P("year = test_year or int(samples['target_date'].dt.year.max())<br/>train_mask = samples['target_date'].dt.year < year<br/>test_mask = samples['target_date'].dt.year == year<br/>train_rows = samples.loc[train_mask]<br/>test_rows = samples.loc[test_mask]<br/>x_train, y_train = train_rows[FEATURE_COLUMNS], train_rows['target']<br/>x_test, y_test = test_rows[FEATURE_COLUMNS], test_rows['target']", "CodeX")]
story += [P("Viva explanation: this is a time-based holdout. Rows before 2025 are training rows and 2025 rows are testing rows. It does not shuffle observations across years.")]

story += [P("17.6 src/train.py — candidate models", "H2X")]
story += [P("models = {<br/>  'Ridge': make_pipeline(SimpleImputer(), StandardScaler(), Ridge(alpha=10.0)),<br/>  'Random Forest': make_pipeline(SimpleImputer(), RandomForestRegressor(...)),<br/>  'XGBoost': make_pipeline(SimpleImputer(), XGBRegressor(...))<br/>}<br/>scores.append(regression_metrics(y_test, predicted))", "CodeX")]
story += [P("Viva explanation: a pipeline applies the same missing-value treatment to training and testing data. Ridge also scales features. Random Forest and XGBoost learn nonlinear relationships. Persistence is evaluated separately as a naive baseline.")]

story += [P("17.7 src/evaluate.py — metrics and categories", "H2X")]
story += [P("MAE: mean_absolute_error(actual, predicted)<br/>RMSE: sqrt(mean_squared_error(actual, predicted))<br/>R2: r2_score(actual, predicted)<br/>Category accuracy: accuracy_score(actual_bands, predicted_bands)<br/>Macro F1: f1_score(..., average='macro')", "CodeX")]
story += [P("Category code: AQI <=50 Good, <=100 Satisfactory, <=200 Moderate, <=300 Poor, <=400 Very Poor, otherwise Severe. MAE and RMSE measure numeric accuracy; category accuracy and F1 measure band classification.")]

story += [P("17.8 backend/main.py — city-only prediction", "H2X")]
story += [P("selected = frame[city match].sort_values('date')<br/>recent = selected.tail(7)<br/>recent_values = recent['aqi'].astype(float).tolist()<br/>values['aqi_today'] = recent_values[-1]<br/>values['aqi_lag_1'] = recent_values[-2]<br/>values['aqi_lag_2'] = recent_values[-3]<br/>values['aqi_lag_3'] = recent_values[-4]<br/>values['aqi_lag_7'] = recent_values[0]<br/>estimate = model.predict(pd.DataFrame([row], columns=FEATURE_COLUMNS))[0]", "CodeX")]
story += [P("Viva explanation: only the city name is required by the end user. The backend reconstructs the last seven observations and the technical lag features automatically.")]

story += [P("17.9 backend/main.py — static city transfer matrix", "H2X")]
story += [P("static_path = METADATA_PATH.parent.parent / 'results' / 'transfer_matrix.json'<br/>if static_path.exists():<br/>    return json.loads(static_path.read_text(...))", "CodeX")]
story += [P("Viva explanation: the matrix is precomputed instead of retraining Random Forest or Ridge models for every browser request. This improves deployed performance and prevents free-server timeouts.")]

story += [P("17.10 frontend/src/App.jsx — API state and city request", "H2X")]
story += [P("const API = import.meta.env.VITE_API_URL || 'http://localhost:8001'<br/><br/>async function api(path, options) {<br/>    const response = await fetch(`${API}${path}`, options)<br/>    const body = await response.json().catch(() => ({}))<br/>    if (!response.ok) throw new Error(body.detail)<br/>    return body<br/>}", "CodeX")]
story += [P("Viva explanation: VITE_API_URL selects the deployed Render API. The fallback selects the local FastAPI server during development.")]

story += [P("17.11 frontend/src/App.jsx — page state and calls", "H2X")]
story += [P("useEffect(() => {<br/>    api('/health').then(...)<br/>    api('/cities').then(...)<br/>}, [])<br/><br/>submitForecast: setForecast(await api('/predict', {<br/>    method: 'POST',<br/>    headers: {'Content-Type':'application/json'},<br/>    body: JSON.stringify({city})<br/>}))", "CodeX")]
story += [P("Viva explanation: React does not calculate the forecast. It obtains state from FastAPI. The frontend only collects the city, sends the request, and renders the JSON result.")]

story += [P("16. Recommended Presentation Sequence", "H1X")]
story += [P("Slide 1: Problem and objective. Slide 2: Dataset source and dimensions. Slide 3: Cleaning pipeline. Slide 4: Feature engineering with lags. Slide 5: Chronological split. Slide 6: Model comparison table. Slide 7: Why XGBoost won. Slide 8: City-transfer meaning. Slide 9: FastAPI architecture. Slide 10: React dashboard. Slide 11: Deployment and CORS. Slide 12: Limitations and future work.")]


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#65736f"))
    canvas.drawString(42, 22, "AQI Forecasting Dashboard — Viva Guide")
    canvas.drawRightString(A4[0]-42, 22, str(doc.page))
    canvas.restoreState()

doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUTPUT)
