"""
skill_plan.py
-------------
Generates a structured weekly skill improvement plan based on detected weaknesses.
Loads plan templates from data/skill_plans.json.
"""

import os
import json

_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "skill_plans.json"
)

# Map weakness tags → plan keys in skill_plans.json
_TAG_TO_PLAN = {
    "low_cgpa":           "low_cgpa",
    "low_aptitude":       "low_aptitude",
    "no_internships":     "no_internships",
    "low_soft_skills":    "low_soft_skills",
    "backlogs":           "backlogs",
    "low_projects":       "low_projects",
}


def _load_plans() -> dict:
    if os.path.exists(_DATA_PATH):
        with open(_DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get("plans", {})
    return {}


def get_plan(plan_key: str) -> dict | None:
    """Return a single plan dict by key, or None if not found."""
    plans = _load_plans()
    return plans.get(plan_key)


def generate_skill_plan(weakness_tags: list[str], max_plans: int = 2) -> list[dict]:
    """
    Generate up to max_plans improvement plans based on weakness tags.
    Prioritizes plans in order of the weakness severity (tags already sorted).

    Parameters
    ----------
    weakness_tags : list[str] from get_weakness_tags(), already severity-ordered
    max_plans     : max number of plans to return (default 2 for UI clarity)

    Returns
    -------
    list[dict] – each dict is a full plan with title, icon, target, weeks list
    """
    plans = _load_plans()
    result = []
    seen = set()

    for tag in weakness_tags:
        plan_key = _TAG_TO_PLAN.get(tag)
        if plan_key and plan_key not in seen and plan_key in plans:
            seen.add(plan_key)
            plan = dict(plans[plan_key])
            plan["plan_key"] = plan_key
            result.append(plan)
        if len(result) >= max_plans:
            break

    return result


def get_all_plan_keys() -> list[dict]:
    """Return all available plan keys with metadata (for the /plan page listing)."""
    plans = _load_plans()
    return [
        {
            "key": k,
            "title": v.get("title", k),
            "icon": v.get("icon", "📋"),
            "target": v.get("target", ""),
            "total_weeks": v.get("total_weeks", 4)
        }
        for k, v in plans.items()
    ]


def generate_combined_timeline(plans: list[dict]) -> list[dict]:
    """
    Merge multiple plans into a single deduplicated weekly timeline.
    Useful for displaying a combined roadmap on the /plan page.

    Returns list of week dicts with combined tasks from all plans.
    """
    max_weeks = max((p.get("total_weeks", 4) for p in plans), default=4)
    timeline = []

    for week_num in range(1, max_weeks + 1):
        week_entry = {
            "week": week_num,
            "tasks": [],
            "themes": [],
            "focuses": []
        }
        for plan in plans:
            weeks = plan.get("weeks", [])
            matching = [w for w in weeks if w.get("week") == week_num]
            for w in matching:
                week_entry["themes"].append(f"{plan.get('icon','📋')} {w.get('theme','')}")
                week_entry["focuses"].append(w.get("focus", ""))
                week_entry["tasks"].extend(w.get("tasks", []))
        if week_entry["tasks"]:
            timeline.append(week_entry)

    return timeline
