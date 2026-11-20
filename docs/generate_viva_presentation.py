from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from pptx import Presentation
from pptx.chart.data import ChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "AQI_Project_Viva_Presentation.pptx"

NAVY = RGBColor(10, 23, 48)
NAVY2 = RGBColor(16, 38, 72)
BLUE = RGBColor(65, 146, 255)
CYAN = RGBColor(72, 201, 229)
WHITE = RGBColor(245, 248, 252)
MUTED = RGBColor(178, 194, 216)
CORAL = RGBColor(239, 139, 111)
GREEN = RGBColor(93, 202, 156)
LIGHT = RGBColor(225, 235, 246)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)


def rect(slide, x, y, w, h, fill, radius=True, line=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
                                   Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line or fill
    return shape


def text(slide, x, y, w, h, value, size=18, color=WHITE, bold=False,
         align=PP_ALIGN.LEFT, font="Aptos", valign=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.margin_left = 0
    frame.margin_right = 0
    frame.margin_top = 0
    frame.margin_bottom = 0
    frame.vertical_anchor = valign
    p = frame.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = value
    r.font.name = font
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    return box


def title(slide, kicker, heading, slide_no):
    text(slide, 0.65, 0.38, 8.8, 0.28, kicker.upper(), 9, CYAN, True)
    text(slide, 0.65, 0.72, 11.9, 0.62, heading, 27, WHITE, True)
    rect(slide, 0.65, 1.38, 11.95, 0.018, BLUE, radius=False)
    text(slide, 12.35, 0.38, 0.35, 0.25, f"{slide_no:02d}", 8, MUTED, True, PP_ALIGN.RIGHT)


def base_slide(kicker, heading, slide_no):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = NAVY
    rect(slide, 12.55, 0, 0.78, 7.5, NAVY2, radius=False)
    title(slide, kicker, heading, slide_no)
    return slide


def bullet_list(slide, items, x=0.75, y=1.72, w=5.8, h=4.9,
                size=15, accent=BLUE, gap=0.12):
    yy = y
    for item in items:
        rect(slide, x, yy + 0.11, 0.09, 0.09, accent, radius=True)
        text(slide, x + 0.22, yy, w - 0.22, 0.62, item, size, WHITE, False)
        yy += h / max(len(items), 1) + gap


def metric_card(slide, x, y, w, h, label, value, note, accent=BLUE):
    rect(slide, x, y, w, h, NAVY2, True)
    rect(slide, x, y, w, 0.06, accent, False)
    text(slide, x + 0.18, y + 0.18, w - 0.36, 0.28, label.upper(), 8, MUTED, True)
    text(slide, x + 0.18, y + 0.58, w - 0.36, 0.55, value, 24, WHITE, True)
    text(slide, x + 0.18, y + 1.15, w - 0.36, h - 1.28, note, 9, MUTED)


# 1 — title
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid()
slide.background.fill.fore_color.rgb = NAVY
rect(slide, 8.9, 0, 4.433, 7.5, NAVY2, radius=False)
rect(slide, 9.35, 1.05, 3.25, 0.06, CYAN, radius=False)
text(slide, 0.75, 0.62, 7.6, 0.30, "MAJOR AI / ML PROJECT", 10, CYAN, True)
text(slide, 0.75, 1.28, 7.7, 1.55, "Next-Day AQI\nForecasting Dashboard", 34, WHITE, True)
text(slide, 0.75, 3.10, 7.2, 0.42, "Data cleaning • Model training • API • React dashboard", 15, MUTED)
rect(slide, 0.75, 4.15, 6.8, 1.30, NAVY2, True)
text(slide, 1.02, 4.42, 2.3, 0.25, "PROJECT TEAM", 9, CYAN, True)
text(slide, 1.02, 4.78, 5.8, 0.42, "Aditya Raj  •  Pratik Ranjan  •  Nilendu Das", 16, WHITE, True)
text(slide, 9.42, 1.55, 2.8, 0.25, "PROJECT SNAPSHOT", 9, CYAN, True)
metric_card(slide, 9.42, 2.05, 2.8, 1.40, "Raw rows", "235005", "Daily city observations", BLUE)
metric_card(slide, 9.42, 3.67, 2.8, 1.40, "Cities", "291", "Indian cities in dataset", CYAN)
metric_card(slide, 9.42, 5.29, 2.8, 1.40, "Test year", "2025", "Chronological holdout", CORAL)

# 2 — contents
slide = base_slide("Presentation map", "Project overview", 2)
items = ["Problem and objective", "Dataset and cleaning", "Feature engineering", "Train/test strategy", "Model comparison", "XGBoost selection", "City Transfer", "System architecture", "Deployment and final results"]
bullet_list(slide, items, y=1.58, h=5.15, w=11.6, size=15)

# 3 — problem
slide = base_slide("01", "Why next-day AQI forecasting?", 3)
metric_card(slide, 0.75, 1.75, 3.55, 2.15, "Problem", "A delayed signal", "AQI is a time-dependent measure affected by recent pollution patterns.", CORAL)
metric_card(slide, 4.88, 1.75, 3.55, 2.15, "Goal", "Predict t+1", "Estimate tomorrow's AQI from information available today.", BLUE)
metric_card(slide, 9.01, 1.75, 3.55, 2.15, "Deliverable", "One system", "Cleaned data → model → API → dashboard.", GREEN)
text(slide, 0.75, 4.55, 11.8, 0.75, "Core question: can recent AQI history and time patterns forecast the next day's AQI?", 20, WHITE, True, PP_ALIGN.CENTER)

# 4 — objectives
slide = base_slide("02", "Project objectives", 4)
objectives = [
    ("01", "Clean", "Normalize real-world AQI CSV variations"),
    ("02", "Engineer", "Create lags, rolling trends, and calendar features"),
    ("03", "Train", "Compare four model approaches"),
    ("04", "Evaluate", "Use chronological 2025 holdout data"),
    ("05", "Deploy", "Expose inference through FastAPI and Vercel"),
]
for i, (num, head, body) in enumerate(objectives):
    y = 1.60 + i * 1.02
    rect(slide, 0.78, y, 11.7, 0.78, NAVY2, True)
    text(slide, 1.02, y + 0.16, 0.55, 0.32, num, 12, CYAN, True)
    text(slide, 1.68, y + 0.12, 1.55, 0.36, head, 16, WHITE, True)
    text(slide, 3.15, y + 0.16, 8.8, 0.32, body, 12, MUTED)

# 5 — dataset
slide = base_slide("03", "Dataset overview", 5)
metric_card(slide, 0.75, 1.72, 2.75, 1.55, "Raw rows", "235005", "City-day records", BLUE)
metric_card(slide, 3.75, 1.72, 2.75, 1.55, "Cities", "291", "Indian locations", CYAN)
metric_card(slide, 6.75, 1.72, 2.75, 1.55, "Feature rows", "238874", "Next-day labeled samples", GREEN)
metric_card(slide, 9.75, 1.72, 2.75, 1.55, "Date range", "2022–2025", "April 2022 to April 2025", CORAL)
text(slide, 0.75, 3.65, 11.7, 0.30, "MAIN RAW COLUMNS", 9, CYAN, True)
bullet_list(slide, ["date — observation date", "city — location name", "aqi — numerical target", "state — city/state metadata", "prominent_pollutants — pollutant text", "monitoring_stations — station count"], x=0.78, y=4.10, w=11.6, h=0.48, size=12)

# 6 — cleaning
slide = base_slide("04", "Data cleaning pipeline", 6)
steps = [
    ("1", "Find CSV", "Verify city, date and AQI columns"),
    ("2", "Normalize", "Map aliases to city, date and AQI"),
    ("3", "Convert", "Parse dates and numeric values"),
    ("4", "Clean", "Trim city names and reject invalid rows"),
    ("5", "Deduplicate", "Keep one last row per city-date"),
]
for i,(num,head,body) in enumerate(steps):
    x = 0.65 + i*2.46
    rect(slide,x,1.86,2.16,3.25,NAVY2,True)
    rect(slide,x,1.86,2.16,0.08,BLUE,False)
    text(slide,x+0.18,2.14,1.7,0.36,num,24,CYAN,True)
    text(slide,x+0.18,2.75,1.75,0.36,head,16,WHITE,True)
    text(slide,x+0.18,3.35,1.78,1.20,body,11,MUTED)
text(slide,0.75,5.55,11.7,0.75,"Invalid city/date rows are removed. Missing numeric values are converted with errors='coerce' and later median-imputed by the model pipeline.",12,MUTED,False,PP_ALIGN.CENTER)

# 7 — feature engineering
slide = base_slide("05", "Feature engineering", 7)
feature_groups = [
    ("Current AQI", ["aqi_today"], BLUE),
    ("Lags", ["lag 1", "lag 2", "lag 3", "lag 7"], CYAN),
    ("Trend", ["3-day mean", "7-day mean"], GREEN),
    ("Volatility", ["3-day std", "7-day std"], CORAL),
    ("Time", ["month sin/cos", "weekday sin/cos"], BLUE),
]
for i,(head,vals,accent) in enumerate(feature_groups):
    x=0.68+i*2.43
    rect(slide,x,1.80,2.18,2.55,NAVY2,True)
    rect(slide,x,1.80,2.18,0.07,accent,False)
    text(slide,x+0.18,2.10,1.82,0.32,head,14,WHITE,True)
    yy=2.72
    for v in vals:
        text(slide,x+0.18,yy,1.82,0.38,v,11,MUTED)
        yy+=0.48
text(slide,0.75,4.75,11.7,0.38,"TARGET",9,CYAN,True,PP_ALIGN.CENTER)
text(slide,0.75,5.15,11.7,0.62,"AQI(t+1)",28,WHITE,True,PP_ALIGN.CENTER)
text(slide,0.75,6.05,11.7,0.40,"Strict rule: no future AQI value is included in X(t)",12,MUTED,False,PP_ALIGN.CENTER)

# 8 — split
slide = base_slide("06", "Chronological train/test split", 8)
rect(slide,0.75,2.05,11.8,1.15,NAVY2,True)
rect(slide,0.75,2.05,7.9,1.15,RGBColor(37,91,148),True)
text(slide,1.05,2.32,7.3,0.30,"Training: target date before 2025",16,WHITE,True)
text(slide,8.85,2.32,3.35,0.30,"Testing: 2025",16,WHITE,True,PP_ALIGN.CENTER)
metric_card(slide,0.75,3.72,3.55,1.65,"Training", "210725", "Rows used to fit the models", BLUE)
metric_card(slide,4.88,3.72,3.55,1.65,"Testing", "28149", "Held-out 2025 observations", CYAN)
metric_card(slide,9.01,3.72,3.55,1.65,"No shuffling", "Time-safe", "No future leakage", GREEN)
text(slide,0.75,5.85,11.8,0.55,"Random train-test splitting is not used because it could mix future patterns into training.",13,MUTED,False,PP_ALIGN.CENTER)

# 9 — models
slide = base_slide("07", "Models compared", 9)
models = [
    ("Persistence", "Tomorrow = today", "Naive baseline", MUTED),
    ("Ridge", "Linear + L2 penalty", "Fast baseline learner", BLUE),
    ("Random Forest", "300 decision trees", "Non-linear ensemble", CYAN),
    ("XGBoost", "400 boosted trees", "Final selected model", GREEN),
]
for i,(name,what,detail,accent) in enumerate(models):
    y=1.62+i*1.18
    rect(slide,0.75,y,11.8,0.92,NAVY2,True)
    rect(slide,0.75,y,0.11,0.92,accent,False)
    text(slide,1.05,y+0.18,2.15,0.32,name,15,WHITE,True)
    text(slide,3.32,y+0.18,3.15,0.32,what,12,MUTED)
    text(slide,7.00,y+0.18,5.15,0.32,detail,12,accent,True)

# 10 — metrics chart
slide = base_slide("08", "Held-out 2025 model comparison", 10)
metrics = pd.DataFrame([
    ["XGBoost",20.2201,29.8203,.7107,.7397],
    ["Ridge",20.3459,29.9308,.7086,.7314],
    ["Random Forest",20.5513,30.1208,.7049,.7311],
    ["Persistence",21.1964,32.5878,.6546,.7319]
], columns=["Model","MAE","RMSE","R2","CategoryAcc"])
chart_data = ChartData()
chart_data.categories = metrics["Model"].tolist()
chart_data.add_series("RMSE", metrics["RMSE"].tolist())
chart = slide.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(0.72), Inches(1.64), Inches(7.0), Inches(4.75), chart_data).chart
chart.has_legend=False
chart.chart_title.text_frame.text="RMSE — lower is better"
chart.chart_title.text_frame.paragraphs[0].runs[0].font.color.rgb=WHITE
chart.value_axis.has_major_gridlines=True
chart.category_axis.reverse_order=True
text(slide,8.15,1.72,4.15,0.30,"FINAL METRIC TABLE",9,CYAN,True)
rows=[["Model","MAE","RMSE","R²"],["XGBoost","20.22","29.82","0.7107"],["Ridge","20.35","29.93","0.7086"],["Random Forest","20.55","30.12","0.7049"],["Persistence","21.20","32.59","0.6546"]]
shape=slide.shapes.add_table(5,4,Inches(8.15),Inches(2.12),Inches(4.15),Inches(2.75))
table_obj=shape.table
for c,label in enumerate(["Model","MAE","RMSE","R²"]):
    table_obj.cell(0,c).text=label
for r,row in enumerate(rows[1:],1):
    for c,val in enumerate(row): table_obj.cell(r,c).text=val
for r in range(5):
    for c in range(4):
        cell=table_obj.cell(r,c)
        cell.fill.solid(); cell.fill.fore_color.rgb=NAVY2 if r else RGBColor(30,94,89)
        for p in cell.text_frame.paragraphs:
            for run in p.runs:
                run.font.name="Aptos"; run.font.size=Pt(9); run.font.bold=(r==0); run.font.color.rgb=WHITE

# 11 — selection
slide = base_slide("09", "How XGBoost was selected", 11)
steps=["1. Train all candidates","2. Predict 2025 test rows","3. Calculate MAE and RMSE","4. Exclude Persistence","5. Choose lowest RMSE","6. Save joblib model"]
for i,s in enumerate(steps):
    x=0.75+i*2.02
    rect(slide,x,2.15,1.72,1.35,NAVY2,True)
    text(slide,x+0.14,2.43,1.44,0.62,s,11,WHITE,True,PP_ALIGN.CENTER)
text(slide,0.75,4.05,11.7,0.46,"Selected model",9,CYAN,True,PP_ALIGN.CENTER)
text(slide,0.75,4.52,11.7,0.68,"XGBoost",30,WHITE,True,PP_ALIGN.CENTER)
text(slide,0.75,5.52,11.7,0.55,"RMSE 29.82  |  MAE 20.22  |  R² 0.7107",16,GREEN,True,PP_ALIGN.CENTER)

# 12 — XGBoost details
slide = base_slide("10", "Why XGBoost is used", 12)
metric_card(slide,0.75,1.70,3.55,2.05,"Ensemble","400 trees","Sequential correction of previous errors",GREEN)
metric_card(slide,4.88,1.70,3.55,2.05,"Depth","5 levels","Limits individual tree complexity",BLUE)
metric_card(slide,9.01,1.70,3.55,2.05,"Learning","0.04","Small correction rate for stable fitting",CYAN)
text(slide,0.75,4.35,11.8,0.30,"VIVA DEFINITION",9,CYAN,True)
text(slide,0.75,4.78,11.8,1.18,"XGBoost means Extreme Gradient Boosting. It builds many decision trees sequentially and adds trees that reduce the residual prediction error left by earlier trees.",15,WHITE,True,PP_ALIGN.CENTER)

# 13 — metrics
slide = base_slide("11", "Metric interpretation", 13)
metric_cards=[("MAE","20.22","Average absolute AQI error","20.22 points on the test year"),("RMSE","29.82","Larger errors receive more weight","Better than the 32.59 baseline"),("R²","0.7107","Variance explained","About 71.1% of target variance"),("Category accuracy","73.97%","Band matching accuracy","AQI category agreement")]
for i,(lab,val,head,note) in enumerate(metric_cards):
    x=0.68+(i%2)*6.05
    y=1.72+(i//2)*2.20
    metric_card(slide,x,y,5.75,1.85,lab,val,head+" — "+note,[BLUE,CYAN,GREEN,CORAL][i])

# 14 — final code
slide = base_slide("12", "Saved model and final inference", 14)
text(slide,0.75,1.65,11.7,0.30,"TRAINING OUTPUT",9,CYAN,True)
rect(slide,0.75,2.02,11.7,0.86,NAVY2,True)
text(slide,1.02,2.25,11.0,0.32,"models/best_model.joblib  +  models/metadata.json",16,WHITE,True)
text(slide,0.75,3.25,11.7,0.30,"INFERENCE FLOW",9,CYAN,True)
flow=["Select city","Load 7 AQI values","Create lag features","Load XGBoost artifact","Predict AQI","Assign category"]
for i,s in enumerate(flow):
    x=0.72+i*2.02
    rect(slide,x,3.72,1.72,1.05,NAVY2,True)
    text(slide,x+0.12,4.02,1.48,0.45,s,10,WHITE,True,PP_ALIGN.CENTER)
    if i<5: text(slide,x+1.76,4.06,0.20,0.30,"→",14,CYAN,True,PP_ALIGN.CENTER)

# 15 — city transfer
slide = base_slide("13", "City Transfer experiment", 15)
text(slide,0.75,1.62,11.8,0.38,"Question: how useful is a model trained in city A when tested in city B?",14,WHITE,True,PP_ALIGN.CENTER)
metric_card(slide,0.75,2.34,3.55,1.85,"Rows","Training city","Which city supplies the training observations",BLUE)
metric_card(slide,4.88,2.34,3.55,1.85,"Columns","Testing city","Which city supplies held-out 2025 observations",CYAN)
metric_card(slide,9.01,2.34,3.55,1.85,"Value","RMSE","Lower value means better prediction",GREEN)
text(slide,0.75,4.72,11.8,0.62,"Diagonal: same-city reference  |  Off-diagonal: cross-city transfer",14,MUTED,True,PP_ALIGN.CENTER)
text(slide,0.75,5.55,11.8,0.50,"The deployed matrix is precomputed as 8 cities × 8 cities = 64 values.",12,CORAL,True,PP_ALIGN.CENTER)

# 16 — architecture
slide = base_slide("14", "Complete system architecture", 16)
boxes=[("Dataset","CSV + city data"),("ML pipeline","Clean + features"),("Model","XGBoost joblib"),("API","FastAPI endpoints"),("Frontend","React dashboard")]
for i,(head,body) in enumerate(boxes):
    x=0.60+i*2.50
    rect(slide,x,2.55,2.05,1.35,NAVY2,True)
    text(slide,x+0.14,2.82,1.77,0.30,head,14,WHITE,True,PP_ALIGN.CENTER)
    text(slide,x+0.14,3.33,1.77,0.28,body,9,MUTED,False,PP_ALIGN.CENTER)
    if i<4:text(slide,x+2.06,2.95,0.34,0.30,"→",16,CYAN,True,PP_ALIGN.CENTER)
text(slide,0.75,4.62,11.8,0.70,"CSV → pandas → feature table → scikit-learn/XGBoost → joblib artifact → FastAPI JSON → React UI",14,WHITE,True,PP_ALIGN.CENTER)

# 17 — deployment
slide = base_slide("15", "Deployment", 17)
metric_card(slide,0.75,1.75,5.25,2.20,"Backend","Render","FastAPI, Uvicorn, model artifact, CORS",BLUE)
metric_card(slide,7.33,1.75,5.25,2.20,"Frontend","Vercel","React, Vite, VITE_API_URL, static build",CYAN)
text(slide,0.75,4.45,11.8,0.35,"API FLOW",9,CORAL,True,PP_ALIGN.CENTER)
text(slide,0.75,4.88,11.8,0.65,"Browser → Vercel frontend → Render API → XGBoost model → JSON response",16,WHITE,True,PP_ALIGN.CENTER)
text(slide,0.75,5.78,11.8,0.42,"Free-tier Render may spin down after inactivity.",11,MUTED,False,PP_ALIGN.CENTER)

# 18 — final results
slide = base_slide("16", "Final results and limitations", 18)
metric_card(slide,0.75,1.72,3.55,1.75,"Best model","XGBoost","Lowest holdout RMSE",GREEN)
metric_card(slide,4.88,1.72,3.55,1.75,"Numeric error","29.82 RMSE","20.22 average absolute error",BLUE)
metric_card(slide,9.01,1.72,3.55,1.75,"Category","73.97%","Accuracy on AQI bands",CYAN)
text(slide,0.75,4.05,11.8,0.28,"LIMITATIONS",9,CORAL,True)
bullet_list(slide,["The active raw data ends in April 2025, not a live source","Optional pollutant/weather fields may be sparse","One estimate is not guaranteed to be exact","Free Render hosting can spin down after inactivity"],x=0.75,y=4.45,w=11.8,h=0.48,size=12)

# 19 — viva
slide = base_slide("17", "Top viva questions", 19)
qa=[("Target?","AQI(t+1)"),("Split?","Chronological, 2025 held out"),("Models?","Persistence, Ridge, Random Forest, XGBoost"),("Best?","XGBoost, RMSE 29.82"),("Why lags?","Recent AQI helps next-day prediction"),("Why no random split?","Avoid future leakage"),("City transfer?","Train in source city, test in another")]
for i,(q,a) in enumerate(qa):
    col=i%2; row=i//2
    x=0.75+col*6.05; y=1.60+row*1.25
    rect(slide,x,y,5.75,0.98,NAVY2,True)
    text(slide,x+0.18,y+0.14,1.45,0.26,q,10,CYAN,True)
    text(slide,x+1.55,y+0.14,3.95,0.48,a,12,WHITE,True)

# 20 — conclusion
slide = base_slide("18", "Conclusion", 20)
text(slide,0.75,1.75,11.8,0.76,"A complete ML project, from raw AQI data to a deployed application.",24,WHITE,True,PP_ALIGN.CENTER)
metric_card(slide,0.75,3.05,3.55,1.75,"Pipeline","Verified","Cleaning → features → split",BLUE)
metric_card(slide,4.88,3.05,3.55,1.75,"Model","XGBoost","Lowest holdout RMSE",GREEN)
metric_card(slide,9.01,3.05,3.55,1.75,"System","Full-stack","FastAPI + React + Render + Vercel",CYAN)
text(slide,0.75,5.45,11.8,0.55,"Thank you",24,WHITE,True,PP_ALIGN.CENTER)
text(slide,0.75,6.15,11.8,0.35,"Aditya Raj  •  Pratik Ranjan  •  Nilendu Das",12,MUTED,True,PP_ALIGN.CENTER)

# footer and slide numbering already handled
prs.save(str(OUT))
print(OUT)
