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
