# PlaceIQ — AI Placement Intelligence System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.3.3-000000?style=for-the-badge&logo=flask&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3.0-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.1.0-150458?style=for-the-badge&logo=pandas&logoColor=white)

**An end-to-end machine learning web application that predicts student placement probability, explains predictions with SHAP, generates AI recommendations, and visualizes insights through an interactive dashboard.**

[Features](#-features) • [Screenshots](#-screenshots) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture) • [API Reference](#-api-reference)

</div>

---

## 📌 Overview

PlaceIQ is a full-stack AI platform built for Indian engineering colleges. It ingests student academic and extracurricular data, trains four ML models in parallel, selects the best performer, and serves real-time predictions through a clean web interface. Every prediction is accompanied by SHAP-based feature attribution, a quantified risk score, and personalized career recommendations.

### Why PlaceIQ?

| Challenge | What PlaceIQ Does |
|---|---|
| TPOs need to identify at-risk students early | Produces a **Risk Score (0–100)** per student |
| Placement decisions are opaque | **SHAP explainability** shows exactly which factors help/hurt |
| Generic advice doesn't work | **AI recommendations** are tailored to each student's profile |
| Manual data analysis is slow | **Auto-generated EDA insights** from raw dataset on startup |
| Different colleges have different data | **CSV upload** triggers full pipeline retraining on custom data |

---

## ✨ Features

### Core ML Capabilities
- **Multi-Model Training** — Trains four classifiers simultaneously and selects the best by F1 score
  - Logistic Regression
  - Random Forest (100 estimators)
  - Gradient Boosting (100 estimators)
  - SVM with RBF kernel
- **Feature Engineering** — Derives composite scores from raw columns:
  - `Academic_Score` (CGPA 50%, SSC 25%, HSC 25%)
  - `Experience_Score` (Internships 40%, Projects 30%, Workshops 30%)
  - `Skill_Score` (Aptitude 50%, Soft Skills 30%, Activities 20%)
  - `Overall_Score` (Academic 40%, Experience 35%, Skill 25%)
  - Binary flags: `Has_Backlog`, `High_CGPA`
- **SHAP Explainability** — Approximated SHAP values visualized as an interactive bar chart per prediction
- **Risk Score** — A 0–100 composite risk metric computed from probability + profile penalties

### Web Application Pages
| Page | Route | Description |
|---|---|---|
| 🏠 Home | `/` | Hero section, live dataset stats, feature overview |
| ◈ Predict | `/predict` | Student profile form → AI analysis |
| 📊 Result | `/result` | Probability ring, risk gauge, SHAP bars, recommendations |
| ⊞ Dashboard | `/dashboard` | EDA graphs, feature importance, model comparison table |
| ⟡ Analytics | `/analytics` | Prediction history charts, radar chart, model stats |
| ⊙ History | `/history` | Searchable/filterable table of all past predictions |
| ⤒ Upload | `/upload` | Drag-and-drop CSV uploader that triggers full retraining |

### Data & Pipeline
- **Auto dataset**: Falls back to a realistic synthetic dataset (600 rows) if Kaggle unavailable
- **Kaggle integration**: Automatically downloads `vishardmehta/indian-engineering-college-placement-dataset`
- **Smart column detection**: Auto-maps fuzzy column names (e.g., "GPA", "Intern", "Aptitude")
- **Persistent SQLite DB**: All predictions stored with full metadata; exportable to CSV

---

## 📂 Project Structure

```
ai_placement_system/
├── run.py                  # Entry point — init DB + pipeline + Flask server
├── app.py                  # Flask routes and REST API endpoints
├── requirements.txt        # Python dependencies
│
├── utils/
│   ├── data_pipeline.py    # Dataset loading, feature engineering, normalization
│   ├── eda.py              # Matplotlib/Seaborn graph generation (11 charts)
│   └── predictor.py        # SHAP approximation, recommendations, risk scoring
│
├── model/
│   ├── train.py            # 4-model trainer with metrics and graph generation
│   ├── best_model.pkl      # Serialized best model (auto-selected by F1)
│   ├── scaler.pkl          # StandardScaler fitted on training data
│   ├── feature_cols.pkl    # Ordered list of 19 feature columns
│   ├── feature_importance.json
│   ├── gradient_boosting.pkl
│   ├── logistic_regression.pkl
│   ├── random_forest.pkl
│   └── svm.pkl
│
├── database/
│   ├── db.py               # SQLite helpers (init, save, query predictions)
│   └── placement.db        # Auto-created SQLite database
│
├── data/
│   ├── placement_data.csv  # Training/loaded dataset
│   └── stats.json          # Pre-computed dataset statistics
│
├── evaluation/
│   └── metrics.json        # Accuracy, Precision, Recall, F1, AUC for all models
│
├── static/
│   └── graphs/             # All EDA and model evaluation PNGs (auto-generated)
│
└── templates/
    ├── base.html           # Shared layout, sidebar, navigation, toast
    ├── index.html          # Home page
    ├── predict.html        # Input form
    ├── result.html         # Prediction result with charts
    ├── dashboard.html      # EDA dashboard
    ├── analytics.html      # Admin analytics
    ├── history.html        # Prediction history table
    └── upload.html         # CSV upload interface
```

---

## 🛠 Installation

### Prerequisites

- Python **3.9** or higher
- `pip` package manager
- (Optional) Kaggle account for real dataset — see [Kaggle Setup](#kaggle-setup)

### Step-by-Step Setup

**1. Clone / download the project**
```bash
cd ai_placement_system
```

**2. Create and activate a virtual environment** *(recommended)*
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the application**
```bash
python run.py
```

The startup process will:
1. Create required directories (`data/`, `model/`, `evaluation/`, `static/graphs/`, `database/`)
2. Initialize the SQLite database
3. Load/generate the dataset and run the full ML pipeline (~30–60 s on first run)
4. Launch the Flask server at **http://localhost:5050**

> **Subsequent runs** are much faster — the trained model and dataset are cached on disk.

### Kaggle Setup *(Optional)*

To use the real Indian engineering college dataset:

1. Install the Kaggle CLI: `pip install kaggle`
2. Place your `kaggle.json` API key in `~/.kaggle/kaggle.json`
3. The app will automatically download the dataset on first run

If Kaggle credentials are not configured, a realistic **600-record synthetic dataset** is generated automatically.

---

## 🚀 Usage

### Making a Prediction

1. Navigate to [http://localhost:5050/predict](http://localhost:5050/predict)
2. Fill in the student profile:
   - **Academic**: CGPA, SSC %, HSC %, Backlogs
   - **Experience**: Internships, Projects, Workshops/Certifications
   - **Skills**: Aptitude Score, Soft Skills Rating
   - **General**: Stream, Gender, Extracurriculars, Training
3. Click **◈ Analyze Placement Probability**
4. View the **Result page** with:
   - Probability ring chart (0–100%)
   - Risk gauge (0–100)
   - SHAP feature contribution bars
   - AI-powered recommendations with priority levels

### Uploading a Custom Dataset

1. Navigate to [http://localhost:5050/upload](http://localhost:5050/upload)
2. Drag & drop or browse for your CSV file (max 16 MB)
3. The pipeline auto-retrains all 4 models on your data
4. Dashboard and analytics update automatically

**Minimum required columns** (names are auto-detected):

| Column | Description |
|---|---|
| `CGPA` | Cumulative GPA (0–10) |
| `PlacementStatus` | Target label: `0/1` or `Placed/Not Placed` |
| `Internships` | Number of internships completed |
| `AptitudeTestScore` | Score out of 100 |

**Optional columns** (filled with defaults if absent):
`SSC_Marks`, `HSC_Marks`, `Projects`, `Workshops_Certifications`, `SoftSkillsRating`, `ExtracurricularActivities`, `PlacementTraining`, `Backlogs`, `Stream`, `Gender`

### Exporting Data

- All predictions can be exported as CSV from **History → Export CSV** or at `GET /export/predictions`

---

## 🧠 ML Pipeline Details

### Feature Engineering (19 Features)

```
Raw inputs:    CGPA, SSC_Marks, HSC_Marks, Internships, Projects,
               Workshops, AptitudeTestScore, SoftSkillsRating,
               Backlogs, Stream, Gender, ExtracurricularActivities,
               PlacementTraining

Derived:       Academic_Score    = CGPA×0.5 + SSC×0.25 + HSC×0.25
               Experience_Score  = Intern×0.4 + Projects×0.3 + Workshop×0.3
               Skill_Score       = Aptitude×0.5 + SoftSkills×0.3 + Activities×0.2
               Overall_Score     = Academic×0.4 + Experience×0.35 + Skill×0.25
               Has_Backlog       = (Backlogs > 0) as 0/1
               High_CGPA         = (CGPA ≥ 8.0) as 0/1
```

### Model Selection

All four classifiers are trained on a **80/20 train-test split** (stratified). The model with the highest **F1 score** on the test set is selected as the best model and saved as `best_model.pkl`.

### Risk Score Formula

The risk score (0–100) combines placement probability with profile penalties:
```
risk = (1 - probability) × 70  +  backlog_penalty + cgpa_penalty + aptitude_penalty
```
Where penalties are added for CGPA < 6.5, backlogs > 0, and aptitude score < 50.

### Recommendation Engine

Recommendations are generated with priority levels (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`) based on specific profile thresholds (e.g., CGPA < 6.5 → CRITICAL, no internships → HIGH).

---

## 📊 EDA Graphs Generated

The following graphs are automatically generated on startup and shown in the Dashboard:

| Graph | Description |
|---|---|
| `cgpa_placement.png` | CGPA distribution by placement status |
| `internships_placement.png` | Internship count vs placement |
| `skills_placement.png` | Aptitude score distribution |
| `projects_placement.png` | Projects count vs placement |
| `placement_distribution.png` | Overall placed vs not-placed pie |
| `heatmap.png` | Feature correlation heatmap |
| `stream_placement.png` | Placement rate by engineering stream |
| `feature_importance.png` | Top feature importances bar chart |
| `roc_curve.png` | ROC curve for the best model |
| `confusion_matrix.png` | Confusion matrix heatmap |
| `model_comparison.png` | Side-by-side model performance bars |
| `shap_plot.png` | Per-prediction SHAP bar (generated live) |

---

## 🔌 API Reference

All endpoints return JSON unless stated otherwise.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Home page |
| `GET` | `/predict` | Prediction form |
| `POST` | `/predict` | Submit prediction (JSON body) |
| `GET` | `/result` | Prediction result page |
| `GET` | `/dashboard` | Dashboard page |
| `GET` | `/analytics` | Analytics page |
| `GET` | `/history` | History page |
| `GET/POST` | `/upload` | Upload CSV |
| `GET` | `/api/status` | `{"ready": bool, "model_trained": bool}` |
| `GET` | `/api/history` | All predictions as JSON array |
| `GET` | `/api/analytics` | Aggregate analytics stats |
| `GET` | `/api/insights` | Auto-generated dataset insights |
| `GET` | `/metrics` | Model performance metrics |
| `GET` | `/export/predictions` | Download predictions as CSV |

### POST `/predict` — Example Request

```json
{
  "student_name": "Arjun Sharma",
  "cgpa": "8.2",
  "internships": "2",
  "projects": "3",
  "workshops": "2",
  "aptitude_score": "78",
  "ssc_marks": "85",
  "hsc_marks": "80",
  "backlogs": "0",
  "soft_skills": "4.0",
  "stream_encoded": "0",
  "gender_encoded": "0",
  "extracurricular": "Yes",
  "placement_training": "Yes"
}
```

### POST `/predict` — Example Response

```json
{
  "student_name": "Arjun Sharma",
  "probability": 87.43,
  "prediction": "Placed",
  "risk_score": 18,
  "category": "High Chance",
  "category_color": "#34d399",
  "category_icon": "🏆",
  "model_used": "Gradient Boosting",
  "recommendations": [...],
  "feature_importance": {
    "CGPA": 0.2341,
    "AptitudeTestScore": 0.1823,
    ...
  },
  "top_positive": ["CGPA", "AptitudeTestScore", "Overall_Score"],
  "top_negative": []
}
```

---

## 📦 Dependencies

```txt
flask==2.3.3          # Web framework
pandas==2.1.0         # Data manipulation
numpy==1.24.3         # Numerical computing
scikit-learn==1.3.0   # ML models and preprocessing
matplotlib==3.7.2     # Graph generation
seaborn==0.12.2       # Statistical visualizations
shap==0.42.1          # SHAP explainability
kagglehub==0.2.5      # Kaggle dataset download
joblib==1.3.2         # Model serialization
Werkzeug==2.3.7       # WSGI utilities
```

---

## ⚙️ Configuration

| Parameter | Default | Where |
|---|---|---|
| Server port | `5050` | `run.py` line 46 |
| Max upload size | `16 MB` | `app.py` — `MAX_CONTENT_LENGTH` |
| Synthetic dataset size | `600 rows` | `data_pipeline.py` — `generate_synthetic_dataset(n=600)` |
| Train/test split | `80% / 20%` | `model/train.py` — `test_size=0.2` |
| Model selection metric | F1 Score | `model/train.py` — `best_f1` |
| Secret key | `ai_placement_secret_2024` | `app.py` — change in production! |

---

## 🗄 Database Schema

### `predictions` table

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `timestamp` | TEXT | Prediction datetime |
| `student_name` | TEXT | Student name |
| `cgpa` | REAL | CGPA value |
| `internships` | INTEGER | Internship count |
| `projects` | INTEGER | Project count |
| `workshops` | INTEGER | Workshop/certification count |
| `aptitude_score` | REAL | Aptitude test score |
| `ssc_marks` | REAL | SSC marks percentage |
| `hsc_marks` | REAL | HSC marks percentage |
| `backlogs` | INTEGER | Number of backlogs |
| `probability` | REAL | Placement probability (%) |
| `risk_score` | REAL | Risk score (0–100) |
| `category` | TEXT | High/Medium/Low Chance |
| `prediction` | TEXT | Placed / Not Placed |
| `recommendations` | TEXT | JSON array of recommendations |
| `feature_importance` | TEXT | JSON dict of feature weights |

### `model_metrics` table

Stores per-run model training metrics (accuracy, precision, recall, F1, best flag).

---

## 🔒 Production Deployment

> This app uses Flask's built-in development server. For production:

1. **Change the secret key** in `app.py`
2. Use a production WSGI server (e.g., Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5050 app:app
   ```
3. Put Nginx as a reverse proxy in front
4. Use environment variables for secrets

---

## 🐛 Troubleshooting

| Issue | Fix |
|---|---|
| `ModuleNotFoundError: database.db` | Run from `ai_placement_system/` directory, not parent |
| `No module named 'matplotlib'` | Run `pip install -r requirements.txt` inside the venv |
| Slow startup (~30–60s) | Normal on first run — models are being trained |
| Port 5050 already in use | Change port in `run.py` last line: `app.run(port=XXXX)` |
| Kaggle download fails | App will automatically use synthetic data — no action needed |
| Old UI showing after template change | Restart the Flask server (Ctrl+C → `python run.py`) |

---

## 📄 License

This project is for educational and research use. Dataset reference:  
[Indian Engineering College Placement Dataset](https://www.kaggle.com/datasets/vishardmehta/indian-engineering-college-placement-dataset) by Vishard Mehta on Kaggle.

---

<div align="center">
Built with ❤️ using Flask · scikit-learn · SHAP · Chart.js
</div>
