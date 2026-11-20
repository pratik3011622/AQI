from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

OUTPUT = "docs/AQI_ML_Methodology_Viva_Guide.pdf"
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleX", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=24, leading=29, alignment=TA_CENTER, textColor=colors.HexColor("#12352f")))
styles.add(ParagraphStyle(name="H1X", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=colors.HexColor("#176b60"), spaceBefore=9, spaceAfter=7))
styles.add(ParagraphStyle(name="H2X", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11.5, leading=14, textColor=colors.HexColor("#203b38"), spaceBefore=7, spaceAfter=4))
styles.add(ParagraphStyle(name="BodyX", parent=styles["BodyText"], fontSize=8.8, leading=12, textColor=colors.HexColor("#263332")))
styles.add(ParagraphStyle(name="CodeX", parent=styles["Code"], fontName="Courier", fontSize=6.8, leading=8.7, textColor=colors.HexColor("#17342f"), backColor=colors.HexColor("#edf3ef"), borderPadding=6))
styles.add(ParagraphStyle(name="SmallX", parent=styles["BodyText"], fontSize=7.2, leading=9, textColor=colors.HexColor("#53615f")))


def P(text, style="BodyX"):
    return Paragraph(text, styles[style])

def table(data, widths, font=7.5):
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

story = []
doc = SimpleDocTemplate(OUTPUT, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=38, bottomMargin=38)

story += [Spacer(1, 0.7*inch), P("AQI DATASET TO XGBOOST", "TitleX"), Spacer(1, 0.12*inch), P("Machine Learning Methodology and Viva Guide", "TitleX"), Spacer(1, 0.25*inch)]
story += [P("This guide explains every ML stage: cleaning, feature engineering, train/test split, model comparison, metric calculation, model selection, artifact saving, transfer testing, and final deployment inference.", "SmallX")]
story += [Spacer(1, 0.22*inch), table([["Dataset", "235005 raw rows, 291 cities"], ["Date range", "2022-04-01 to 2025-04-30"], ["Target", "AQI at day t+1"], ["Main model", "XGBoost XGBRegressor"], ["Test year", "2025"], ["Selected by", "Lowest held-out RMSE"]], [145, 290], 8.5), PageBreak()] 

story += [P("1. End-to-End ML Pipeline", "H1X")]
story += [P("Raw CSV → schema normalization → date and numeric cleaning → duplicate removal → sorting → daily reindexing → lag features → rolling features → target creation → train/test split → model comparison → best model selection → joblib save → FastAPI load → city prediction")]
story += [P("The central rule is: X(t) predicts AQI(t+1). The city name is never included as an ML feature. It is used only to sort and group observations and to identify the city in API responses.")]

story += [P("2. Dataset and Raw Columns", "H1X")]
story += [P("The active normalized load contains these fields:")]
story += [table([["Column", "Role in project"], ["date", "Sort rows, create daily index, chronological split"], ["city", "Separate observations by city; excluded from feature matrix"], ["aqi", "Target and source for lag/rolling features"], ["state", "Available metadata; not used by model"], ["prominent_pollutants", "Available text metadata; not converted to numeric model features"], ["number_of_monitoring_stations", "Available raw metadata; not in final FEATURE_COLUMNS"], ["air_quality_status", "Category text; not the numeric regression target"], ["unit", "Not used by model"], ["note", "Completely missing, 235005 missing values"]], [155, 290], 7.8)]

story += [P("3. File 1: src/data_utils.py — schema normalization", "H1X")]
story += [P("The first code step maps different CSV names to a single schema.")]
story += [P("ALIASES = {<br/>  'city': {'city','cityname','stationcity','area','location','district'},<br/>  'date': {'date','datetime','day'},<br/>  'aqi': {'aqi','airqualityindex','index','aqi_value','aqivalue'},<br/>  'pm25': {'pm25','pm2.5','pm2_5'}, ...<br/>}", "CodeX")]
story += [P("def normalize_columns(frame, require_aqi=True):<br/>    lookup = {_key(alias): canonical ...}<br/>    rename = {column: lookup[_key(column)] ...}<br/>    frame = frame.rename(columns=rename).copy()<br/>    required = {'city','date','aqi'} if require_aqi else {'city','date'}<br/>    if not required.issubset(frame.columns): raise ValueError(...)<br/>    return frame", "CodeX")]
story += [P("Viva explanation: if a file calls the location column area or the AQI column aqi_value, the code converts both to standard names city and aqi. This is schema standardization, not model cleaning.")]

story += [P("4. File 2: src/data_utils.py — find and load CSV", "H1X")]
story += [P("source = find_source(path)<br/>frame = normalize_columns(pd.read_csv(source))<br/>frame['date'] = pd.to_datetime(frame['date'], errors='coerce', dayfirst=True)<br/>frame['city'] = frame['city'].astype('string').str.strip()<br/>for column in numeric_columns:<br/>    frame[column] = pd.to_numeric(frame[column], errors='coerce')", "CodeX")]
story += [P("Why these steps are used:")]
story += [bullet("pd.to_datetime() converts date strings into comparable datetime values."), bullet("errors='coerce' makes invalid dates or numbers missing instead of crashing."), bullet("str.strip() removes unwanted whitespace from city names."), bullet("pd.to_numeric() ensures calculations receive numbers, not text.")]

story += [P("Duplicate and missing-row removal", "H2X")]
story += [P("frame = frame.dropna(subset=['city','date'])<br/>frame = frame.drop_duplicates(['city','date'], keep='last')<br/>frame = frame.sort_values(['city','date']).reset_index(drop=True)", "CodeX")]
story += [P("This keeps one observation per city-date. Duplicate city-date rows keep the last version. Missing city or date rows cannot be ordered or grouped correctly, so they are removed.")]

story += [P("5. Missing-value handling", "H1X")]
story += [P("The raw load has no missing values in date, city, AQI, state, monitoring station count, pollutants text, status, and unit. The note column is completely missing. Missing weather/pollutant columns can appear when a weather merge is absent.")]
story += [P("For feature rows, SimpleImputer(strategy='median') is added inside each model pipeline. This replaces missing feature values with a median learned from training data.")]
story += [P("Within build_features(), a missing daily value is interpolated only if the internal missing gap is at most 3 days and is located inside the city observation series. A gap longer than 3 days remains missing.")]

story += [P("6. Feature engineering: lag and rolling features", "H1X")]
story += [P("Each city is processed separately:")]
story += [P("for city, city_frame in frame.groupby('city'):<br/>    city_frame = city_frame.sort_values('date').set_index('date')<br/>    daily_index = pd.date_range(min_date, max_date, freq='D')<br/>    city_frame = city_frame.reindex(daily_index)", "CodeX")]
story += [P("This creates a complete daily timeline for that city. A missing date becomes a missing daily row, not an unknown next city date.")]
story += [P("Lag and target code:")]
story += [P("aqi = city_frame['aqi'].astype(float)<br/>city_frame['aqi_today'] = aqi<br/>city_frame['aqi_lag_1'] = aqi.shift(1)<br/>city_frame['aqi_lag_2'] = aqi.shift(2)<br/>city_frame['aqi_lag_3'] = aqi.shift(3)<br/>city_frame['aqi_lag_7'] = aqi.shift(7)<br/>city_frame['target'] = aqi.shift(-1)<br/>city_frame['target_date'] = city_frame['date'].shift(-1)", "CodeX")]

story += [P("Viva explanation of a row", "H2X")]
story += [table([["Feature", "Meaning"], ["aqi_today", "AQI at day t"], ["aqi_lag_1", "AQI at day t-1"], ["aqi_lag_2", "AQI at day t-2"], ["aqi_lag_3", "AQI at day t-3"], ["aqi_lag_7", "AQI at day t-7"], ["target", "AQI at day t+1"]], [165, 275], 8)]
story += [P("For example, if today is 200 AQI and yesterday is 190, lag_1 is 190 and target is tomorrow's real AQI.")]

story += [P("Rolling features", "H1X")]
story += [P("city_frame['aqi_rolling_mean_3'] = aqi.rolling(3, min_periods=3).mean()<br/>city_frame['aqi_rolling_mean_7'] = aqi.rolling(7, min_periods=7).mean()<br/>city_frame['aqi_rolling_std_3'] = aqi.rolling(3, min_periods=3).std()<br/>city_frame['aqi_rolling_std_7'] = aqi.rolling(7, min_periods=7).std()", "CodeX")]
story += [P("Rolling mean shows average recent pollution. Rolling standard deviation shows how much the AQI has moved. The code creates these values only from observations available up to the current row.")]

story += [P("Cyclical time features", "H1X")]
story += [P("month_sin = sin(2π × month / 12)<br/>month_cos = cos(2π × month / 12)<br/>weekday_sin = sin(2π × weekday / 7)<br/>weekday_cos = cos(2π × weekday / 7)", "CodeX")]
story += [P("Viva explanation: sine/cosine convert cyclic time to numerical coordinates. January and December become close in the circular month representation, avoiding a false 1-to-12 linear distance.")]

story += [P("Final feature table and target filtering", "H1X")]
story += [P("required = ['aqi_today','aqi_lag_1','aqi_lag_2','aqi_lag_3','aqi_lag_7']<br/>result = result.dropna(subset=required + ['target'])", "CodeX")]
story += [P("This removes rows that do not contain enough past history or do not have a next-day label. It creates 238874 valid feature samples from 235005 raw rows.")]

story += [P("7. Chronological Train/Test Split", "H1X")]
story += [P("year = test_year or int(samples['target_date'].dt.year.max())<br/>train_mask = samples['target_date'].dt.year < year<br/>test_mask = samples['target_date'].dt.year == year<br/>train_rows = samples.loc[train_mask]<br/>test_rows = samples.loc[test_mask]", "CodeX")]
story += [table([["Part", "Rows", "Year rule"], ["Training", "210725", "target date before 2025"], ["Testing", "28149", "target date in 2025"]], [160, 100, 180], 8)]
story += [P("The project does not use random train_test_split because random splitting would allow a model to see neighboring future patterns and violate chronological forecasting.")]

story += [P("8. Model Comparison Code", "H1X")]
story += [P("scores = [{'model':'Persistence', **regression_metrics(y_test, test_rows['aqi_today'])}]<br/>for name, estimator in candidates().items():<br/>    estimator.fit(x_train, y_train)<br/>    prediction = clip(estimator.predict(x_test), 0, None)<br/>    scores.append({'model': name, **regression_metrics(y_test, prediction)})", "CodeX")]

story += [P("Persistence baseline", "H2X")]
story += [P("A simple forecast where tomorrow = today. It sets a minimum benchmark; a usable model should generally improve this baseline.")]

story += [P("Ridge regression", "H2X")]
story += [P("make_pipeline(<br/>  SimpleImputer(strategy='median'),<br/>  StandardScaler(),<br/>  Ridge(alpha=10.0)<br/>)", "CodeX")]
story += [P("Ridge is a linear regression model with L2 regularization. Scaling makes features comparable. Alpha 10 controls regularization strength and discourages very large coefficients.")]

story += [P("Random Forest", "H2X")]
story += [P("make_pipeline(<br/>  SimpleImputer(strategy='median'),<br/>  RandomForestRegressor(<br/>    n_estimators=300,<br/>    min_samples_leaf=2,<br/>    max_features=0.8,<br/>    random_state=42,<br/>    n_jobs=-1<br/>  )<br/>)", "CodeX")]
story += [P("Random Forest combines 300 decision trees. min_samples_leaf=2 prevents overly small leaf groups, max_features=0.8 selects 80% of features for each split search, and random_state=42 makes the experiment reproducible.")]

story += [P("XGBoost", "H2X")]
story += [P("make_pipeline(<br/>  SimpleImputer(strategy='median'),<br/>  XGBRegressor(<br/>    n_estimators=400,<br/>    max_depth=5,<br/>    learning_rate=0.04,<br/>    subsample=0.85,<br/>    colsample_bytree=0.85,<br/>    objective='reg:squarederror',<br/>    random_state=42,<br/>    n_jobs=-1<br/>  )<br/>)", "CodeX")]
story += [P("XGBoost builds 400 sequential trees. Each later tree reduces errors left by earlier trees. max_depth=5 limits tree complexity, learning_rate=0.04 controls the size of each correction, subsample=0.85 uses 85% of rows, and colsample_bytree=0.85 uses 85% of features.")]

story += [P("9. Metrics Code", "H1X")]
story += [P("return {<br/>  'mae': mean_absolute_error(actual, predicted),<br/>  'rmse': sqrt(mean_squared_error(actual, predicted)),<br/>  'r2': r2_score(actual, predicted),<br/>  'category_accuracy': accuracy_score(actual_bands, predicted_bands),<br/>  'macro_f1': f1_score(actual_bands, predicted_bands, average='macro')<br/>}", "CodeX")]
story += [table([["Metric", "Meaning", "Lower or higher is better?"], ["MAE", "Average absolute numeric error", "Lower"], ["RMSE", "Numeric error with extra penalty for large errors", "Lower"], ["R²", "Explained target variance", "Higher"], ["Category accuracy", "Percent matching AQI category", "Higher"], ["Macro F1", "Balanced category quality", "Higher"]], [120, 230, 90], 7.5)]

story += [P("10. Final Model Selection", "H1X")]
story += [P("selected = min(<br/>    (score for score in scores if score['model'] != 'Persistence'),<br/>    key=lambda score: score['rmse']<br/>)<br/>best = fitted[selected['model']]<br/>joblib.dump(best, MODEL_PATH)", "CodeX")]
story += [P("The selector compares only the machine-learning candidates, excludes Persistence, and chooses the lowest RMSE. XGBoost is saved to models/best_model.joblib, and metadata is written to models/metadata.json.")]

story += [P("11. 2025 Holdout Results", "H1X")]
story += [table([["Model", "MAE", "RMSE", "R²", "Category accuracy", "Macro F1"], ["XGBoost", "20.2201", "29.8203", "0.7107", "73.97%", "0.5025"], ["Ridge", "20.3459", "29.9308", "0.7086", "73.14%", "0.4891"], ["Random Forest", "20.5513", "30.1208", "0.7049", "73.11%", "0.4942"], ["Persistence", "21.1964", "32.5878", "0.6546", "73.19%", "0.5434"]], [74, 54, 58, 52, 82, 58], 7)]
story += [P("Final interpretation: XGBoost has the lowest RMSE, 29.82, and lowest MAE among ML models, 20.22. Its R² is 0.7107, so it explains about 71.07% of target variance in the held-out test year. Persistence has worse RMSE and MAE, proving the ML models add value over simply repeating today's AQI.")]

story += [P("12. City-Transfer Experiment", "H1X")]
story += [P("In src/experiments.py, transfer_matrix() trains on one city and tests on 2025 observations in another city. It is useful for studying cross-city generalization.")]
story += [P("For each training city:<br/>    fit model on that city's pre-2025 rows<br/>    for each test city:<br/>        predict 2025 rows from test city<br/>        calculate RMSE", "CodeX")]
story += [P("The display currently uses a precomputed JSON artifact of 8 supported cities and 64 pairwise values. This avoids retraining on every browser request.")]

story += [P("13. Final Inference Code", "H1X")]
story += [P("model = joblib.load(MODEL_PATH)<br/>estimate = model.predict(pd.DataFrame([row], columns=FEATURE_COLUMNS))[0]<br/>estimate = max(0.0, float(estimate))<br/>category = aqi_category(estimate)", "CodeX")]
story += [P("The saved XGBoost pipeline includes median imputation and the fitted XGBoost estimator. The API constructs the feature row, predicts, clips negative values, and converts the numeric prediction to an AQI category.")]

story += [P("14. Viva Script: 90 Seconds", "H1X")]
story += [P("We first loaded 235005 daily city observations from 291 cities and normalized the CSV schema. We cleaned dates and numbers, removed invalid city-date rows and duplicates, and sorted the data chronologically. We built past-only features including today AQI, one/two/three/seven-day lags, rolling mean and standard deviation, and cyclic month and weekday features. We used 2025 as the chronological test year, with 210725 training rows and 28149 testing rows. We compared Persistence, Ridge, Random Forest, and XGBoost using MAE, RMSE, R-squared, category accuracy, and Macro F1. XGBoost gave the lowest RMSE of 29.8203 and lowest MAE of 20.2201, so it was saved for FastAPI inference. The backend fills the final city lag row automatically from the latest seven observations. The app does not calculate the model result; it sends the city to the API and displays the prediction.")]

story += [P("15. Viva Questions to Memorize", "H1X")]
qa = [
("What is supervised learning here?", "Each row has input features and a next-day AQI target."),
("What is one sample?", "One city-date row with AQI history and time features."),
("Why is lag 7 useful?", "It provides a weekly pattern."),
("Why use rolling mean?", "It summarizes recent pollution trend instead of one isolated day."),
("Why use standard deviation?", "It captures short-term variability."),
("Why is Random Forest not the final model?", "Its held-out RMSE was 30.1208, higher than XGBoost 29.8203."),
("Why was XGBoost selected?", "It had the lowest held-out RMSE among all ML candidates."),
("Why use 2025 only for testing?", "It prevents future observations from entering training."),
("What is median imputation?", "Replacing missing values with median from the training data."),
("What is overfitting?", "Learning training patterns that fail on unseen data."),
("How is overfitting tested?", "By comparing training and chronological held-out 2025 performance."),
("What does R² mean?", "About 71.07% of held-out target variance is explained by XGBoost."),
("What is category accuracy?", "Percent of predicted AQI bands matching actual bands."),
("What is the final artifact?", "models/best_model.joblib plus metadata.json."),
]
story += [table([["Question", "Answer"]] + qa, [145, 295], 7)]

story += [P("16. Presentation of Results", "H1X")]
story += [P("Show this table in the viva: XGBoost selected as the final model; Ridge close behind; Random Forest slightly worse; Persistence weakest. State that MAE is about 20 AQI points and RMSE about 30 AQI points. Do not claim exact real-world accuracy, and do not present the dataset end date as live data.")]

story += [P("17. Recommended Presentation Sequence", "H1X")]
story += [P("Dataset → Cleaning code → Lag feature code → Chronological split → Pipeline and models → Metric table → XGBoost selection → Saved artifact → Backend inference → Frontend result → Limitations.")]

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#65736f"))
    canvas.drawString(40, 22, "AQI ML Methodology — Viva Guide")
    canvas.drawRightString(A4[0]-40, 22, str(doc.page))
    canvas.restoreState()

doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUTPUT)
