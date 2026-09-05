import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'placement.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            student_name TEXT,
            cgpa REAL,
            internships INTEGER,
            projects INTEGER,
            workshops INTEGER,
            aptitude_score REAL,
            ssc_marks REAL,
            hsc_marks REAL,
            backlogs INTEGER,
            probability REAL,
            risk_score REAL,
            category TEXT,
            prediction TEXT,
            recommendations TEXT,
            feature_importance TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS model_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            model_name TEXT,
            accuracy REAL,
            precision_score REAL,
            recall REAL,
            f1_score REAL,
            is_best INTEGER DEFAULT 0
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS improvement_tracker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            student_name TEXT,
            before_score REAL,
            after_score REAL,
            new_prediction TEXT,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_tracker_entry(student_name, before, after, prediction, notes=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO improvement_tracker (timestamp, student_name, before_score, after_score, new_prediction, notes)
        VALUES (?,?,?,?,?,?)
    ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), student_name, before, after, prediction, notes))
    conn.commit()
    conn.close()

def get_tracker_entries():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM improvement_tracker ORDER BY timestamp DESC')
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_prediction(data):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO predictions 
        (timestamp, student_name, cgpa, internships, projects, workshops,
         aptitude_score, ssc_marks, hsc_marks, backlogs, probability,
         risk_score, category, prediction, recommendations, feature_importance)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        data.get('student_name', 'Anonymous'),
        data.get('cgpa'), data.get('internships'), data.get('projects'),
        data.get('workshops'), data.get('aptitude_score'), data.get('ssc_marks'),
        data.get('hsc_marks'), data.get('backlogs'), data.get('probability'),
        data.get('risk_score'), data.get('category'), data.get('prediction'),
        json.dumps(data.get('recommendations', [])),
        json.dumps(data.get('feature_importance', {}))
    ))
    conn.commit()
    conn.close()

def get_all_predictions():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM predictions ORDER BY timestamp DESC')
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_analytics():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM predictions')
    total = c.fetchone()[0]
    c.execute('SELECT AVG(probability) FROM predictions')
    avg_prob = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM predictions WHERE prediction='Placed'")
    placed = c.fetchone()[0]
    c.execute('SELECT AVG(risk_score) FROM predictions')
    avg_risk = c.fetchone()[0] or 0
    conn.close()
    return {
        'total_predictions': total,
        'avg_probability': round(avg_prob, 2),
        'placed_count': placed,
        'not_placed_count': total - placed,
        'avg_risk_score': round(avg_risk, 2),
        'placement_rate': round((placed / total * 100) if total > 0 else 0, 2)
    }

def save_model_metrics(metrics_list, best_model):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM model_metrics')
    for m in metrics_list:
        c.execute('''
            INSERT INTO model_metrics (timestamp, model_name, accuracy, precision_score, recall, f1_score, is_best)
            VALUES (?,?,?,?,?,?,?)
        ''', (
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            m['name'], m['accuracy'], m['precision'], m['recall'], m['f1'],
            1 if m['name'] == best_model else 0
        ))
    conn.commit()
    conn.close()

def get_model_metrics():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM model_metrics')
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]
