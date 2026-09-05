import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

GRAPHS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'graphs')
os.makedirs(GRAPHS_DIR, exist_ok=True)

PALETTE = {'placed': '#00d4aa', 'not_placed': '#ff6b6b', 'main': '#6c63ff', 'accent': '#ffd166'}
BG = '#0f1117'
TEXT = '#e8e8f0'

def set_dark_style():
    plt.rcParams.update({
        'figure.facecolor': BG, 'axes.facecolor': '#1a1d2e',
        'axes.edgecolor': '#2d3154', 'text.color': TEXT,
        'xtick.color': TEXT, 'ytick.color': TEXT,
        'axes.labelcolor': TEXT, 'grid.color': '#2d3154',
        'axes.grid': True, 'font.family': 'DejaVu Sans'
    })

def generate_all_graphs(df):
    set_dark_style()
    graphs = {}
    
    # 1. CGPA vs Placement
    fig, ax = plt.subplots(figsize=(10, 6))
    placed = df[df['PlacementStatus'] == 1]['CGPA']
    not_placed = df[df['PlacementStatus'] == 0]['CGPA']
    ax.hist(placed, alpha=0.75, bins=25, color=PALETTE['placed'], label='Placed', edgecolor='none')
    ax.hist(not_placed, alpha=0.75, bins=25, color=PALETTE['not_placed'], label='Not Placed', edgecolor='none')
    ax.set_xlabel('CGPA', fontsize=13)
    ax.set_ylabel('Number of Students', fontsize=13)
    ax.set_title('CGPA Distribution by Placement Status', fontsize=15, fontweight='bold', color='#a78bfa')
    ax.legend(fontsize=12)
    plt.tight_layout()
    path = os.path.join(GRAPHS_DIR, 'cgpa_placement.png')
    plt.savefig(path, dpi=120, bbox_inches='tight', facecolor=BG)
    plt.close()
    graphs['cgpa_placement'] = 'graphs/cgpa_placement.png'

    # 2. Internships vs Placement
    fig, ax = plt.subplots(figsize=(10, 6))
    internship_placement = df.groupby('Internships')['PlacementStatus'].mean() * 100
    colors = [PALETTE['main'] if i % 2 == 0 else PALETTE['accent'] for i in range(len(internship_placement))]
    bars = ax.bar(internship_placement.index, internship_placement.values, color=colors, edgecolor='none', width=0.6)
    for bar, val in zip(bars, internship_placement.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{val:.1f}%',
                ha='center', va='bottom', color=TEXT, fontsize=11)
    ax.set_xlabel('Number of Internships', fontsize=13)
    ax.set_ylabel('Placement Rate (%)', fontsize=13)
    ax.set_title('Internships vs Placement Rate', fontsize=15, fontweight='bold', color='#a78bfa')
    plt.tight_layout()
    path = os.path.join(GRAPHS_DIR, 'internships_placement.png')
    plt.savefig(path, dpi=120, bbox_inches='tight', facecolor=BG)
    plt.close()
    graphs['internships_placement'] = 'graphs/internships_placement.png'

    # 3. Aptitude Score vs Placement (Skills)
    fig, ax = plt.subplots(figsize=(10, 6))
    if 'AptitudeTestScore' in df.columns:
        for status, label, color in [(1, 'Placed', PALETTE['placed']), (0, 'Not Placed', PALETTE['not_placed'])]:
            data = df[df['PlacementStatus'] == status]['AptitudeTestScore']
            ax.hist(data, bins=20, alpha=0.75, label=label, color=color, edgecolor='none')
        ax.set_xlabel('Aptitude Test Score', fontsize=13)
        ax.set_ylabel('Frequency', fontsize=13)
        ax.set_title('Aptitude Score Distribution by Placement', fontsize=15, fontweight='bold', color='#a78bfa')
        ax.legend(fontsize=12)
    plt.tight_layout()
    path = os.path.join(GRAPHS_DIR, 'skills_placement.png')
    plt.savefig(path, dpi=120, bbox_inches='tight', facecolor=BG)
    plt.close()
    graphs['skills_placement'] = 'graphs/skills_placement.png'

    # 4. Correlation Heatmap
    fig, ax = plt.subplots(figsize=(12, 9))
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()[:12]
    corr = df[num_cols].corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    cmap = sns.diverging_palette(250, 15, s=75, l=40, n=9, center="dark")
    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap=cmap, ax=ax,
                linewidths=0.5, linecolor='#0f1117', annot_kws={'size': 9},
                vmin=-1, vmax=1, cbar_kws={'shrink': 0.8})
    ax.set_title('Feature Correlation Heatmap', fontsize=15, fontweight='bold', color='#a78bfa', pad=15)
    plt.tight_layout()
    path = os.path.join(GRAPHS_DIR, 'heatmap.png')
    plt.savefig(path, dpi=120, bbox_inches='tight', facecolor=BG)
    plt.close()
    graphs['heatmap'] = 'graphs/heatmap.png'

    # 5. Placement Distribution Pie
    fig, ax = plt.subplots(figsize=(8, 8))
    placed_count = int(df['PlacementStatus'].sum())
    not_placed_count = len(df) - placed_count
    wedge_props = dict(width=0.6, edgecolor=BG, linewidth=3)
    ax.pie([placed_count, not_placed_count], labels=['Placed', 'Not Placed'],
           colors=[PALETTE['placed'], PALETTE['not_placed']],
           autopct='%1.1f%%', startangle=90, wedgeprops=wedge_props,
           textprops={'color': TEXT, 'fontsize': 14},
           pctdistance=0.75)
    ax.set_title('Overall Placement Distribution', fontsize=15, fontweight='bold', color='#a78bfa')
    plt.tight_layout()
    path = os.path.join(GRAPHS_DIR, 'placement_distribution.png')
    plt.savefig(path, dpi=120, bbox_inches='tight', facecolor=BG)
    plt.close()
    graphs['placement_distribution'] = 'graphs/placement_distribution.png'

    # 6. Projects vs Placement Rate
    fig, ax = plt.subplots(figsize=(10, 6))
    proj_data = df.groupby('Projects')['PlacementStatus'].mean() * 100
    ax.plot(proj_data.index, proj_data.values, color=PALETTE['accent'], 
            linewidth=3, marker='o', markersize=10, markerfacecolor=PALETTE['main'])
    ax.fill_between(proj_data.index, proj_data.values, alpha=0.2, color=PALETTE['accent'])
    ax.set_xlabel('Number of Projects', fontsize=13)
    ax.set_ylabel('Placement Rate (%)', fontsize=13)
    ax.set_title('Projects vs Placement Rate', fontsize=15, fontweight='bold', color='#a78bfa')
    plt.tight_layout()
    path = os.path.join(GRAPHS_DIR, 'projects_placement.png')
    plt.savefig(path, dpi=120, bbox_inches='tight', facecolor=BG)
    plt.close()
    graphs['projects_placement'] = 'graphs/projects_placement.png'

    # 7. Stream-wise placement
    if 'Stream' in df.columns:
        fig, ax = plt.subplots(figsize=(12, 6))
        stream_data = df.groupby('Stream')['PlacementStatus'].mean() * 100
        stream_data = stream_data.sort_values(ascending=True)
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(stream_data)))
        bars = ax.barh(stream_data.index, stream_data.values, color=colors, edgecolor='none')
        for bar, val in zip(bars, stream_data.values):
            ax.text(val + 0.5, bar.get_y() + bar.get_height()/2, f'{val:.1f}%',
                    va='center', color=TEXT, fontsize=11)
        ax.set_xlabel('Placement Rate (%)', fontsize=13)
        ax.set_title('Stream-wise Placement Rate', fontsize=15, fontweight='bold', color='#a78bfa')
        plt.tight_layout()
        path = os.path.join(GRAPHS_DIR, 'stream_placement.png')
        plt.savefig(path, dpi=120, bbox_inches='tight', facecolor=BG)
        plt.close()
        graphs['stream_placement'] = 'graphs/stream_placement.png'

    print(f"Generated {len(graphs)} EDA graphs")
    return graphs

def generate_feature_importance_graph(feature_names, importances, title="Feature Importance"):
    set_dark_style()
    fig, ax = plt.subplots(figsize=(10, 7))
    sorted_idx = np.argsort(importances)
    pos = np.arange(len(sorted_idx))
    colors = plt.cm.plasma(np.linspace(0.3, 0.9, len(sorted_idx)))
    ax.barh(pos, np.array(importances)[sorted_idx], color=colors, edgecolor='none')
    ax.set_yticks(pos)
    ax.set_yticklabels(np.array(feature_names)[sorted_idx], fontsize=11)
    ax.set_xlabel('Importance Score', fontsize=13)
    ax.set_title(title, fontsize=15, fontweight='bold', color='#a78bfa')
    plt.tight_layout()
    path = os.path.join(GRAPHS_DIR, 'feature_importance.png')
    plt.savefig(path, dpi=120, bbox_inches='tight', facecolor=BG)
    plt.close()
    return 'graphs/feature_importance.png'

def generate_roc_curve(fpr, tpr, auc_score, model_name):
    set_dark_style()
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.plot(fpr, tpr, color=PALETTE['placed'], linewidth=3, label=f'{model_name} (AUC={auc_score:.3f})')
    ax.plot([0, 1], [0, 1], color='#555577', linestyle='--', linewidth=2, label='Random')
    ax.fill_between(fpr, tpr, alpha=0.15, color=PALETTE['placed'])
    ax.set_xlabel('False Positive Rate', fontsize=13)
    ax.set_ylabel('True Positive Rate', fontsize=13)
    ax.set_title('ROC Curve', fontsize=15, fontweight='bold', color='#a78bfa')
    ax.legend(fontsize=12)
    plt.tight_layout()
    path = os.path.join(GRAPHS_DIR, 'roc_curve.png')
    plt.savefig(path, dpi=120, bbox_inches='tight', facecolor=BG)
    plt.close()
    return 'graphs/roc_curve.png'

def generate_confusion_matrix(cm, labels=['Not Placed', 'Placed']):
    set_dark_style()
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='RdPu', ax=ax,
                xticklabels=labels, yticklabels=labels,
                linewidths=2, linecolor=BG, annot_kws={'size': 16, 'weight': 'bold'})
    ax.set_xlabel('Predicted', fontsize=13)
    ax.set_ylabel('Actual', fontsize=13)
    ax.set_title('Confusion Matrix', fontsize=15, fontweight='bold', color='#a78bfa')
    plt.tight_layout()
    path = os.path.join(GRAPHS_DIR, 'confusion_matrix.png')
    plt.savefig(path, dpi=120, bbox_inches='tight', facecolor=BG)
    plt.close()
    return 'graphs/confusion_matrix.png'

def generate_shap_bar(feature_names, shap_values, title="SHAP Feature Contributions"):
    set_dark_style()
    fig, ax = plt.subplots(figsize=(10, 7))
    colors = [PALETTE['placed'] if v > 0 else PALETTE['not_placed'] for v in shap_values]
    sorted_idx = np.argsort(np.abs(shap_values))
    ax.barh(
        [feature_names[i] for i in sorted_idx],
        [shap_values[i] for i in sorted_idx],
        color=[colors[i] for i in sorted_idx],
        edgecolor='none'
    )
    ax.axvline(0, color='#aaa', linewidth=1.5)
    ax.set_xlabel('SHAP Value (impact on prediction)', fontsize=13)
    ax.set_title(title, fontsize=15, fontweight='bold', color='#a78bfa')
    plt.tight_layout()
    path = os.path.join(GRAPHS_DIR, 'shap_plot.png')
    plt.savefig(path, dpi=120, bbox_inches='tight', facecolor=BG)
    plt.close()
    return 'graphs/shap_plot.png'

def generate_model_comparison(model_metrics):
    set_dark_style()
    fig, ax = plt.subplots(figsize=(11, 7))
    names = [m['name'] for m in model_metrics]
    metrics = ['accuracy', 'precision', 'recall', 'f1']
    metric_labels = ['Accuracy', 'Precision', 'Recall', 'F1']
    colors_list = [PALETTE['placed'], PALETTE['main'], PALETTE['accent'], PALETTE['not_placed']]
    x = np.arange(len(names))
    width = 0.2
    for i, (metric, label, color) in enumerate(zip(metrics, metric_labels, colors_list)):
        vals = [m[metric] * 100 for m in model_metrics]
        bars = ax.bar(x + i * width, vals, width, label=label, color=color, edgecolor='none', alpha=0.9)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{val:.1f}',
                    ha='center', va='bottom', fontsize=8, color=TEXT)
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(names, fontsize=12)
    ax.set_ylabel('Score (%)', fontsize=13)
    ax.set_title('Model Performance Comparison', fontsize=15, fontweight='bold', color='#a78bfa')
    ax.legend(fontsize=11)
    ax.set_ylim(0, 115)
    plt.tight_layout()
    path = os.path.join(GRAPHS_DIR, 'model_comparison.png')
    plt.savefig(path, dpi=120, bbox_inches='tight', facecolor=BG)
    plt.close()
    return 'graphs/model_comparison.png'
