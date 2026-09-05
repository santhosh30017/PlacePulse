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
    elif backlogs >= THRESHOLDS["backlogs"]["any"]:
        weaknesses.append({
            "field": "backlogs",
            "label": "Active Backlog",
            "severity": "HIGH",
            "actual_value": backlogs,
            "threshold": THRESHOLDS["backlogs"]["any"],
            "message": f"You have {backlogs} backlog. Even 1 backlog eliminates you from many companies.",
            "improvement_hint": "Clear this backlog at the earliest opportunity — it's blocking placements.",
            "tag": "backlogs",
            "icon": "⚠"
        })

    # ----------------------------------------------------------------- Aptitude
    if aptitude < THRESHOLDS["aptitude_score"]["critical"]:
        weaknesses.append({
            "field": "low_aptitude",
            "label": "Very Low Aptitude Score",
            "severity": "CRITICAL",
            "actual_value": aptitude,
            "threshold": THRESHOLDS["aptitude_score"]["critical"],
            "message": f"Aptitude score of {aptitude:.0f}/100 is very low. Companies like TCS, Infosys, Wipro use aptitude as the first filter.",
            "improvement_hint": "Start practicing quantitative, LR, and verbal aptitude daily.",
            "tag": "low_aptitude",
            "icon": "🧠"
        })
    elif aptitude < THRESHOLDS["aptitude_score"]["high"]:
        weaknesses.append({
            "field": "low_aptitude",
            "label": "Low Aptitude Score",
            "severity": "HIGH",
            "actual_value": aptitude,
            "threshold": THRESHOLDS["aptitude_score"]["high"],
            "message": f"Aptitude score of {aptitude:.0f}/100 needs improvement. Target 70+ to pass most company filters.",
            "improvement_hint": "Use IndiaBix, PrepInsta, and practice 30 questions per day.",
            "tag": "low_aptitude",
            "icon": "🧠"
        })
    elif aptitude < THRESHOLDS["aptitude_score"]["medium"]:
        weaknesses.append({
            "field": "low_aptitude",
            "label": "Below-Average Aptitude",
            "severity": "MEDIUM",
            "actual_value": aptitude,
            "threshold": THRESHOLDS["aptitude_score"]["medium"],
            "message": f"Aptitude score {aptitude:.0f}/100 is slightly below average. Aim for 70+ for better shortlisting.",
            "improvement_hint": "Focus on time-speed-distance, number systems, and logical reasoning.",
            "tag": "low_aptitude",
            "icon": "🧠"
        })

    # ----------------------------------------------------------------- Internships
    if internships == 0:
        weaknesses.append({
            "field": "no_internships",
            "label": "No Internship Experience",
            "severity": "HIGH",
            "actual_value": 0,
            "threshold": 1,
            "message": "You have no internship experience. Recruiters strongly prefer candidates with at least 1 internship.",
            "improvement_hint": "Apply on Internshala for remote internships — even virtual ones count.",
            "tag": "no_internships",
            "icon": "💼"
        })
    elif internships == 1:
        weaknesses.append({
            "field": "no_internships",
            "label": "Limited Internship Experience",
            "severity": "LOW",
            "actual_value": 1,
            "threshold": 2,
            "message": "Only 1 internship. 2+ internships strongly differentiate candidates at the interview stage.",
            "improvement_hint": "Apply for a second internship or a meaningful project-based freelance role.",
            "tag": "no_internships",
            "icon": "💼"
        })

    # ----------------------------------------------------------------- Projects
    if projects == 0:
        weaknesses.append({
            "field": "low_projects",
            "label": "No Projects",
            "severity": "HIGH",
            "actual_value": 0,
            "threshold": 2,
            "message": "You have no projects. Projects prove practical skills and are essential for technical interviews.",
            "improvement_hint": "Start with a beginner project this week — see the Projects page for ideas.",
            "tag": "low_projects",
            "icon": "🛠"
        })
    elif projects < THRESHOLDS["projects"]["low"]:
        weaknesses.append({
            "field": "low_projects",
            "label": "Insufficient Projects",
            "severity": "MEDIUM",
            "actual_value": projects,
            "threshold": THRESHOLDS["projects"]["low"],
            "message": f"Only {projects} project(s). Aim for 3+ projects to stand out in technical rounds.",
            "improvement_hint": "Build 1 domain-specific project and upload it to GitHub with a good README.",
            "tag": "low_projects",
            "icon": "🛠"
        })

    # ----------------------------------------------------------------- Workshops / Certifications
    if workshops == 0:
        weaknesses.append({
            "field": "low_certifications",
            "label": "No Certifications",
            "severity": "MEDIUM",
            "actual_value": 0,
            "threshold": 1,
            "message": "No workshops or certifications. Certifications show self-driven learning and fill resume gaps.",
            "improvement_hint": "Complete 1 free Kaggle or NPTEL course this month to get a verifiable certificate.",
