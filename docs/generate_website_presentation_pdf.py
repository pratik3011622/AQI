from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether

OUTPUT = "docs/AQI_Website_Presentation_and_Viva_Guide.pdf"

styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    name="CoverPre", fontName="Helvetica-Bold", fontSize=9.5, leading=13,
    alignment=TA_CENTER, textColor=colors.HexColor("#176b60")
))
styles.add(ParagraphStyle(
    name="CoverTitle", fontName="Helvetica-Bold", fontSize=20, leading=25,
    alignment=TA_CENTER, textColor=colors.HexColor("#12352f")
))
styles.add(ParagraphStyle(
    name="CoverSubtitle", fontName="Helvetica", fontSize=11, leading=15,
    alignment=TA_CENTER, textColor=colors.HexColor("#344c48")
))
styles.add(ParagraphStyle(
    name="CoverURL", fontName="Courier-Bold", fontSize=9, leading=12,
    alignment=TA_CENTER, textColor=colors.HexColor("#0f5146")
))

styles.add(ParagraphStyle(
    name="H1X", fontName="Helvetica-Bold", fontSize=13, leading=17,
    textColor=colors.HexColor("#176b60"), spaceBefore=10, spaceAfter=5, keepWithNext=True
))
styles.add(ParagraphStyle(
    name="H2X", fontName="Helvetica-Bold", fontSize=10, leading=14,
    textColor=colors.HexColor("#203b38"), spaceBefore=7, spaceAfter=3, keepWithNext=True
))
styles.add(ParagraphStyle(
    name="BodyX", fontName="Helvetica", fontSize=8.5, leading=12,
    textColor=colors.HexColor("#243130"), alignment=TA_JUSTIFY, spaceAfter=3
))
styles.add(ParagraphStyle(
    name="SmallX", fontName="Helvetica", fontSize=7.5, leading=10,
    textColor=colors.HexColor("#53615f")
))
styles.add(ParagraphStyle(
    name="Callout", fontName="Helvetica-Oblique", fontSize=8.2, leading=11.5,
    textColor=colors.HexColor("#134e44"), backColor=colors.HexColor("#eef5f2"),
    borderPadding=6, spaceBefore=4, spaceAfter=5
))
styles.add(ParagraphStyle(
    name="QuesX", fontName="Helvetica-Bold", fontSize=9, leading=12.5,
    textColor=colors.HexColor("#12352f"), spaceBefore=6, spaceAfter=2, keepWithNext=True
))
styles.add(ParagraphStyle(
    name="AnsX", fontName="Helvetica", fontSize=8.3, leading=11.8,
    textColor=colors.HexColor("#2a3836"), spaceAfter=5
))

styles.add(ParagraphStyle(
    name="TableHeader", fontName="Helvetica-Bold", fontSize=7.5, leading=10,
    textColor=colors.white, alignment=TA_LEFT
))
styles.add(ParagraphStyle(
    name="TableCell", fontName="Helvetica", fontSize=7.2, leading=9.8,
    textColor=colors.HexColor("#243130"), alignment=TA_LEFT
))
styles.add(ParagraphStyle(
    name="TableCellBold", fontName="Helvetica-Bold", fontSize=7.2, leading=9.8,
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
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    return t

doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=52, bottomMargin=52
)
story = []

# --- COVER / TITLE BLOCK ---
story += [
    P("RESEARCH LAB & VIVA DEFENSE GUIDE", "CoverPre"),
    Spacer(1, 4),
    P("Can Delhi Teach Surat?<br/>Air Quality Forecasting & Transfer Dashboard", "CoverTitle"),
    Spacer(1, 4),
    P("Full-Stack Architecture, Interactive Walkthrough, Methodology & Defense Answers", "CoverSubtitle"),
    Spacer(1, 4),
    P("Live System: https://aqi-etdki.vercel.app/", "CoverURL"),
    Spacer(1, 8),
]

summary_data = [
    ["System Dimension", "Engineering Specification"],
    ["Central Research Question", "Can an ML model trained on a data-rich city forecast air quality in an unseen city without city labels?"],
    ["Machine Learning Model", "XGBoost Regressor (Pipeline: SimpleImputer -> XGBRegressor, evaluated chronologically)"],
    ["Temporal Baseline", "Persistence Baseline (Today -> Tomorrow, AQI(t+1) = AQI(t))"],
    ["Backend Web Framework", "Python 3.11+, FastAPI, Uvicorn, Pydantic v2 (hosted on Render)"],
    ["Frontend UI & Dashboard", "React 18, Vite, Recharts, Lucide Icons (hosted on Vercel)"],
    ["Live Air Quality Feed", "Open-Meteo Air Quality API (US AQI scale via coordinates for 35+ major Indian cities)"],
    ["Historical Training Dataset", "235,005 daily observations covering 291 Indian cities (2022-04-01 to 2025-04-30)"],
    ["Validation Strategy", "Strict chronological test split (Train < 2025, Test == 2025) avoiding lookahead data leakage"]
]
story += [make_table(summary_data, widths=[145, 370]), Spacer(1, 8)]

# --- SECTION 1: THE 60-SECOND PITCH ---
story += [
    P("1. The 60-Second Presentation Hook", "H1X"),
    P("<i>\"Traditional air quality systems build isolated models for single cities by memorizing local sensor IDs. Our project tests a fundamental premise: Can an AI model trained on a sensor-dense metropolis (like Delhi) generalize to a sensor-sparse industrial city (like Surat) where historical training data is scarce? By intentionally stripping city identity from the feature matrix and learning pure physical dynamics—autocorrelation, rolling momentum, and calendar seasonality—we demonstrate zero-shot cross-city forecasting through an interactive full-stack dashboard.\"</i>", "Callout"),
    P("<b>Core Project Significance:</b>"),
    bullet("<b>Full Data-to-Deployment Lifecycle:</b> Ingests 235k raw CPCB records, normalizes schemas, constructs past-only lag features, evaluates 4 model paradigms, exposes a FastAPI backend, and renders a reactive React UI."),
    bullet("<b>Cross-City Generalization Matrix:</b> Benchmarks true transfer error (RMSE) when testing models on cities they have never seen during training."),
    bullet("<b>Dual-Scale Transparency:</b> Clearly decouples real-time ambient US AQI readings (via Open-Meteo API) from next-day Indian National AQI forecasts (via XGBoost), educating users on international vs domestic standards.")
]

story += [PageBreak()]

# --- SECTION 2: PAGE-BY-PAGE UI WALKTHROUGH ---
story += [
    P("2. Comprehensive Dashboard Walkthrough", "H1X"),
    P("The web application is partitioned into 4 distinct scientific workspaces, each serving a specific research objective:"),
    Spacer(1, 4),

    P("2.1 Forecast Workspace (/forecast)", "H2X"),
    P("The operational centerpiece where evaluators interact with predictions and real-time sensor streams:"),
    bullet("<b>Header Status & Copy:</b> Displays <i>'Current AQI, with context.'</i> and <i>'MODEL READY'</i> indicating live connection to the Render FastAPI server."),
    bullet("<b>City Selection Dropdown:</b> Dynamically populated with 35+ supported Indian cities. When selected, the backend automatically retrieves that city's latest 7-day historical sequence."),
    bullet("<b>Auto-Filled AQI Card:</b> Displays the last 7 observed AQI numbers as mini-pills (t-7 to t-1). Users do not have to manually input or calculate technical lag values."),
    bullet("<b>Live Current AQI Card (Open-Meteo):</b> Queries Open-Meteo's API using the selected city's latitude/longitude. Displays the live ambient reading, marked with the <b>US AQI</b> scale badge and an Indian Standard Time (IST) observation timestamp."),
    bullet("<b>Next-Day Model Forecast Panel:</b> Outputs tomorrow's forecasted AQI number, color-coded official CPCB health category pill (Good, Satisfactory, Moderate, Poor, Very Poor, Severe), and medical advisory guidance."),
    bullet("<b>Holdout Error Reference:</b> Shows the test-year Mean Absolute Error (<b>MAE: ~20.2 AQI points</b>). This teaches viewers that ML estimates come with an empirical confidence margin rather than false certainty."),
    bullet("<b>Metrics Summary Bar:</b> Highlights 7-day movement (+/- points), holdout MAE, monitored city count, and the Persistence benchmark."),
    bullet("<b>Interactive Recharts Timeline:</b> Displays 7-day, 30-day, and 90-day historical trajectories with an optional comparison city overlay (e.g. comparing Delhi vs. Bengaluru)."),
    bullet("<b>Data Note Footnote:</b> Explicitly warns that live readings follow the US AQI standard while the next-day estimate is an XGBoost model trained on Indian NAQI data."),
    Spacer(1, 6),

    P("2.2 City Transfer Matrix Workspace (/transfer)", "H2X"),
    P("The academic core answering: <i>'Can one city's historical dynamics forecast another?'</i>"),
    bullet("<b>How to Read the Table:</b> Rows represent the <b>Training City</b>; Columns represent the <b>Testing City</b>. The displayed metric is <b>RMSE (Root Mean Squared Error)</b> in AQI points (lower is better)."),
    bullet("<b>The Diagonal (Self-Performance):</b> The model is trained and tested on the <i>same</i> city (e.g. Train Delhi -> Test Delhi). This acts as the upper-bound performance ceiling."),
    bullet("<b>Off-Diagonal Cells (Zero-Shot Transfer):</b> The model is trained on City A and tested directly on City B without seeing any City B training samples. A low RMSE indicates that atmospheric pollution dynamics are transferable across geographies."),
    bullet("<b>Three Core Transfer Principles:</b> (1) Past -> Future chronological split; (2) City Name completely excluded from inputs; (3) Evaluated against the Today -> Tomorrow persistence baseline."),
    Spacer(1, 6),

    P("2.3 Feature Importance Workspace (/explain)", "H2X"),
    P("Provides global explainability and transparency for the trained gradient-boosted trees:"),
    bullet("<b>Top Ranking Features:</b> (1) <code>aqi_today</code> (recency effect); (2) <code>aqi_rolling_mean_7</code> (multi-day pollution accumulation); (3) <code>aqi_rolling_mean_3</code> (short-term momentum); (4) <code>aqi_lag_1</code> (rate-of-change); (5) Trigonometric harmonics (<code>month_sin</code>, <code>month_cos</code>)."),
    bullet("<b>Importance vs Causality Disclaimer:</b> Explicitly highlights that Gini/split importance describes how the tree algorithm segments variance, not that a feature causes pollution physically."),
    Spacer(1, 6),

    P("2.4 Method Notes Workspace (/method)", "H2X"),
    P("Documents scientific rigor across 4 pillars: (1) Cross-city transfer question; (2) Lag, rolling, and harmonic feature formulation; (3) Forward-chaining temporal validation preventing future leakage; (4) Multi-metric evaluation (MAE, RMSE, R-squared, and Category Macro-F1).")
]

story += [PageBreak()]

# --- SECTION 3: SYSTEM ARCHITECTURE & DATA FLOW ---
story += [
    P("3. End-to-End System Architecture", "H1X"),
    P("The system uses an enterprise split-stack architecture configured for zero maintenance and instant client delivery:"),
    Spacer(1, 4)
]

arch_table = [
    ["Component", "Technology", "Role & Execution Details"],
    ["Raw Data Storage", "data/raw/aqi.csv", "235,005 rows covering 291 cities. Ingested via data_utils.py with automatic schema aliasing."],
    ["Feature Pipeline", "src/data_utils.py", "Constructs past-only lags (1, 2, 3, 7), 3/7-day rolling means/stds, and sine/cosine calendar harmonics."],
    ["Trained Artifacts", "models/best_model.joblib", "Optimized XGBoost Regressor pipeline bundled with SimpleImputer and metadata.json."],
    ["Backend API", "FastAPI on Render", "Exposes /health, /cities, /history/{city}, /live/{city}, /predict, /transfer-matrix, and /explain."],
    ["Live Sensor Provider", "Open-Meteo REST API", "Queried asynchronously by the backend to fetch current ambient US AQI for city coordinates."],
    ["Frontend Dashboard", "React 18 + Vite on Vercel", "Client-side SPA with Recharts data visualization and mobile-responsive drawer navigation."],
    ["Cache & Routing", "frontend/vercel.json", "Enforces Cache-Control: no-cache on index.html to guarantee instantaneous client updates."]
]
story += [make_table(arch_table, widths=[95, 120, 300]), Spacer(1, 8)]

story += [
    P("Key Algorithmic Implementations", "H2X"),
    bullet("<b>Strict Past-Only Shifting:</b> Features use <code>aqi.shift(lag)</code> while the target is <code>aqi.shift(-1)</code>. No sample can ever observe future timestamps during training."),
    bullet("<b>Controlled Interpolation:</b> Missing sensor gaps are linearly interpolated within a city <i>only if the gap is <= 3 days</i>. Multi-week blackouts are retained as missing to avoid hallucinating synthetic air quality trends."),
    bullet("<b>Trigonometric Calendar Encoding:</b> Standard integers treat Dec (12) and Jan (1) as 11 units apart. We map months onto a unit circle via sin(2*pi*m/12) and cos(2*pi*m/12), preserving winter continuity.")
]

story += [Spacer(1, 6), P("4. Model Comparison & Experimental Results", "H1X")]

model_table = [
    ["Model Architecture", "Held-out RMSE", "Held-out MAE", "R² Score", "Category Accuracy", "Evaluation Verdict"],
    ["Persistence Baseline", "32.59 pts", "21.20 pts", "65.5%", "73.2%", "Benchmark: Tomorrow = Today (No ML)"],
    ["Ridge Regression (alpha=10)", "29.93 pts", "20.35 pts", "70.9%", "73.1%", "Linear regularized baseline with feature scaling"],
    ["Random Forest (300 trees)", "30.12 pts", "20.55 pts", "70.5%", "73.1%", "Non-linear bagging ensemble; ~140MB memory footprint"],
    ["XGBoost Regressor (Selected)", "29.82 pts", "20.22 pts", "71.1%", "74.0%", "Best performance: Lowest error and fastest inference"]
]
story += [make_table(model_table, widths=[115, 65, 65, 50, 75, 145]), Spacer(1, 6)]
story += [P("<b>Why XGBoost Won:</b> Gradient boosting iteratively minimizes residual errors through second-order Taylor approximations. It effectively captures abrupt non-linear transitions (e.g. rapid post-Diwali inversions) that linear Ridge models smooth out, while running with a lightweight 1.1 MB serialized memory footprint.")]

story += [PageBreak()]

# --- SECTION 4: TOP 8 VIVA DEFENSE QUESTIONS ---
story += [
    P("5. Top 8 Viva Defense Questions & Winning Answers", "H1X"),
    P("Be prepared to answer these exact technical inquiries during your presentation defense:"),
    Spacer(1, 4),

    P("Q1: Why did you intentionally exclude the city name as a feature in your model?", "QuesX"),
    P("<b>Winning Answer:</b> <i>\"If we include city name as a categorical feature, the tree algorithm splits on specific city IDs and memorizes local geographic intercepts. In our cross-city transfer experiment, the model would encounter an unseen city at inference time, leading to out-of-vocabulary failure. By omitting city labels, the model is compelled to learn universal atmospheric dynamics—autocorrelation, rate-of-change, rolling momentum, and calendar seasonality—enabling true zero-shot cross-city forecasting.\"</i>", "AnsX"),

    P("Q2: Why can't we use standard K-Fold Cross Validation for this dataset?", "QuesX"),
    P("<b>Winning Answer:</b> <i>\"Standard K-Fold randomly shuffles data rows. In time-series data, random shuffling allows future observations (e.g. October 2024) to train predictions for past observations (e.g. January 2024). This causes catastrophic lookahead leakage, giving artificially inflated scores. We enforce strict temporal validation: data strictly prior to 2025 forms the training set, and the held-out year 2025 forms the unseen test set.\"</i>", "AnsX"),

    P("Q3: What is the difference between the live Open-Meteo reading and your XGBoost prediction?", "QuesX"),
    P("<b>Winning Answer:</b> <i>\"Open-Meteo provides real-time ambient sensor readings calculated on the US EPA AQI standard. Our predictive model, in contrast, was trained on historical Central Pollution Control Board (CPCB) data following the Indian National AQI (NAQI) scale. Because the two standards use different sub-index breakpoints and pollutant weights, we display them side-by-side with distinct labels rather than conflating them under one misleading number.\"</i>", "AnsX"),

    P("Q4: What is the Persistence Baseline and why is it essential?", "QuesX"),
    P("<b>Winning Answer:</b> <i>\"In atmospheric science, persistence assumes that tomorrow's weather will simply equal today's (y_hat_{t+1} = y_t). Because air quality has high daily autocorrelation, persistence often achieves an deceptively low MAE. Any machine learning model that cannot beat persistence adds zero real predictive value. XGBoost achieved an RMSE of 29.82 compared to persistence's 32.59, validating genuine predictive intelligence.\"</i>", "AnsX"),

    P("Q5: How do you handle sensor dropouts and missing dates in real CPCB stations?", "QuesX"),
    P("<b>Winning Answer:</b> <i>\"In src/data_utils.py, we apply linear interpolation within a city only for minor gaps of 3 consecutive days or fewer. If a monitoring station goes offline for weeks or months, we refuse to interpolate or synthesize fake numbers; those dates are dropped to prevent training on fabricated signals. During model training, an sklearn SimpleImputer handles any remaining isolated null values.\"</i>", "AnsX"),

    P("Q6: Why did you encode dates using sine and cosine functions?", "QuesX"),
    P("<b>Winning Answer:</b> <i>\"If month is represented as an integer (1 to 12), a regression model treats December (12) and January (1) as 11 units apart, despite being consecutive winter months with identical inversion conditions. By mapping months to angles on a trigonometric unit circle [sin(2*pi*m/12), cos(2*pi*m/12)], December and January remain continuous and mathematically adjacent.\"</i>", "AnsX"),

    P("Q7: How does the backend derive lag features if the user only provides a city name?", "QuesX"),
    P("<b>Winning Answer:</b> <i>\"The frontend sends a simple payload: {'city': 'Delhi'}. The FastAPI backend queries the historical dataframe, isolates the latest 7 chronological observations for Delhi, extracts [aqi_today, aqi_lag_1 ... aqi_lag_7], computes rolling statistics (mean, std), and injects current date harmonics before invoking model.predict(). This abstracts technical complexity away from the user interface.\"</i>", "AnsX"),

    P("Q8: How did you solve production deployment and browser caching issues?", "QuesX"),
    P("<b>Winning Answer:</b> <i>\"We decoupled the architecture: Render hosts the FastAPI web service with a permissive regex CORS policy (https://.*\\.vercel\\.app), and Vercel hosts the Vite frontend. To prevent aggressive browser disk caching of old JavaScript bundles, we configured vercel.json with Cache-Control: 'no-cache, no-store, must-revalidate' for index.html, ensuring every client instantaneously loads updated code.\"</i>", "AnsX")
]

story += [PageBreak()]

# --- SECTION 5: RECOMMENDED PRESENTATION FLOW ---
story += [
    P("6. Recommended 5-Minute Presentation Sequence", "H1X"),
    P("Follow this exact step-by-step structure during your slide presentation and live demonstration:"),
    Spacer(1, 4)
]

flow_table = [
    ["Slide / Step", "Time", "What to Display", "Key Talking Points to Emphasize"],
    ["1. Title & Problem", "0:00 - 0:45", "Cover Slide & Architecture", "Introduce 'Can Delhi Teach Surat?'. Explain the sensor gap in tier-2 cities."],
    ["2. Data & Validation", "0:45 - 1:30", "Pipeline & Cleaning Steps", "235k rows, 291 cities. Strict chronological split (Train < 2025, Test == 2025). No leakage."],
    ["3. Model Comparison", "1:30 - 2:15", "Metrics Comparison Table", "XGBoost beat Persistence by ~3 RMSE points. Explain why Ridge and Random Forest lost."],
    ["4. Live System Demo", "2:15 - 3:45", "Live URL: aqi-etdki.vercel.app", "Select Delhi, show auto-filled 7 lags, show live US AQI card, click 'Estimate Next Day'."],
    ["5. City Transfer Matrix", "3:45 - 4:30", "/transfer Tab on Live UI", "Explain diagonal vs off-diagonal RMSE. Prove that the model transfers without city labels."],
    ["6. Conclusion & Viva", "4:30 - 5:00", "/explain & Q&A Slide", "Highlight feature importance (recency + rolling), acknowledge CPCB vs US AQI, open for Q&A."]
]
story += [make_table(flow_table, widths=[90, 60, 135, 230]), Spacer(1, 10)]

story += [
    P("Final Presentation Tip:", "H2X"),
    P("<i>Keep the live website open in one browser tab (<b>https://aqi-etdki.vercel.app/</b>) and your PDF guide in another. When asked about code or architecture, you can seamlessly switch between the live interactive demo and the exact mathematical formulas.</i>", "Callout")
]

def add_header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#65736f"))
    # Header
    canvas.drawString(40, A4[1] - 25, "Can Delhi Teach Surat? | AQI Research Lab — Presentation & Viva Guide")
    canvas.drawRightString(A4[0] - 40, A4[1] - 25, "Live: aqi-etdki.vercel.app")
    canvas.setStrokeColor(colors.HexColor("#d5deda"))
    canvas.setLineWidth(0.5)
    canvas.line(40, A4[1] - 30, A4[0] - 40, A4[1] - 30)
    # Footer
    canvas.line(40, 36, A4[0] - 40, 36)
    canvas.drawString(40, 22, "Confidential Viva Preparation Document · AI/ML Engineering Prototype")
    canvas.drawRightString(A4[0] - 40, 22, f"Page {doc.page}")
    canvas.restoreState()

doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
print("SUCCESS: Cleanly generated " + OUTPUT)
