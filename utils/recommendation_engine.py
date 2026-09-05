"""
recommendation_engine.py
------------------------
Advanced targeted recommendation generator.
Returns prioritised recommendation dicts with action items,
category, resources, and estimated impact.
"""

from utils.weakness_detector import detect_weaknesses, get_weakness_tags

# --------------------------------------------------------------------------- #
# Recommendation templates keyed by weakness tag
# --------------------------------------------------------------------------- #
_RECS = {
    "low_cgpa": [
        {
            "title": "Academic Recovery Plan",
            "category": "Academics",
            "icon": "🎓",
            "description": (
                "A low CGPA is one of the most critical placement blockers. "
                "Many companies (TCS, Infosys, Cognizant, Wipro) enforce a hard "
                "7.0 CGPA cut-off. Focus on improving internal marks, clearing "
                "backlogs, and excelling in upcoming semesters."
            ),
            "action_items": [
                "Re-appear in backlogs / supplementary exams at the earliest opportunity",
                "Request internal mark recalculation or assignment re-submission",
                "Spend 3–4 hours/day on weak subjects using NPTEL lectures",
                "Form a study group and practice previous 5-year question papers",
                "Compensate with strong projects and certifications to offset low CGPA"
            ],
            "resources": [
                {"name": "NPTEL Courses", "url": "https://nptel.ac.in"},
                {"name": "GeeksforGeeks DSA Sheet", "url": "https://geeksforgeeks.org"},
                {"name": "PlaceIQ Skill Plan", "url": "/plan?skill=low_cgpa"}
            ],
            "estimated_impact": "High — directly expands number of eligible companies",
            "timeframe": "2–3 semesters"
        }
    ],
    "backlogs": [
        {
            "title": "Clear All Backlogs Immediately",
            "category": "Academics",
            "icon": "⚠",
            "description": (
                "Backlogs are placement killers. Over 90% of mass-recruiting companies "
                "in India (TCS, Infosys, Capgemini) disqualify candidates with any "
                "active backlog. This must be your #1 priority — no other improvement "
                "matters until your backlog count is zero."
            ),
            "action_items": [
                "List all backlog subjects and their next examination dates",
                "Gather 5 years of previous exam papers for each subject",
                "Spend 5–6 hours/day on backlog subjects — prioritize high-scoring chapters",
                "Talk to seniors who cleared the same paper and get their notes",
                "Register for supplementary exams immediately if registration is open"
            ],
            "resources": [
                {"name": "PlaceIQ Backlog Clearing Plan", "url": "/plan?skill=backlogs"},
                {"name": "Previous Year Papers — StudyChaCha", "url": "https://studychacha.com"}
            ],
            "estimated_impact": "Critical — zero backlogs required for 90% of companies",
            "timeframe": "1–2 semesters"
        }
    ],
    "low_aptitude": [
        {
            "title": "Aptitude Accelerator Program",
            "category": "Skills",
            "icon": "🧠",
            "description": (
                "Aptitude tests are the very first filter in mass placement drives. "
                "Companies like TCS (NQT), Infosys (InfyTQ), Capgemini, and Wipro "
                "use scores to shortlist candidates. Consistent daily practice of "
                "30–50 questions can raise your score by 20–30 points in 4–6 weeks."
            ),
            "action_items": [
                "Register at IndiaBix.com — solve 30 questions per day",
                "Solve PrepInsta company-specific mock papers (TCS, Infosys, Wipro)",
                "Focus on: Number System, Time & Work, Speed-Distance, Permutation",
                "Take 1 full TCS NQT mock test every weekend",
                "Use Pocket Aptitude or Oliveboard apps for daily practice"
            ],
            "resources": [
                {"name": "IndiaBix", "url": "https://indiabix.com"},
                {"name": "PrepInsta", "url": "https://prepinsta.com"},
                {"name": "TCS NQT Practice", "url": "https://learning.tcsionhub.in"},
                {"name": "PlaceIQ Aptitude Plan", "url": "/plan?skill=low_aptitude"}
            ],
            "estimated_impact": "High — aptitude score is 1st-round filter for most companies",
            "timeframe": "4–6 weeks"
        }
    ],
    "no_internships": [
        {
            "title": "Land Your First Internship",
            "category": "Experience",
            "icon": "💼",
            "description": (
                "Internship experience doubles your placement probability according to "
                "industry data. Even a 1-month remote or virtual internship counts. "
                "Internshala has 50,000+ active listings and many are beginner-friendly."
            ),
            "action_items": [
                "Create a profile on Internshala, LinkedIn, and Naukri immediately",
                "Apply to 10 internships per day using saved search filters",
                "Target: remote, 0-experience, any domain — get experience first",
                "Cold-email/message 5 alumni from your college working at firms you target",
                "Build a 1-page portfolio website to attach to applications"
            ],
            "resources": [
                {"name": "Internshala", "url": "https://internshala.com"},
                {"name": "LinkedIn Internships", "url": "https://linkedin.com/jobs"},
                {"name": "Unstop Opportunities", "url": "https://unstop.com"},
                {"name": "Internship Plan", "url": "/plan?skill=no_internships"}
            ],
            "estimated_impact": "High — doubles placement probability with even 1 internship",
            "timeframe": "2–4 weeks to first offer"
        }
    ],
    "low_projects": [
        {
            "title": "Build a Project Portfolio",
            "category": "Projects",
            "icon": "🛠",
            "description": (
                "Projects are your practical proof of skills. Technical interviewers "
                "will spend 60–70% of the interview discussing your projects. Having "
                "3+ well-documented projects on GitHub demonstrates that you can "
                "build things, not just study them."
            ),
            "action_items": [
                "Choose 3 projects from different domains (ML, Web, Automation)",
                "Create a GitHub account and commit code daily",
                "Each project must have: README, screenshots, live demo (or video)",
                "Add projects to LinkedIn 'Projects' section with 3 bullet points each",
                "Practice explaining each project in 2 minutes: What, Why, How, Result"
            ],
            "resources": [
                {"name": "PlaceIQ Project Ideas", "url": "/projects"},
                {"name": "GitHub Student Pack", "url": "https://education.github.com"},
                {"name": "Free hosting: Render.com", "url": "https://render.com"},
                {"name": "Project Portfolio Plan", "url": "/plan?skill=low_projects"}
            ],
            "estimated_impact": "High — projects directly asked in 100% of technical interviews",
            "timeframe": "4–6 weeks (3 projects)"
        }
    ],
    "low_certifications": [
        {
            "title": "Earn Recognized Certifications",
            "category": "Certifications",
            "icon": "📜",
            "description": (
                "Certifications from NPTEL, Coursera, and Google fill resume gaps, "
                "demonstrate self-driven learning, and are searchable by recruiters "
                "on LinkedIn. A good cert takes 4–8 weeks and is free or near-free."
            ),
            "action_items": [
                "Register for 1 NPTEL course in your domain this week (free audit)",
                "Complete a Kaggle Python or ML certification (free, 3–5 hours)",
                "Enrol in Google Data Analytics Certificate on Coursera (financial aid available)",
                "Upload all certificates to LinkedIn's 'Licenses & Certifications' section",
                "Aim for 2–3 strong certs from recognised platforms by placement season"
            ],
            "resources": [
                {"name": "NPTEL", "url": "https://nptel.ac.in"},
                {"name": "Kaggle Learn (Free)", "url": "https://kaggle.com/learn"},
                {"name": "Coursera Financial Aid", "url": "https://coursera.org"},
                {"name": "PlaceIQ Certifications", "url": "/suggestions"}
            ],
            "estimated_impact": "Medium — certificates differentiate candidates with similar CGPAs",
            "timeframe": "4–8 weeks per certification"
        }
    ],
    "low_soft_skills": [
        {
          "title": "Communication & Interview Skills Bootcamp",
          "category": "Soft Skills",
          "icon": "🗣",
          "description": (
              "Soft skills — communication, confidence, and teamwork — determine "
              "success in HR interviews and group discussions. Many technically "
              "strong students fail at this stage. 30 minutes of daily practice "
              "makes a measurable difference in 3–4 weeks."
          ),
          "action_items": [
              "Record yourself for 2 minutes daily — review for clarity and confidence",
              "Practice 20 common HR questions using the STAR method",
              "Participate in mock GD sessions (online groups, college clubs)",
              "Read English newspaper for 15 minutes daily — builds vocabulary",
              "Learn professional email writing — send 3 mock emails per day"
          ],
          "resources": [
              {"name": "Toastmasters Online", "url": "https://toastmasters.org"},
              {"name": "NPTEL Soft Skills", "url": "https://nptel.ac.in"},
              {"name": "InterviewBuddy Mock Interviews", "url": "https://interviewbuddy.net"},
              {"name": "Soft Skills Plan", "url": "/plan?skill=low_soft_skills"}
          ],
          "estimated_impact": "High — HR round elimination is top reason students don't get placed",
          "timeframe": "3–4 weeks"
        }
    ],
    "no_extracurriculars": [
        {
            "title": "Build Leadership Through Activities",
            "category": "Profile",
            "icon": "🏅",
            "description": (
                "Extracurricular activities demonstrate teamwork, leadership, and "
                "communication — qualities companies look for beyond academics. "
                "Hackathons in particular are excellent for technical resume building."
            ),
            "action_items": [
                "Register for 1 hackathon on Devfolio or Unstop this month",
                "Join a technical club in your college (coding, robotics, debate)",
                "Volunteer for college events or inter-college competitions",
                "Participate in Smart India Hackathon (SIH) — national level exposure",
                "Add any existing activities (NCC, NSS, sports) to your resume"
            ],
            "resources": [
                {"name": "Devfolio Hackathons", "url": "https://devfolio.co"},
                {"name": "Unstop Competitions", "url": "https://unstop.com"},
                {"name": "Smart India Hackathon", "url": "https://sih.gov.in"}
            ],
            "estimated_impact": "Medium — adds depth to resume and shows cultural fit",
            "timeframe": "Ongoing"
        }
    ],
    "no_training": [
        {
            "title": "Attend Placement Training",
            "category": "Preparation",
            "icon": "🎯",
            "description": (
                "Placement training bridges the gap between college academics and "
                "industry expectations. It typically covers aptitude, GD, technical "
                "interviews, and HR rounds. Missing this is a significant disadvantage."
            ),
            "action_items": [
                "Register for your college TPO's pre-placement training NOW",
                "Enrol on Internshala Training (Placement Bootcamp)",
                "Join free sessions by career coaches on YouTube or LinkedIn Live",
                "Do 1 mock technical interview per week using Pramp.com (free)",
                "Prepare a 30-second and 2-minute 'Tell me about yourself' answer"
            ],
            "resources": [
                {"name": "Internshala Placement Bootcamp", "url": "https://internshala.com/trainings"},
                {"name": "Pramp Mock Interviews", "url": "https://pramp.com"},
                {"name": "Placement Preparation Guide — GeeksforGeeks", "url": "https://geeksforgeeks.org/company-preparation"}
            ],
            "estimated_impact": "Medium — improves interview conversion rate significantly",
            "timeframe": "2–4 weeks"
        }
    ]
}

PRIORITY_MAP = {"CRITICAL": "CRITICAL", "HIGH": "HIGH", "MEDIUM": "MEDIUM", "LOW": "LOW"}


def generate_advanced_recommendations(
    data: dict,
    probability: float,
    weaknesses: list[dict] | None = None
) -> list[dict]:
    """
    Generate targeted recommendations based on detected weaknesses.

    Parameters
    ----------
    data        : student profile dict
    probability : placement probability (0–100)
    weaknesses  : pre-computed weakness list (or None to auto-detect)

    Returns
    -------
    list[dict]  – ordered by priority
    """
    if weaknesses is None:
        weaknesses = detect_weaknesses(data)

    recommendations = []
    seen_categories = set()

    for w in weaknesses:
        tag = w.get("tag", w.get("field", ""))
        severity = w["severity"]

        if tag in _RECS:
            for rec_template in _RECS[tag]:
                rec = dict(rec_template)
                rec["priority"] = PRIORITY_MAP.get(severity, "MEDIUM")
                rec["weakness_ref"] = w["label"]
                uid = rec["title"]
                if uid not in seen_categories:
                    seen_categories.add(uid)
                    recommendations.append(rec)

    # Add probability-based general recs
    if probability < 40 and len(recommendations) < 5:
        recommendations.append({
            "title": "Focus on Quick Wins First",
            "category": "Strategy",
            "icon": "⚡",
            "priority": "HIGH",
            "description": (
                "With a placement probability below 40%, focus on quick-impact changes: "
                "clear backlogs, add 1 project, and practice aptitude daily. This can "
                "shift your probability into the 50–70% range within 6–8 weeks."
            ),
            "action_items": [
                "Address CRITICAL weaknesses first (backlogs, CGPA, aptitude)",
                "Build 1 portfolio project this week",
                "Apply to any 1 internship today on Internshala",
                "Practice 30 aptitude questions per day on IndiaBix"
            ],
            "resources": [{"name": "PlaceIQ Improvement Hub", "url": "/improvement"}],
            "estimated_impact": "High — compound effect of fixing multiple weak areas",
            "timeframe": "6–8 weeks"
        })
    elif probability >= 70:
        recommendations.append({
            "title": "Polish & Differentiate",
            "category": "Strategy",
            "icon": "✦",
            "priority": "LOW",
            "description": (
                "Your profile is already strong! Focus on differentiation: "
                "advanced certifications, an impactful capstone project, "
                "and practising for product company interviews (DSA + System Design)."
            ),
            "action_items": [
                "Solve 3 LeetCode problems daily (Easy → Medium → Hard)",
                "Attempt 1 Kaggle competition for real-world ML experience",
                "Write 2 technical articles on Medium or LinkedIn to build personal brand",
                "Apply to top-tier companies and off-campus openings"
            ],
            "resources": [
                {"name": "LeetCode", "url": "https://leetcode.com"},
                {"name": "Kaggle Competitions", "url": "https://kaggle.com/competitions"}
            ],
            "estimated_impact": "Medium — fine-tuning an already strong profile",
            "timeframe": "4–6 weeks"
        })

    return recommendations


def get_quick_wins(weaknesses: list[dict]) -> list[dict]:
    """Return top 3 fastest-impact actions from weaknesses."""
    quick = []
    for w in weaknesses[:3]:
        tag = w.get("tag", "")
        if tag in _RECS:
            rec = _RECS[tag][0]
            quick.append({
                "title": rec["title"],
                "icon": rec["icon"],
                "action": rec["action_items"][0] if rec["action_items"] else "Take action now",
                "severity": w["severity"]
            })
    return quick
