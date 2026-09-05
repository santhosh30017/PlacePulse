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
