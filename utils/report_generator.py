"""
report_generator.py
-------------------
Generates a full student placement report as a formatted TXT string.
Optionally produces a PDF if reportlab is installed.
All output is self-contained — no external network calls.
"""

import os
from datetime import datetime


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _line(char: str = "─", width: int = 70) -> str:
    return char * width


def _center(text: str, width: int = 70) -> str:
    return text.center(width)


def _section(title: str) -> str:
    return f"\n{_line()}\n  {title.upper()}\n{_line()}\n"


def _wrap(text: str, indent: int = 4, width: int = 66) -> str:
    """Simple word-wrap."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        if len(current) + len(word) + 1 <= width:
            current = (current + " " + word).strip()
        else:
            lines.append(" " * indent + current)
            current = word
    if current:
        lines.append(" " * indent + current)
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# TXT Report
# --------------------------------------------------------------------------- #
def generate_txt_report(result: dict) -> str:
    """
    Generate a plain-text report from a prediction result dict.

    Parameters
    ----------
    result : dict — must contain keys returned by the prediction API:
             student_name, probability, risk_score, prediction, category,
             model_used, recommendations, feature_importance,
             weaknesses (optional), career_score (optional).

    Returns
    -------
    str — formatted multi-line report
    """
    now = datetime.now().strftime("%d %B %Y  |  %I:%M %p")
    name        = result.get("student_name", "Unknown Student")
    prob        = result.get("probability", 0)
    risk        = result.get("risk_score", 0)
    prediction  = result.get("prediction", "Unknown")
    category    = result.get("category", "")
    model_used  = result.get("model_used", "")
    recs        = result.get("recommendations", [])
    fi          = result.get("feature_importance", {})
    weaknesses  = result.get("weaknesses", [])
    career      = result.get("career_score", {})
    emp_score   = career.get("score", "N/A") if career else "N/A"
    emp_band    = career.get("band", {}).get("label", "") if career else ""

    lines = []

    # ---- Header ----
    lines += [
        _line("═"),
        _center("PLACEIQ  —  AI PLACEMENT INTELLIGENCE SYSTEM"),
        _center("STUDENT PLACEMENT REPORT"),
        _center(f"Generated on: {now}"),
        _line("═"),
        "",
    ]

    # ---- Student Summary ----
    lines += [
        _section("Student Summary"),
        f"  Name            : {name}",
        f"  Prediction      : {prediction}  ({category})",
        f"  Probability     : {prob}%",
        f"  Risk Score      : {risk} / 100",
        f"  Employ. Score   : {emp_score} / 100  [{emp_band}]",
        f"  Model Used      : {model_used}",
        "",
    ]

    # ---- AI Executive Summary ----
    ai_summary = result.get("ai_summary")
    if ai_summary:
        lines += [
            _section("AI Executive Summary"),
            _wrap(ai_summary, indent=2),
            "",
        ]

    # ---- Profile Inputs ----
    profile_keys = [
        ("cgpa",             "CGPA"),
        ("ssc_marks",        "SSC Marks (%)"),
        ("hsc_marks",        "HSC Marks (%)"),
        ("internships",      "Internships"),
        ("projects",         "Projects"),
        ("workshops",        "Workshops/Certs"),
        ("aptitude_score",   "Aptitude Score"),
        ("soft_skills",      "Soft Skills Rating"),
        ("backlogs",         "Backlogs"),
    ]
    lines += [_section("Profile Data")]
    for key, label in profile_keys:
        val = result.get(key, result.get("input_data", {}).get(key, "—"))
        lines.append(f"  {label:<22}: {val}")
    lines.append("")

    # ---- Weakness Analysis ----
    if weaknesses:
        lines += [_section("Weakness Analysis")]
        for i, w in enumerate(weaknesses, 1):
            sev = w.get("severity", "INFO")
            lbl = w.get("label", "")
            msg = w.get("message", "")
            lines.append(f"  {i}. [{sev}] {lbl}")
            lines.append(_wrap(msg, indent=6))
            lines.append("")
    else:
        lines += [_section("Weakness Analysis"), "  No critical weaknesses detected.\n"]

    # ---- Employability Score Breakdown ----
    if career and career.get("dimensions"):
        lines += [_section("Employability Score Breakdown")]
        dims = career["dimensions"]
        for key, dim in dims.items():
            bar_filled = int(dim["score"] / 10)
            bar = "█" * bar_filled + "░" * (10 - bar_filled)
            lines.append(
                f"  {dim['label']:<24} [{bar}]  {dim['score']:.1f}/100  (weight: {dim['weight']}%)"
            )
        lines.append(f"\n  TOTAL EMPLOYABILITY SCORE: {emp_score}/100  —  {emp_band}")
        tip = career.get("improvement_tip", "")
        if tip:
            lines.append(f"\n  Top Tip: {tip}")
        lines.append("")

    # ---- Feature Importance ----
    if fi:
        lines += [_section("Top Feature Contributions")]
        sorted_fi = sorted(fi.items(), key=lambda x: x[1], reverse=True)[:8]
        max_val = sorted_fi[0][1] if sorted_fi else 1
        for feat, val in sorted_fi:
            pct = round(val * 100, 1)
            bar_len = int((val / max_val) * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            lines.append(f"  {feat.replace('_',' '):<28} [{bar}]  {pct}%")
        lines.append("")

    # ---- Recommendations ----
    if recs:
        lines += [_section("AI-Powered Recommendations")]
        for i, rec in enumerate(recs, 1):
            priority = rec.get("priority", "INFO")
            title    = rec.get("title", "")
            desc     = rec.get("description", "")
            actions  = rec.get("action_items", [])
            tf       = rec.get("timeframe", "")
            impact   = rec.get("estimated_impact", "")
            lines.append(f"  {i}. [{priority}] {title}")
            lines.append(_wrap(desc, indent=6))
            if actions:
                lines.append("      Steps:")
                for idx, act in enumerate(actions[:4], 1):
                    lines.append(f"        {idx}. {act}")
            if tf:    lines.append(f"      Timeframe : {tf}")
            if impact: lines.append(f"      Impact    : {impact}")
            lines.append("")

    # ---- Footer ----
    lines += [
        _line("═"),
        _center("This report was generated by PlaceIQ AI System"),
        _center("For improvements, visit: http://localhost:5050/improvement"),
        _line("═"),
        "",
    ]

    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# PDF Report (optional — requires reportlab)
# --------------------------------------------------------------------------- #
def generate_pdf_report(result: dict, output_path: str | None = None) -> bytes | None:
    """
    Generate a PDF report. Returns PDF bytes if successful, None otherwise.
    Requires: pip install reportlab

    Parameters
    ----------
    result      : same dict as generate_txt_report
    output_path : if given, saves to file and returns None;
                  if None, returns PDF bytes directly

    Returns
    -------
    bytes | None
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        import io

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm)
        styles = getSampleStyleSheet()
        story  = []

        AMBER  = colors.HexColor("#f59e0b")
        ROSE   = colors.HexColor("#fb7185")
        EMRALD = colors.HexColor("#34d399")
        DARK   = colors.HexColor("#1e1e1e")
        LIGHT  = colors.HexColor("#e5e0d5")

        h1 = ParagraphStyle("h1", fontSize=18, textColor=AMBER, spaceAfter=4, fontName="Helvetica-Bold")
        h2 = ParagraphStyle("h2", fontSize=13, textColor=AMBER, spaceAfter=4, fontName="Helvetica-Bold")
        body = ParagraphStyle("body", fontSize=10, textColor=DARK, leading=16)
        small = ParagraphStyle("small", fontSize=9, textColor=colors.grey)

        now  = datetime.now().strftime("%d %B %Y · %I:%M %p")
        name = result.get("student_name", "Unknown")
        prob = result.get("probability", 0)
        pred = result.get("prediction", "Unknown")
        cat  = result.get("category", "")
        risk = result.get("risk_score", 0)
        emp  = result.get("career_score", {}).get("score", "N/A") if result.get("career_score") else "N/A"

        story.append(Paragraph("PlaceIQ — AI Placement Intelligence Report", h1))
        story.append(Paragraph(f"Generated: {now}", small))
        story.append(HRFlowable(width="100%", thickness=1, color=AMBER))
        story.append(Spacer(1, 0.3*cm))

        # Summary table
        summary_data = [
            ["Field", "Value"],
            ["Student Name", name],
            ["Prediction", f"{pred} ({cat})"],
            ["Probability", f"{prob}%"],
            ["Risk Score", f"{risk}/100"],
            ["Employability Score", f"{emp}/100"],
            ["Model Used", result.get("model_used", "—")],
        ]
        t = Table(summary_data, colWidths=[6*cm, 10*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), AMBER),
            ("TEXTCOLOR",  (0,0), (-1,0), colors.black),
            ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",   (0,0), (-1,-1), 10),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f9f6f0")]),
            ("GRID",       (0,0), (-1,-1), 0.5, colors.lightgrey),
            ("PADDING",    (0,0), (-1,-1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.5*cm))

        # Weaknesses
        weaknesses = result.get("weaknesses", [])
        if weaknesses:
            story.append(Paragraph("Weakness Analysis", h2))
            for w in weaknesses:
                sev_color = {"CRITICAL": ROSE, "HIGH": ROSE, "MEDIUM": AMBER, "LOW": EMRALD}.get(w.get("severity",""), DARK)
                story.append(Paragraph(
                    f'<font color="#{sev_color.hexval()[1:]}">[{w.get("severity")}]</font> <b>{w.get("label","")}</b>',
                    body
                ))
                story.append(Paragraph(w.get("message",""), small))
                story.append(Spacer(1, 0.2*cm))
            story.append(Spacer(1, 0.3*cm))

        # Recommendations
        recs = result.get("recommendations", [])
        if recs:
            story.append(Paragraph("AI-Powered Recommendations", h2))
            for i, rec in enumerate(recs[:5], 1):
                story.append(Paragraph(f'{i}. [{rec.get("priority")}] {rec.get("title","")}', body))
                story.append(Paragraph(rec.get("description","")[:300], small))
                for act in rec.get("action_items", [])[:3]:
                    story.append(Paragraph(f"• {act}", small))
                story.append(Spacer(1, 0.25*cm))

        # Footer
        story.append(HRFlowable(width="100%", thickness=1, color=AMBER))
        story.append(Paragraph("PlaceIQ AI System · http://localhost:5050", small))

        doc.build(story)
        pdf_bytes = buf.getvalue()

        if output_path:
            with open(output_path, "wb") as f:
                f.write(pdf_bytes)
            return None
        return pdf_bytes

    except ImportError:
        # reportlab not installed — return None, caller should fallback to TXT
        return None


def pdf_available() -> bool:
    """Check whether reportlab is installed for PDF generation."""
    try:
        import reportlab  # noqa: F401
        return True
    except ImportError:
        return False
