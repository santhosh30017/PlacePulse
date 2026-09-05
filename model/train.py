import os
import json
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, roc_curve, auc, confusion_matrix)

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'model')
EVAL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'evaluation')
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(EVAL_DIR, exist_ok=True)

def train_all_models(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
        'SVM': SVC(probability=True, random_state=42, kernel='rbf')
    }
    
    results = []
    best_f1 = 0
    best_name = None
    best_model = None
    
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        auc_score = auc(fpr, tpr)
        cm = confusion_matrix(y_test, y_pred).tolist()
        
        result = {
            'name': name,
            'accuracy': round(float(acc), 4),
            'precision': round(float(prec), 4),
            'recall': round(float(rec), 4),
            'f1': round(float(f1), 4),
            'auc': round(float(auc_score), 4),
            'confusion_matrix': cm,
            'fpr': fpr.tolist(),
            'tpr': tpr.tolist()
        }
        results.append(result)
        
        if f1 > best_f1:
            best_f1 = f1
            best_name = name
            best_model = model
        
        joblib.dump(model, os.path.join(MODEL_DIR, f'{name.replace(" ", "_").lower()}.pkl'))
    
    # Save best model
    joblib.dump(best_model, os.path.join(MODEL_DIR, 'best_model.pkl'))
    with open(os.path.join(MODEL_DIR, 'best_model_name.txt'), 'w') as f:
        f.write(best_name)
    
    # Save all metrics
    metrics_data = {
        'models': results,
        'best_model': best_name,
        'feature_names': list(X.columns),
        'test_size': len(X_test),
        'train_size': len(X_train)
    }
    with open(os.path.join(EVAL_DIR, 'metrics.json'), 'w') as f:
        json.dump(metrics_data, f, indent=2)
    
    # Generate graphs
    from utils.eda import generate_feature_importance_graph, generate_roc_curve, generate_confusion_matrix, generate_model_comparison
    
    best_result = next(r for r in results if r['name'] == best_name)
    generate_roc_curve(best_result['fpr'], best_result['tpr'], best_result['auc'], best_name)
    generate_confusion_matrix(np.array(best_result['confusion_matrix']))
    generate_model_comparison(results)
    
    # Feature importance
    if hasattr(best_model, 'feature_importances_'):
        importances = best_model.feature_importances_
        feature_names = list(X.columns)
        generate_feature_importance_graph(feature_names, importances, f"{best_name} - Feature Importance")
        
        fi_dict = dict(zip(feature_names, importances.tolist()))
        with open(os.path.join(MODEL_DIR, 'feature_importance.json'), 'w') as f:
            json.dump(fi_dict, f, indent=2)
    elif hasattr(best_model, 'coef_'):
        importances = np.abs(best_model.coef_[0])
        importances = importances / importances.sum()
        feature_names = list(X.columns)
        generate_feature_importance_graph(feature_names, importances, f"{best_name} - Coefficient Magnitude")
        fi_dict = dict(zip(feature_names, importances.tolist()))
        with open(os.path.join(MODEL_DIR, 'feature_importance.json'), 'w') as f:
            json.dump(fi_dict, f, indent=2)
    
    print(f"\nBest model: {best_name} (F1={best_f1:.4f})")
    return results, best_name, best_model

def load_best_model():
    model_path = os.path.join(MODEL_DIR, 'best_model.pkl')
    if not os.path.exists(model_path):
        return None, None, None, None
    model = joblib.load(model_path)
    scaler = joblib.load(os.path.join(MODEL_DIR, 'scaler.pkl'))
    feature_cols = joblib.load(os.path.join(MODEL_DIR, 'feature_cols.pkl'))
    with open(os.path.join(MODEL_DIR, 'best_model_name.txt')) as f:
        model_name = f.read().strip()
    return model, scaler, feature_cols, model_name

def get_metrics():
    metrics_path = os.path.join(EVAL_DIR, 'metrics.json')
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            return json.load(f)
    return {}

def get_feature_importance():
    fi_path = os.path.join(MODEL_DIR, 'feature_importance.json')
    if os.path.exists(fi_path):
        with open(fi_path) as f:
            return json.load(f)
    return {}
