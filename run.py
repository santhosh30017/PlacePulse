#!/usr/bin/env python3
"""
AI Placement Intelligence System - Startup Script
Run this to initialize the full pipeline and launch the web server.
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# Ensure all directories exist
for d in ['data', 'model', 'evaluation', 'static/graphs', 'database']:
    os.makedirs(os.path.join(os.path.dirname(__file__), d), exist_ok=True)

if __name__ == '__main__':
    from database.db import init_db
    from app import app, initialize_pipeline

    print("=" * 55)
    print("  AI PLACEMENT INTELLIGENCE SYSTEM")
    print("  End-to-End ML Decision Platform")
    print("=" * 55)
    print()

    print("[1/2] Initializing database...")
    init_db()

    print("[2/2] Running full ML pipeline (may take ~30s)...")
    initialize_pipeline()

    print()
    print("=" * 55)
    print("  SERVER READY  →  http://localhost:5050")
    print("=" * 55)
    print()
    print("  Pages:")
    print("    Home       →  http://localhost:5050/")
    print("    Predict    →  http://localhost:5050/predict")
    print("    Dashboard  →  http://localhost:5050/dashboard")
    print("    Analytics  →  http://localhost:5050/analytics")
    print("    History    →  http://localhost:5050/history")
    print("    Upload     →  http://localhost:5050/upload")
    print()

    app.run(debug=False, port=5050, use_reloader=False)
