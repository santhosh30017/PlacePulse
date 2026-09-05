import pandas as pd
import numpy as np
import os
import json

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def generate_synthetic_dataset(n=500):
    """Generate realistic synthetic placement dataset when kaggle unavailable."""
    np.random.seed(42)
    
    cgpa = np.clip(np.random.normal(7.5, 1.2, n), 4.0, 10.0)
    ssc_marks = np.clip(np.random.normal(72, 12, n), 40, 100)
    hsc_marks = np.clip(np.random.normal(70, 13, n), 40, 100)
    internships = np.random.randint(0, 4, n)
    projects = np.random.randint(0, 6, n)
    workshops = np.random.randint(0, 5, n)
    aptitude_score = np.clip(np.random.normal(65, 15, n), 20, 100)
    backlogs = np.random.choice([0, 0, 0, 1, 2, 3], n)
    
    # Placement probability based on features
    score = (
        (cgpa - 4) / 6 * 0.35 +
        internships / 3 * 0.20 +
        projects / 5 * 0.15 +
        (aptitude_score - 20) / 80 * 0.15 +
        (ssc_marks - 40) / 60 * 0.08 +
        (hsc_marks - 40) / 60 * 0.07 -
        backlogs * 0.05
    )
    prob = 1 / (1 + np.exp(-5 * (score - 0.5)))
    placement = (np.random.random(n) < prob).astype(int)
    
    stream = np.random.choice(['Computer Science', 'Electronics', 'Mechanical', 'Civil', 'Information Technology'], n)
    gender = np.random.choice(['Male', 'Female'], n)
    
    df = pd.DataFrame({
        'StudentID': range(1, n+1),
        'Stream': stream,
        'Gender': gender,
        'CGPA': np.round(cgpa, 2),
        'SSC_Marks': np.round(ssc_marks, 1),
        'HSC_Marks': np.round(hsc_marks, 1),
        'Internships': internships,
        'Projects': projects,
        'Workshops_Certifications': workshops,
        'AptitudeTestScore': np.round(aptitude_score, 1),
        'SoftSkillsRating': np.round(np.clip(np.random.normal(3.5, 0.8, n), 1, 5), 1),
        'ExtracurricularActivities': np.random.choice(['Yes', 'No'], n),
        'PlacementTraining': np.random.choice(['Yes', 'No'], n),
        'Backlogs': backlogs,
        'PlacementStatus': placement
    })
    return df

def load_dataset():
    """Try to load from kaggle or use synthetic data."""
    csv_path = os.path.join(DATA_DIR, 'placement_data.csv')
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        print(f"Loaded existing dataset: {len(df)} records")
        return df
    
    # Try kagglehub
    try:
        import kagglehub
        path = kagglehub.dataset_download("vishardmehta/indian-engineering-college-placement-dataset")
        print("Path to dataset files:", path)
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith('.csv'):
                    df = pd.read_csv(os.path.join(root, f))
                    df.to_csv(csv_path, index=False)
                    print(f"Loaded from kaggle: {len(df)} records")
                    return df
    except Exception as e:
        print(f"Kaggle not available ({e}), generating synthetic dataset")
    
    df = generate_synthetic_dataset(600)
    df.to_csv(csv_path, index=False)
    print(f"Generated synthetic dataset: {len(df)} records")
    return df

def clean_data(df):
    """Clean and standardize the dataframe."""
    df = df.copy()
    # Standardize column names
    col_map = {}
    for col in df.columns:
        lower = col.lower().replace(' ', '_')
        if 'cgpa' in lower or 'gpa' in lower: col_map[col] = 'CGPA'
        elif 'ssc' in lower: col_map[col] = 'SSC_Marks'
        elif 'hsc' in lower: col_map[col] = 'HSC_Marks'
        elif 'intern' in lower: col_map[col] = 'Internships'
        elif 'project' in lower: col_map[col] = 'Projects'
        elif 'workshop' in lower or 'certif' in lower: col_map[col] = 'Workshops_Certifications'
        elif 'aptitude' in lower or 'apt' in lower: col_map[col] = 'AptitudeTestScore'
        elif 'soft' in lower or 'skill' in lower: col_map[col] = 'SoftSkillsRating'
        elif 'extra' in lower or 'activity' in lower: col_map[col] = 'ExtracurricularActivities'
        elif 'training' in lower: col_map[col] = 'PlacementTraining'
        elif 'backlog' in lower: col_map[col] = 'Backlogs'
        elif 'placement' in lower and 'status' in lower: col_map[col] = 'PlacementStatus'
        elif 'stream' in lower or 'branch' in lower: col_map[col] = 'Stream'
        elif 'gender' in lower: col_map[col] = 'Gender'
    df = df.rename(columns=col_map)
    
    # Ensure essential columns
    required = ['CGPA', 'Internships', 'Projects', 'AptitudeTestScore', 'PlacementStatus']
    for col in required:
        if col not in df.columns:
            if col == 'CGPA': df[col] = np.random.normal(7.5, 1.0, len(df))
            elif col in ['Internships', 'Projects']: df[col] = np.random.randint(0, 3, len(df))
            elif col == 'AptitudeTestScore': df[col] = np.random.normal(65, 15, len(df))
            elif col == 'PlacementStatus': df[col] = np.random.randint(0, 2, len(df))
    
    for col in ['SSC_Marks', 'HSC_Marks']:
        if col not in df.columns: df[col] = np.random.normal(70, 12, len(df))
    for col in ['Workshops_Certifications', 'Backlogs']:
        if col not in df.columns: df[col] = 0
    for col in ['SoftSkillsRating']:
        if col not in df.columns: df[col] = np.random.normal(3.5, 0.8, len(df))
    for col in ['ExtracurricularActivities', 'PlacementTraining']:
        if col not in df.columns: df[col] = np.random.choice(['Yes', 'No'], len(df))
    if 'Stream' not in df.columns: df['Stream'] = 'Computer Science'
    if 'Gender' not in df.columns: df['Gender'] = np.random.choice(['Male', 'Female'], len(df))
    
    # Convert target
    if df['PlacementStatus'].dtype == object:
        df['PlacementStatus'] = df['PlacementStatus'].map({'Placed': 1, 'Not Placed': 0, 'placed': 1, 'not placed': 0}).fillna(0).astype(int)
    
    # Fill numeric NAs
    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].fillna(df[col].median())
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].fillna(df[col].mode()[0] if len(df[col].mode()) > 0 else 'Unknown')
    
    return df

def engineer_features(df):
    """Create new engineered features."""
    df = df.copy()
    df['Academic_Score'] = (df['CGPA'] / 10 * 0.5 + 
                            df.get('SSC_Marks', pd.Series([70]*len(df))) / 100 * 0.25 + 
                            df.get('HSC_Marks', pd.Series([70]*len(df))) / 100 * 0.25)
    df['Experience_Score'] = (df['Internships'] * 0.4 + df['Projects'] * 0.3 + 
                               df.get('Workshops_Certifications', 0) * 0.3)
    df['Skill_Score'] = (df.get('AptitudeTestScore', 65) / 100 * 0.5 + 
                          df.get('SoftSkillsRating', 3.5) / 5 * 0.3 +
                          (df.get('ExtracurricularActivities', 'No').map({'Yes': 1, 'No': 0}) if df.get('ExtracurricularActivities', pd.Series(['No'])).dtype == object else 0) * 0.2)
    df['Overall_Score'] = (df['Academic_Score'] * 0.4 + 
                            df['Experience_Score'] / df['Experience_Score'].max() * 0.35 + 
                            df['Skill_Score'] * 0.25)
    df['Has_Backlog'] = (df.get('Backlogs', 0) > 0).astype(int)
    df['High_CGPA'] = (df['CGPA'] >= 8.0).astype(int)
    return df

def encode_and_normalize(df):
    """Encode categoricals and normalize numerics."""
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    import joblib
    
    df = df.copy()
    le_stream = LabelEncoder()
    le_gender = LabelEncoder()
    
    if df['Stream'].dtype == object:
        df['Stream_Encoded'] = le_stream.fit_transform(df['Stream'].astype(str))
    else:
        df['Stream_Encoded'] = df['Stream']
        
    if df['Gender'].dtype == object:
        df['Gender_Encoded'] = le_gender.fit_transform(df['Gender'].astype(str))
    else:
        df['Gender_Encoded'] = df['Gender']
    
    for col in ['ExtracurricularActivities', 'PlacementTraining']:
        if col in df.columns and df[col].dtype == object:
            df[col + '_Enc'] = df[col].map({'Yes': 1, 'No': 0}).fillna(0)
    
    feature_cols = [
        'CGPA', 'SSC_Marks', 'HSC_Marks', 'Internships', 'Projects',
        'Workshops_Certifications', 'AptitudeTestScore', 'SoftSkillsRating',
        'Backlogs', 'Academic_Score', 'Experience_Score', 'Skill_Score',
        'Overall_Score', 'Has_Backlog', 'High_CGPA', 'Stream_Encoded',
        'Gender_Encoded', 'ExtracurricularActivities_Enc', 'PlacementTraining_Enc'
    ]
    existing_features = [c for c in feature_cols if c in df.columns]
    # Convert all selected columns to numeric, coercing errors
    for col in existing_features:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    scaler = StandardScaler()
    X = df[existing_features].copy()
    X_scaled = scaler.fit_transform(X)
    X_scaled_df = pd.DataFrame(X_scaled, columns=existing_features)
    
    model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'model')
    joblib.dump(scaler, os.path.join(model_dir, 'scaler.pkl'))
    joblib.dump(existing_features, os.path.join(model_dir, 'feature_cols.pkl'))
    joblib.dump(le_stream, os.path.join(model_dir, 'le_stream.pkl'))
    joblib.dump(le_gender, os.path.join(model_dir, 'le_gender.pkl'))
    
    y = df['PlacementStatus']
    return X_scaled_df, y, existing_features

def save_stats(df):
    stats = {
        'total_students': int(len(df)),
        'placement_rate': float(round(df['PlacementStatus'].mean() * 100, 2)),
        'avg_cgpa': float(round(df['CGPA'].mean(), 2)),
        'avg_internships': float(round(df['Internships'].mean(), 2)),
        'placed_count': int(df['PlacementStatus'].sum()),
        'not_placed_count': int((df['PlacementStatus'] == 0).sum()),
        'streams': df['Stream'].value_counts().to_dict() if 'Stream' in df.columns else {}
    }
    stats_path = os.path.join(DATA_DIR, 'stats.json')
    with open(stats_path, 'w') as f:
        json.dump(stats, f)
    return stats
