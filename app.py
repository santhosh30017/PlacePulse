import os
import sys
import json
import csv
import io
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from werkzeug.utils import secure_filename

sys.path.insert(0, os.path.dirname(__file__))
os.makedirs(os.path.join(os.path.dirname(__file__), 'data'), exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), 'model'), exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), 'evaluation'), exist_ok=True)

from database.db import init_db, save_prediction, get_all_predictions, get_analytics, get_model_metrics, save_tracker_entry, get_tracker_entries

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ai_placement_secret_2024'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'data')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Global state
pipeline_ready = False
df_global = None
insights_global = []

def initialize_pipeline(df=None):
    global pipeline_ready, df_global, insights_global
    from utils.data_pipeline import load_dataset, clean_data, engineer_features, encode_and_normalize, save_stats
    from utils.eda import generate_all_graphs
    from model.train import train_all_models
    from utils.predictor import generate_auto_insights
    from database.db import save_model_metrics

    print("Initializing AI placement pipeline...")
    if df is None:
        df = load_dataset()
    df = clean_data(df)
    df_global = engineer_features(df)
    save_stats(df_global)
    generate_all_graphs(df_global)
    X, y, feature_cols = encode_and_normalize(df_global)
    results, best_name, best_model = train_all_models(X, y)
    save_model_metrics(results, best_name)
    insights_global = generate_auto_insights(df_global)
    pipeline_ready = True
    print("Pipeline ready!")

def get_model():
    from model.train import load_best_model
    return load_best_model()

# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    stats = {}
    stats_path = os.path.join(app.root_path, 'data', 'stats.json')
    if os.path.exists(stats_path):
        with open(stats_path) as f:
            stats = json.load(f)
    return render_template('index.html', stats=stats, ready=pipeline_ready)

@app.route('/predict', methods=['GET'])
def predict_page():
    return render_template('predict.html')

@app.route('/predict', methods=['POST'])
def predict_api():
    try:
        data = request.get_json() or request.form.to_dict()
        model, scaler, feature_cols, model_name = get_model()
        if model is None:
            return jsonify({'error': 'Model not trained yet. Please wait for initialization.'}), 503

        from utils.predictor import prepare_input, compute_shap_approximation, generate_recommendations, compute_risk_score, get_performance_category
        from utils.eda import generate_shap_bar
        from model.train import get_feature_importance

        X_scaled, row = prepare_input(data, feature_cols, scaler)
        prob = float(model.predict_proba(X_scaled)[0][1])
        prediction = 'Placed' if prob >= 0.5 else 'Not Placed'
        risk_score = compute_risk_score(prob, data)
        category, color, icon = get_performance_category(prob)
        
        shap_vals = compute_shap_approximation(model, X_scaled, feature_cols)
        generate_shap_bar(feature_cols, shap_vals)

        fi = get_feature_importance()
        top_features = sorted(fi.items(), key=lambda x: x[1], reverse=True)[:5] if fi else []

        from utils.weakness_detector import detect_weaknesses
        from utils.recommendation_engine import generate_advanced_recommendations
        from utils.career_score import compute_employability_score
        
        # New AI Analysis
        weaknesses = detect_weaknesses(data)
        career_score = compute_employability_score(data)
        recommendations = generate_advanced_recommendations(data, prob * 100, weaknesses)
        
        from utils.llm_service import get_report_summary, get_personalized_recommendations
        
        # Try to get a real AI summary if Ollama is available
        ai_summary = get_report_summary(data, {
            'prediction': prediction,
            'probability': round(prob * 100, 2),
            'top_positive': [f for f, v in zip(feature_cols, shap_vals) if v > 0.02][:3],
            'top_negative': [f for f, v in zip(feature_cols, shap_vals) if v < -0.02][:3],
            'risk_score': risk_score
        })

        result = {
            'student_name': data.get('student_name', 'Student'),
            'probability': round(prob * 100, 2),
            'prediction': prediction,
            'risk_score': risk_score,
            'category': category,
            'category_color': color,
            'category_icon': icon,
            'recommendations': recommendations,
            'feature_importance': dict(top_features),
            'shap_plot': 'graphs/shap_plot.png',
            'model_used': model_name,
            'top_positive': [f for f, v in zip(feature_cols, shap_vals) if v > 0.02][:3],
            'top_negative': [f for f, v in zip(feature_cols, shap_vals) if v < -0.02][:3],
            'weaknesses': weaknesses,
            'career_score': career_score,
            'ai_summary': ai_summary,
            'input_data': data
        }

        db_data = {**data, **{
            'probability': round(prob * 100, 2),
            'risk_score': risk_score,
            'category': category,
            'prediction': prediction,
            'recommendations': recommendations,
            'feature_importance': dict(top_features),
            'ai_summary': ai_summary
        }}
        save_prediction(db_data)

        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/result')
def result_page():
    return render_template('result.html')

@app.route('/dashboard')
def dashboard():
    stats = {}
    stats_path = os.path.join(app.root_path, 'data', 'stats.json')
    if os.path.exists(stats_path):
        with open(stats_path) as f:
            stats = json.load(f)
    
    from model.train import get_metrics, get_feature_importance
    metrics = get_metrics()
    fi = get_feature_importance()
    analytics = get_analytics()
    
    graphs = [
        ('cgpa_placement', 'CGPA vs Placement'),
        ('internships_placement', 'Internships vs Placement'),
        ('skills_placement', 'Aptitude Score Distribution'),
        ('projects_placement', 'Projects vs Placement'),
        ('placement_distribution', 'Placement Distribution'),
        ('heatmap', 'Correlation Heatmap'),
        ('stream_placement', 'Stream-wise Placement'),
        ('feature_importance', 'Feature Importance'),
        ('roc_curve', 'ROC Curve'),
        ('confusion_matrix', 'Confusion Matrix'),
        ('model_comparison', 'Model Comparison'),
    ]
    existing_graphs = [(g, l) for g, l in graphs if os.path.exists(
        os.path.join(app.root_path, 'static', 'graphs', f'{g}.png'))]
    
    return render_template('dashboard.html', 
                           stats=stats, metrics=metrics, fi=fi,
                           analytics=analytics, graphs=existing_graphs,
                           insights=insights_global)

@app.route('/analytics')
def analytics_page():
    analytics = get_analytics()
    model_metrics = get_model_metrics()
    from model.train import get_metrics
    metrics = get_metrics()
    return render_template('analytics.html', analytics=analytics, 
                           model_metrics=model_metrics, metrics=metrics,
                           insights=insights_global)

@app.route('/history')
def history_page():
    predictions = get_all_predictions()
    for p in predictions:
        try:
            p['recommendations'] = json.loads(p['recommendations']) if p['recommendations'] else []
        except:
            p['recommendations'] = []
        try:
            p['feature_importance'] = json.loads(p['feature_importance']) if p['feature_importance'] else {}
        except:
            p['feature_importance'] = {}
    return render_template('history.html', predictions=predictions)

@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        f = request.files['file']
        if f.filename == '' or not f.filename.endswith('.csv'):
            return jsonify({'error': 'Please upload a valid CSV file'}), 400
        
        filename = secure_filename('placement_data.csv')
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        f.save(save_path)
        
        try:
            df = pd.read_csv(save_path)
            initialize_pipeline(df)
            return jsonify({'success': True, 'message': f'Dataset uploaded ({len(df)} rows). Model retrained successfully!', 'rows': len(df)})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return render_template('upload.html')

@app.route('/metrics')
def metrics_api():
    from model.train import get_metrics
    return jsonify(get_metrics())

@app.route('/api/history')
def history_api():
    predictions = get_all_predictions()
    return jsonify(predictions)

@app.route('/api/analytics')
def analytics_api():
    return jsonify(get_analytics())

@app.route('/api/insights')
def insights_api():
    return jsonify({'insights': insights_global})

# ─────────────────────────────────────────────────────────────────────────────
# NEW AI UPGRADE ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/improvement')
def improvement_hub():
    return render_template('improvement.html')

@app.route('/plan')
def plan_page():
    skill = request.args.get('skill')
    from utils.skill_plan import get_all_plan_keys, get_plan, generate_combined_timeline
    plans_list = get_all_plan_keys()
    
    selected_plan = None
    timeline = []
