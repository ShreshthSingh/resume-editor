import streamlit as st
from utils import storage

st.title("Resume Editor")

resume = storage.load_resume()

# Contact Info
st.header("Contact Information")
firstName = st.text_input("First Name", resume.get("firstName", ""))
lastName = st.text_input("Last Name", resume.get("lastName", ""))
phoneNumber = st.text_input("Phone Number", resume.get("phoneNumber", ""))
email = st.text_input("Email", resume.get("email", ""))
location = st.text_input("Location", resume.get("location", ""))
linkedin = st.text_input("LinkedIn", resume.get("linkedin", ""))
github = st.text_input("GitHub", resume.get("github", ""))

if st.button("Save Contact Info"):
    storage.update_contact_info(firstName, lastName, phoneNumber, email, location, linkedin, github)
    st.success("Contact info saved!")

# Education
st.header("Education")
education_entry = st.text_area("Add Education Entry")
if st.button("Add Education"):
    if education_entry.strip():
        storage.add_education(education_entry.strip())
        st.success("Education entry added!")

st.write("Current Education Entries:")
for entry in storage.load_resume()["education"]:
    st.write(f"- {entry}")

# Achievements
st.header("Achievements")
achievement_entry = st.text_area("Add Achievements (one bullet per line)")
bullets_ach = [a.strip() for a in achievement_entry.split("\n") if a.strip()]
if st.button("Add Achievements"):
    for bullet in bullets_ach:
        storage.add_achievement(bullet)
    st.success("Achievements added!")

st.write("Current Achievements:")
for entry in storage.load_resume()["achievements"]:
    st.write(f"• {entry}")

# Experience
st.header("Experience")
role = st.text_input("Role")
company = st.text_input("Company")
startDate = st.text_input("Start Date (e.g. Jan 2023)")
endDate = st.text_input("End Date (e.g. May 2024)")
isPresent = st.checkbox("Currently working here?")
bullets = st.text_area("Bullet Points (one per line)").split("\n")
skills_exp = st.text_input("Skills (comma separated)")
if st.button("Add Experience"):
    skills_list = [s.strip() for s in skills_exp.split(",") if s.strip()]
    bullets_list = [b.strip() for b in bullets if b.strip()]
    storage.add_experience(role, company, startDate, endDate, isPresent, bullets_list, skills_list)
    st.success("Experience added!")

st.write("Current Experience Entries:")
for exp in storage.load_resume()["experience"]:
    st.write(f"- {exp['role']} at {exp['company']}")

# Projects
st.header("Projects")
title = st.text_input("Project Title")
desc = st.text_area("Project Description (one bullet per line)")
bullets_proj = [d.strip() for d in desc.split("\n") if d.strip()]
tech_stack = st.text_input("Tech Stack (comma separated)")
if st.button("Add Project"):
    tech_list = [t.strip() for t in tech_stack.split(",") if t.strip()]
    storage.add_project(title, "", bullets_proj, tech_list)
    st.success("Project added!")

st.write("Current Projects:")
for proj in storage.load_resume()["projects"]:
    st.write(f"- {proj['title']}")
    for bullet in proj.get("bullets", []):
        st.write(f"  • {bullet}")

# Skills
st.header("Skills")

# Programming Skills
prog_skills = st.text_input("Add Programming Skills (comma separated)")
if st.button("Add Programming Skills"):
    prog_list = [s.strip() for s in prog_skills.split(",") if s.strip()]
    storage.add_skills_category("Programming", prog_list)
    st.success("Programming skills added!")

# Technologies
tech_skills = st.text_input("Add Technologies (comma separated)")
if st.button("Add Technologies"):
    tech_list = [s.strip() for s in tech_skills.split(",") if s.strip()]
    storage.add_skills_category("Technologies", tech_list)
    st.success("Technologies added!")

# Tools
tool_skills = st.text_input("Add Tools (comma separated)")
if st.button("Add Tools"):
    tool_list = [s.strip() for s in tool_skills.split(",") if s.strip()]
    storage.add_skills_category("Tools", tool_list)
    st.success("Tools added!")

st.write("Current Skills:")
skills_data = storage.load_resume()["skills"]
st.write("**Programming:** " + ", ".join(skills_data.get("Programming", [])))
st.write("**Technologies:** " + ", ".join(skills_data.get("Technologies", [])))
st.write("**Tools:** " + ", ".join(skills_data.get("Tools", [])))