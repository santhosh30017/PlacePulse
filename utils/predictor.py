import numpy as np
import pandas as pd
import os
import json
import joblib

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'model')

def prepare_input(data, feature_cols, scaler):
    """Prepare single student input for prediction."""
    # Base features
    cgpa = float(data.get('cgpa', 7.0))
    ssc = float(data.get('ssc_marks', 70.0))
    hsc = float(data.get('hsc_marks', 70.0))
    internships = int(data.get('internships', 0))
    projects = int(data.get('projects', 0))
    workshops = int(data.get('workshops', 0))
    apt = float(data.get('aptitude_score', 65.0))
    soft = float(data.get('soft_skills', 3.5))
    backlogs = int(data.get('backlogs', 0))
    extra = 1 if str(data.get('extracurricular', 'No')).lower() == 'yes' else 0
    training = 1 if str(data.get('placement_training', 'No')).lower() == 'yes' else 0
    stream_enc = int(data.get('stream_encoded', 0))
    gender_enc = int(data.get('gender_encoded', 0))

    # Engineered
    academic_score = cgpa / 10 * 0.5 + ssc / 100 * 0.25 + hsc / 100 * 0.25
    exp_score = internships * 0.4 + projects * 0.3 + workshops * 0.3
    skill_score = apt / 100 * 0.5 + soft / 5 * 0.3 + extra * 0.2
    overall_score = academic_score * 0.4 + (exp_score / 3.0) * 0.35 + skill_score * 0.25
    has_backlog = 1 if backlogs > 0 else 0
    high_cgpa = 1 if cgpa >= 8.0 else 0

    row = {
        'CGPA': cgpa, 'SSC_Marks': ssc, 'HSC_Marks': hsc,
        'Internships': internships, 'Projects': projects,
        'Workshops_Certifications': workshops, 'AptitudeTestScore': apt,
        'SoftSkillsRating': soft, 'Backlogs': backlogs,
        'Academic_Score': academic_score, 'Experience_Score': exp_score,
        'Skill_Score': skill_score, 'Overall_Score': overall_score,
        'Has_Backlog': has_backlog, 'High_CGPA': high_cgpa,
        'Stream_Encoded': stream_enc, 'Gender_Encoded': gender_enc,
        'ExtracurricularActivities_Enc': extra, 'PlacementTraining_Enc': training
    }

    # Only use features that the model was trained on
    X = pd.DataFrame([{k: row.get(k, 0) for k in feature_cols}])
    X_scaled_arr = scaler.transform(X)
    X_scaled_df = pd.DataFrame(X_scaled_arr, columns=feature_cols)
    return X_scaled_df, row

def compute_shap_approximation(model, X_scaled, feature_cols, base_value=0.5):
    """Compute real SHAP values or fall back to permutation-based approximation."""
    try:
        import shap
        # Use KernelExplainer for general models (e.g. LogisticRegression) 
        # but only for the specific instance to keep it fast
        background = np.zeros((1, len(feature_cols))) # mean backround
        explainer = shap.KernelExplainer(model.predict_proba, background)
        shap_values = explainer.shap_values(X_scaled, silent=True)
        
        # shap_values[1] is for the 'Placed' class (index 1)
        if isinstance(shap_values, list):
            res = shap_values[1][0].tolist()
        else:
            # For some models it might return a single array if it's binary
            res = shap_values[0].tolist()
        return res
        
    except Exception as e:
        print(f"SHAP Error: {e}")
        # Fallback to permutation approximation
        try:
            df_base = pd.DataFrame(X_scaled, columns=feature_cols)
            pred_base = model.predict_proba(df_base)[0][1]
            shap_vals = []
            for i, col in enumerate(feature_cols):
                df_perm = df_base.copy()
                df_perm[col] = 0  # zero out feature (mean of scaled data = 0)
                pred_without = model.predict_proba(df_perm)[0][1]
                shap_vals.append(float(pred_base - pred_without))
            return shap_vals
        except:
            return [0.0] * len(feature_cols)

def generate_recommendations(data, probability, feature_importance):
    """AI-powered recommendation engine."""
    recs = []
    cgpa = float(data.get('cgpa', 7.0))
    internships = int(data.get('internships', 0))
    projects = int(data.get('projects', 0))
    apt = float(data.get('aptitude_score', 65.0))
    soft = float(data.get('soft_skills', 3.5))
    backlogs = int(data.get('backlogs', 0))
    workshops = int(data.get('workshops', 0))
    training = str(data.get('placement_training', 'No')).lower()
    
    # CGPA recommendations
    if cgpa < 7.0:
        recs.append({
            'priority': 'HIGH',
            'icon': '📚',
            'title': 'Improve Academic Performance',
            'detail': f'Your CGPA of {cgpa:.1f} is below the competitive threshold. Students with CGPA ≥ 7.5 have 40% higher placement rates. Focus on core subjects and seek academic mentoring.'
        })
    elif cgpa < 8.0:
        recs.append({
            'priority': 'MEDIUM',
            'icon': '📖',
            'title': 'Strengthen Academic Record',
            'detail': f'CGPA of {cgpa:.1f} is decent. Pushing to 8.0+ can significantly improve your chances with top recruiters who often filter at 7.5–8.0 cutoffs.'
        })
    
    # Internship recommendations
    if internships == 0:
        recs.append({
            'priority': 'HIGH',
            'icon': '💼',
            'title': 'Get Industry Internship Experience',
            'detail': 'You have 0 internships. Students with even 1 internship are 55% more likely to be placed. Apply to summer internships, industry projects, or virtual internship programs immediately.'
        })
    elif internships == 1:
        recs.append({
            'priority': 'MEDIUM',
            'icon': '💼',
            'title': 'Add More Internship Experience',
            'detail': 'Having 2+ internships significantly boosts your profile. Look for part-time, virtual, or short-term internship opportunities in your domain.'
        })
    
    # Aptitude score
    if apt < 60:
        recs.append({
            'priority': 'HIGH',
            'icon': '🧠',
            'title': 'Boost Aptitude Test Score',
            'detail': f'Aptitude score of {apt:.0f}/100 needs improvement. Most companies screen on aptitude. Practice quantitative reasoning, logical puzzles, and verbal ability daily for 3–4 weeks.'
        })
    elif apt < 75:
        recs.append({
            'priority': 'MEDIUM',
            'icon': '🎯',
            'title': 'Sharpen Aptitude Skills',
            'detail': f'Score of {apt:.0f}/100 is average. Target 80+ with focused practice on time management, number series, and data interpretation problems.'
        })
    
    # Projects
    if projects < 2:
        recs.append({
            'priority': 'MEDIUM',
            'icon': '🛠️',
            'title': 'Build More Projects',
            'detail': f'Only {projects} project(s) listed. Build 3–5 domain-relevant projects and host them on GitHub. Real-world projects demonstrate practical skills more than grades.'
        })
    
    # Backlogs
    if backlogs > 0:
        recs.append({
            'priority': 'CRITICAL',
            'icon': '⚠️',
            'title': 'Clear Pending Backlogs',
            'detail': f'You have {backlogs} backlog(s). Many companies have zero-backlog policies. Clearing all backlogs should be your immediate priority as it directly blocks placement opportunities.'
        })
    
    # Soft skills
    if soft < 3.0:
        recs.append({
            'priority': 'MEDIUM',
            'icon': '🗣️',
            'title': 'Improve Communication & Soft Skills',
            'detail': 'Soft skills rating is below average. Join a communication club, participate in group discussions, and practice mock interviews. HR rounds heavily weigh communication skills.'
        })
    
    # Workshops
    if workshops < 2:
        recs.append({
            'priority': 'LOW',
            'icon': '🎓',
            'title': 'Attend Workshops & Get Certifications',
            'detail': 'Earn 2–3 industry-recognized certifications (AWS, Google, Coursera). These differentiate you in a competitive pool and show initiative to learn beyond the curriculum.'
        })
    
    # Placement training
    if training == 'no':
        recs.append({
            'priority': 'MEDIUM',
            'icon': '🏆',
            'title': 'Enroll in Placement Training',
            'detail': 'Students who complete placement training are significantly better prepared for interviews. Enroll in your college\'s TPO program or online placement prep courses.'
        })
    
    # High probability positive feedback
    if probability >= 0.75 and not recs:
        recs.append({
            'priority': 'INFO',
            'icon': '✅',
            'title': 'Strong Profile – Keep It Up!',
            'detail': 'Your profile is excellent. Focus on interview preparation, company research, and applying to your target companies early in the placement season.'
        })
    
    return recs[:6]

def compute_risk_score(probability, data):
    """Generate a placement risk score 0–100 (higher = more at risk)."""
    base_risk = (1 - probability) * 70
    backlogs = int(data.get('backlogs', 0))
    backlogs_risk = min(backlogs * 8, 20)
    cgpa = float(data.get('cgpa', 7.0))
    cgpa_risk = max(0, (6.0 - cgpa) * 3) if cgpa < 6.0 else 0
    total_risk = min(100, base_risk + backlogs_risk + cgpa_risk)
    return round(total_risk, 1)

def get_performance_category(probability):
    if probability >= 0.75:
        return 'High Chance', '#00d4aa', '🚀'
    elif probability >= 0.45:
        return 'Medium Chance', '#ffd166', '📈'
    else:
        return 'Low Chance', '#ff6b6b', '⚠️'

def generate_auto_insights(df):
    """Generate text insights from dataset statistics."""
    insights = []
    
    cgpa_threshold = 8.0
    high_cgpa_rate = df[df['CGPA'] >= cgpa_threshold]['PlacementStatus'].mean() * 100
    low_cgpa_rate = df[df['CGPA'] < cgpa_threshold]['PlacementStatus'].mean() * 100
    insights.append(f"📊 Students with CGPA ≥ {cgpa_threshold} have a {high_cgpa_rate:.1f}% placement rate, compared to {low_cgpa_rate:.1f}% for those below.")
    
    if 'Internships' in df.columns:
        for n in [1, 2]:
            rate = df[df['Internships'] >= n]['PlacementStatus'].mean() * 100
            insights.append(f"💼 Students with {n}+ internship(s) achieve a {rate:.1f}% placement rate.")
    
    if 'AptitudeTestScore' in df.columns:
        apt_corr = df[['AptitudeTestScore', 'PlacementStatus']].corr().iloc[0, 1]
        insights.append(f"🎯 Aptitude test scores show a {abs(apt_corr):.2f} correlation with placement — {'strong' if abs(apt_corr) > 0.4 else 'moderate'} predictor.")
    
    if 'Backlogs' in df.columns:
        no_backlog_rate = df[df['Backlogs'] == 0]['PlacementStatus'].mean() * 100
        backlog_rate = df[df['Backlogs'] > 0]['PlacementStatus'].mean() * 100
        insights.append(f"⚠️ Students with no backlogs have {no_backlog_rate:.1f}% placement rate vs {backlog_rate:.1f}% for those with backlogs.")
    
    if 'Projects' in df.columns:
        high_proj = df[df['Projects'] >= 3]['PlacementStatus'].mean() * 100
        insights.append(f"🛠️ Students with 3+ projects see a {high_proj:.1f}% placement rate — projects are a differentiating factor.")
    
    if 'Stream' in df.columns:
        top_stream = df.groupby('Stream')['PlacementStatus'].mean().idxmax()
        top_rate = df.groupby('Stream')['PlacementStatus'].mean().max() * 100
        insights.append(f"🏫 {top_stream} has the highest placement rate at {top_rate:.1f}% among all streams.")
    
    overall = df['PlacementStatus'].mean() * 100
    insights.append(f"📈 Overall campus placement rate is {overall:.1f}% based on the current dataset of {len(df)} students.")
    
    return insights
