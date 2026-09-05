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
