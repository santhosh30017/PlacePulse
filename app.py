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
