"""
weakness_detector.py
--------------------
Analyzes a student profile dict and returns a structured list of weaknesses.
Each weakness has: field, label, severity ('CRITICAL'|'HIGH'|'MEDIUM'|'LOW'),
message, threshold, actual_value, and improvement_hint.
"""

# --------------------------------------------------------------------------- #
# Thresholds
# --------------------------------------------------------------------------- #
THRESHOLDS = {
    "cgpa":            {"critical": 5.5, "high": 6.5, "medium": 7.0},
    "aptitude_score":  {"critical": 40,  "high": 55,  "medium": 65},
    "soft_skills":     {"critical": 2.0, "high": 2.5, "medium": 3.0},
    "internships":     {"none": 0,       "low": 1},
    "projects":        {"none": 0,       "low": 2},
    "workshops":       {"none": 0,       "low": 1},
    "backlogs":        {"any": 1,        "high": 2},
    "ssc_marks":       {"critical": 50,  "high": 60},
    "hsc_marks":       {"critical": 50,  "high": 60},
}

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}


def _f(val, default=0):
    """Safe float cast."""
    try:
        return float(val)
    except (TypeError, ValueError):
        return float(default)


def detect_weaknesses(data: dict) -> list[dict]:
    """
    Parameters
    ----------
    data : dict
        Student profile. Keys match the prediction form fields:
        cgpa, aptitude_score, soft_skills, internships, projects,
        workshops (Workshops_Certifications), backlogs, ssc_marks,
        hsc_marks, extracurricular, placement_training.

    Returns
    -------
    list[dict]  – sorted by severity (CRITICAL first)
    """
    weaknesses = []

    cgpa           = _f(data.get("cgpa", 0))
    aptitude       = _f(data.get("aptitude_score", 0))
    soft_skills    = _f(data.get("soft_skills", 0))
    internships    = int(_f(data.get("internships", 0)))
    projects       = int(_f(data.get("projects", 0)))
    workshops      = int(_f(data.get("workshops", data.get("workshops_certifications", 0))))
    backlogs       = int(_f(data.get("backlogs", 0)))
    ssc            = _f(data.get("ssc_marks", 70))
    hsc            = _f(data.get("hsc_marks", 70))
    extracurr      = str(data.get("extracurricular", "No")).strip().lower()
    placement_tr   = str(data.get("placement_training", "No")).strip().lower()

    # ------------------------------------------------------------------ CGPA
    if cgpa < THRESHOLDS["cgpa"]["critical"]:
        weaknesses.append({
            "field": "low_cgpa",
            "label": "Very Low CGPA",
            "severity": "CRITICAL",
            "actual_value": cgpa,
            "threshold": THRESHOLDS["cgpa"]["critical"],
            "message": f"Your CGPA of {cgpa:.2f} is critically low. Most companies require ≥ 6.0, many require ≥ 7.0.",
            "improvement_hint": "Focus on academic recovery — target ≥ 7.0 in upcoming semesters.",
            "tag": "low_cgpa",
            "icon": "🎓"
        })
    elif cgpa < THRESHOLDS["cgpa"]["high"]:
        weaknesses.append({
            "field": "low_cgpa",
            "label": "Low CGPA",
            "severity": "HIGH",
            "actual_value": cgpa,
            "threshold": THRESHOLDS["cgpa"]["high"],
            "message": f"Your CGPA of {cgpa:.2f} may disqualify you from companies that require ≥ 6.5.",
            "improvement_hint": "Improve internal marks, attend extra classes, and clear backlogs.",
            "tag": "low_cgpa",
            "icon": "🎓"
        })
    elif cgpa < THRESHOLDS["cgpa"]["medium"]:
        weaknesses.append({
            "field": "low_cgpa",
            "label": "Below-Average CGPA",
            "severity": "MEDIUM",
            "actual_value": cgpa,
            "threshold": THRESHOLDS["cgpa"]["medium"],
            "message": f"CGPA {cgpa:.2f} is below average. Improving to 7.5+ significantly raises your chances.",
            "improvement_hint": "Score higher in remaining semesters and tackle pending backlogs.",
            "tag": "low_cgpa",
            "icon": "🎓"
        })

    # ----------------------------------------------------------------- Backlogs
    if backlogs >= THRESHOLDS["backlogs"]["high"]:
        weaknesses.append({
            "field": "backlogs",
            "label": "Multiple Backlogs",
            "severity": "CRITICAL",
            "actual_value": backlogs,
            "threshold": THRESHOLDS["backlogs"]["high"],
            "message": f"You have {backlogs} backlogs. Most top-tier companies immediately disqualify candidates with any backlog.",
            "improvement_hint": "Prioritize clearing all backlogs before placement season begins.",
            "tag": "backlogs",
            "icon": "⚠"
        })
