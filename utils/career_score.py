"""
career_score.py
---------------
Computes an Employability Score (0–100) and a dimension-wise breakdown
for a student profile. The score captures overall job-readiness
independently from the placement probability (which is model-driven).
"""

# --------------------------------------------------------------------------- #
# Dimension weights (must sum to 1.0)
# --------------------------------------------------------------------------- #
DIMENSION_WEIGHTS = {
    "academics":    0.28,   # CGPA + SSC + HSC
    "experience":   0.22,   # Internships + Projects
    "aptitude":     0.18,   # Aptitude test score
    "skills":       0.15,   # Soft skills + Training
    "activities":   0.10,   # Certifications + Extracurriculars
    "discipline":   0.07,   # Backlogs (penalty)
}

# Interpretation bands
BANDS = [
    (85, 100, "Excellent",    "var(--emerald)", "🏆"),
    (70,  84, "Strong",       "var(--sky)",     "✦"),
    (55,  69, "Moderate",     "var(--primary)", "◎"),
    (40,  54, "Needs Work",   "var(--yellow)",  "⚠"),
    (0,   39, "At Risk",      "var(--rose)",    "↘"),
]


def _clamp(val: float, mn: float = 0.0, mx: float = 100.0) -> float:
    return max(mn, min(mx, val))


def _f(val, default=0.0) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return float(default)


def _academics_score(data: dict) -> float:
    """0–100 academic subscore."""
    cgpa     = _clamp(_f(data.get("cgpa", 0)) / 10.0 * 100, 0, 100)
    ssc      = _clamp(_f(data.get("ssc_marks", 70)), 0, 100)
    hsc      = _clamp(_f(data.get("hsc_marks", 70)), 0, 100)
    return round(cgpa * 0.60 + ssc * 0.20 + hsc * 0.20, 2)


def _experience_score(data: dict) -> float:
    """0–100 experience subscore."""
    internships = _clamp(_f(data.get("internships", 0)), 0, 3)
    projects    = _clamp(_f(data.get("projects", 0)), 0, 5)
    intern_s = (internships / 3.0) * 100
    proj_s   = (projects   / 5.0) * 100
    return round(intern_s * 0.55 + proj_s * 0.45, 2)


def _aptitude_score_dim(data: dict) -> float:
    """0–100 aptitude subscore (same scale as the input)."""
    return _clamp(_f(data.get("aptitude_score", 0)), 0, 100)


def _skills_score(data: dict) -> float:
    """0–100 skills subscore."""
    soft   = _clamp(_f(data.get("soft_skills", 0)) / 5.0 * 100, 0, 100)
    train  = 100.0 if str(data.get("placement_training", "No")).strip().lower() in ("yes","1","true") else 0.0
    return round(soft * 0.70 + train * 0.30, 2)


def _activities_score(data: dict) -> float:
    """0–100 activities subscore."""
    workshops = _clamp(_f(data.get("workshops", data.get("workshops_certifications", 0))), 0, 4)
    extra     = 100.0 if str(data.get("extracurricular", "No")).strip().lower() in ("yes","1","true") else 0.0
    cert_s    = (workshops / 4.0) * 100
    return round(cert_s * 0.55 + extra * 0.45, 2)


def _discipline_score(data: dict) -> float:
    """0–100 discipline subscore — penalized by backlogs."""
    backlogs = int(_f(data.get("backlogs", 0)))
    if backlogs == 0:
        return 100.0
    elif backlogs == 1:
        return 50.0
    elif backlogs == 2:
        return 20.0
    else:
        return 0.0


def _get_band(score: float) -> dict:
    for low, high, label, color, icon in BANDS:
        if low <= score <= high:
            return {"label": label, "color": color, "icon": icon}
    return {"label": "Unknown", "color": "var(--text2)", "icon": "◎"}


def compute_employability_score(data: dict) -> dict:
    """
    Compute a full Employability Score for the student profile.

    Parameters
    ----------
    data : student profile dict (same keys as prediction form)

    Returns
    -------
    dict with keys:
        score           : int 0–100
        band            : dict(label, color, icon)
        dimensions      : dict of subscore dicts
        interpretation  : str explanation
        improvement_tip : str top tip
    """
    dims = {
        "academics":  _academics_score(data),
        "experience": _experience_score(data),
        "aptitude":   _aptitude_score_dim(data),
        "skills":     _skills_score(data),
        "activities": _activities_score(data),
        "discipline": _discipline_score(data),
    }

    weighted = sum(dims[d] * DIMENSION_WEIGHTS[d] for d in dims)
    total = round(_clamp(weighted), 1)
    band  = _get_band(total)

    # Build dimension display
    dim_labels = {
        "academics":  ("Academics",            "🎓"),
        "experience": ("Experience",           "💼"),
        "aptitude":   ("Aptitude",             "🧠"),
        "skills":     ("Communication Skills", "🗣"),
        "activities": ("Certifications",       "📜"),
        "discipline": ("Academic Discipline",  "📖"),
    }

    dimension_display = {}
    for key, val in dims.items():
        label, icon = dim_labels[key]
        b = _get_band(val)
        dimension_display[key] = {
            "label":   label,
            "icon":    icon,
            "score":   val,
            "weight":  int(DIMENSION_WEIGHTS[key] * 100),
            "band":    b["label"],
            "color":   b["color"],
        }

    # Find weakest dimension for tip
    weakest_key = min(dims, key=dims.get)
    weakest_label = dim_labels[weakest_key][0]

    interpretation = (
        f"Your Employability Score is {total}/100 — {band['label']}. "
        f"Your strongest area is {dim_labels[max(dims, key=dims.get)][0]} "
        f"and your weakest is {weakest_label}."
    )

    tips = {
        "academics":  "Improve your CGPA through consistent study and clearing backlogs.",
        "experience": "Build projects and apply for internships on Internshala.",
        "aptitude":   "Practice 30 aptitude questions daily on IndiaBix or PrepInsta.",
        "skills":     "Practice daily spoken English and mock HR interviews.",
        "activities": "Complete a free Kaggle or NPTEL certification this month.",
        "discipline": "Clear all backlogs immediately — this is the #1 placement blocker.",
    }

    return {
        "score":           total,
        "band":            band,
        "dimensions":      dimension_display,
        "interpretation":  interpretation,
        "improvement_tip": tips.get(weakest_key, "Focus on your weakest dimension."),
        "weakest_dim":     weakest_key,
    }


def score_to_color(score: float) -> str:
    """Return CSS color variable for a 0–100 score."""
    if score >= 75:  return "var(--emerald)"
    if score >= 55:  return "var(--primary)"
    if score >= 40:  return "var(--yellow)"
    return "var(--rose)"
