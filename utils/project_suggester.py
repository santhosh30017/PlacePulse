"""
project_suggester.py
--------------------
Suggests project ideas based on detected weakness tags and student stream.
Loads from data/project_suggestions.json.
"""

import os
import json

_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "project_suggestions.json"
)

_STREAM_CATEGORY_MAP = {
    "computer science":      ["machine_learning", "web_development", "data_science", "python_automation"],
    "information technology":["web_development", "machine_learning", "python_automation", "mini_projects"],
    "electronics":           ["python_automation", "machine_learning", "mini_projects", "data_science"],
    "mechanical":            ["python_automation", "data_science", "mini_projects", "web_development"],
    "civil":                 ["data_science", "python_automation", "mini_projects", "web_development"],
}

_WEAKNESS_CATEGORY_MAP = {
    "low_aptitude":       ["machine_learning", "data_science", "python_automation"],
    "low_projects":       ["mini_projects", "python_automation", "machine_learning"],
    "no_internships":     ["mini_projects", "web_development", "python_automation"],
    "low_cgpa":           ["mini_projects", "data_science", "python_automation"],
    "low_certifications": ["machine_learning", "data_science"],
    "low_soft_skills":    ["web_development", "mini_projects"],
    "backlogs":           ["mini_projects", "python_automation"],
    "no_extracurriculars":["machine_learning", "web_development"],
    "no_training":        ["mini_projects", "python_automation"],
}


def _load_data() -> dict:
    if os.path.exists(_DATA_PATH):
        with open(_DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"categories": {}}


def suggest_projects(
    weakness_tags: list[str],
    stream: str = "computer science",
    max_results: int = 6
) -> list[dict]:
    """
    Return up to max_results project suggestions relevant to the student.

    Parameters
    ----------
    weakness_tags : list of tag strings from get_weakness_tags()
    stream        : student's engineering stream (lowercase)
    max_results   : maximum number of projects to return

    Returns
    -------
    list[dict] – each dict has all project fields + 'category_label' & 'category_icon'
    """
    data = _load_data()
    categories = data.get("categories", {})
    stream_lower = stream.lower().strip()

    # Build priority category order
    priority_cats = []
    for tag in weakness_tags:
        for cat in _WEAKNESS_CATEGORY_MAP.get(tag, []):
            if cat not in priority_cats:
                priority_cats.append(cat)

    # Add stream-based categories
    for cat in _STREAM_CATEGORY_MAP.get(stream_lower, _STREAM_CATEGORY_MAP["computer science"]):
        if cat not in priority_cats:
            priority_cats.append(cat)

    # Add any remaining categories
    for cat in categories:
        if cat not in priority_cats:
            priority_cats.append(cat)

    results = []
    seen_ids = set()

    for cat_key in priority_cats:
        if cat_key not in categories:
            continue
        cat = categories[cat_key]
        for project in cat.get("projects", []):
            pid = project.get("id", project.get("title"))
            if pid not in seen_ids:
                seen_ids.add(pid)
                enriched = dict(project)
                enriched["category_key"] = cat_key
                enriched["category_label"] = cat.get("label", cat_key)
                enriched["category_icon"] = cat.get("icon", "🛠")
                results.append(enriched)
            if len(results) >= max_results:
                break
        if len(results) >= max_results:
            break

    return results


def get_all_categories() -> list[dict]:
    """Return all project categories with metadata (for browsing page)."""
    data = _load_data()
    cats = []
    for key, val in data.get("categories", {}).items():
        cats.append({
            "key": key,
            "label": val.get("label", key),
            "icon": val.get("icon", "🛠"),
            "count": len(val.get("projects", [])),
            "projects": val.get("projects", [])
        })
    return cats


def get_projects_by_category(category_key: str) -> list[dict]:
    """Return all projects in a specific category."""
    data = _load_data()
    cat = data.get("categories", {}).get(category_key, {})
    projects = cat.get("projects", [])
    for p in projects:
        p["category_label"] = cat.get("label", category_key)
        p["category_icon"]  = cat.get("icon", "🛠")
    return projects


def get_difficulty_color(difficulty: str) -> str:
    colors = {
        "Beginner":     "var(--emerald)",
        "Intermediate": "var(--primary)",
        "Advanced":     "var(--rose)"
    }
    return colors.get(difficulty, "var(--text2)")
