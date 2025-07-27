import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.units import inch

def load_resume(json_path):
    with open(json_path, "r") as f:
        return json.load(f)

def make_resume_story(resume):
    styles = getSampleStyleSheet()
    story = []

    # Header
    header = f"<b>{resume['firstName']} {resume['lastName']}</b>"
    contact = f"{resume['email']} | {resume['phoneNumber']} | {resume['location']}<br/>" \
              f"<a href='{resume['linkedin']}'>LinkedIn</a> | <a href='{resume['github']}'>GitHub</a>"
    story.append(Paragraph(header, styles['Title']))
    story.append(Paragraph(contact, styles['Normal']))
    story.append(Spacer(1, 0.05*inch))

    # Education
    story.append(Paragraph("Education", styles['Heading2']))
    for edu in resume.get("education", []):
        story.append(Paragraph(f"- {edu}", styles['Normal']))
    story.append(Spacer(1, 0.05*inch))

    # Achievements
    if resume.get("achievements"):
        story.append(Paragraph("Achievements", styles['Heading2']))
        ach_list = ListFlowable(
            [ListItem(Paragraph(ach, styles['Normal'])) for ach in resume["achievements"]],
            bulletType='bullet'
        )
        story.append(ach_list)
        story.append(Spacer(1, 0.1*inch))

    # Experience
    if resume.get("experience"):
        story.append(Paragraph("Experience", styles['Heading2']))
        for exp in resume["experience"]:
            role = exp.get("role", "")
            company = exp.get("company", "")
            start = exp.get("startDate", "")
            end = "Present" if exp.get("isPresent") else exp.get("endDate", "")
            story.append(Paragraph(f"<b>{role}</b>, {company} ({start} - {end})", styles['Normal']))
            exp_bullets = ListFlowable(
                [ListItem(Paragraph(bullet, styles['Normal'])) for bullet in exp.get("bullets", [])],
                bulletType='bullet'
            )
            story.append(exp_bullets)
            if exp.get("skills"):
                story.append(Paragraph(f"<i>Skills: {', '.join(exp['skills'])}</i>", styles['Normal']))
            story.append(Spacer(1, 0.05*inch))

    # Projects
    if resume.get("projects"):
        story.append(Paragraph("Projects", styles['Heading2']))
        for proj in resume["projects"]:
            title = proj.get("title", "")
            story.append(Paragraph(f"<b>{title}</b>", styles['Normal']))
            proj_bullets = ListFlowable(
                [ListItem(Paragraph(bullet, styles['Normal'])) for bullet in proj.get("bullets", [])],
                bulletType='bullet'
            )
            story.append(proj_bullets)
            if proj.get("tech_stack"):
                story.append(Paragraph(f"<i>Tech Stack: {', '.join(proj['tech_stack'])}</i>", styles['Normal']))
            story.append(Spacer(1, 0.05*inch))

    # Skills
    if resume.get("skills"):
        story.append(Paragraph("Skills", styles['Heading2']))
        for cat, items in resume["skills"].items():
            story.append(Paragraph(f"<b>{cat}:</b> {', '.join(items)}", styles['Normal']))
        story.append(Spacer(1, 0.05*inch))

    return story

def generate_resume_pdf(json_path, pdf_path):
    resume = load_resume(json_path)
    story = make_resume_story(resume)
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                            leftMargin=0.5*inch, rightMargin=0.5*inch,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)
    doc.build(story)

# Example usage:
# generate_resume_pdf("../data/resume.json", "../output/resume.pdf")