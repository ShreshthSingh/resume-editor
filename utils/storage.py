import json
import os

DATA_FILE = "data/resume.json"

DEFAULT_RESUME = {
    "firstName": "",
    "lastName": "",
    "phoneNumber": "",
    "email": "",
    "location": "",
    "linkedin": "",
    "github": "",
    "education": [],
    "achievements": [],
    "experience": [],
    "projects": [],
    "skills": []
}

def load_resume():
    if not os.path.exists(DATA_FILE):
        return DEFAULT_RESUME.copy()
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_resume(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_experience(role, company, startDate, endDate, isPresent, bullets, skills):
    resume = load_resume()
    resume["experience"].append({
        "role": role,
        "company": company,
        "startDate": startDate,
        "endDate": endDate,
        "isPresent": isPresent,
        "bullets": bullets,
        "skills": skills
    })
    save_resume(resume)

def add_project(title, description, bullets, tech_stack):
    resume = load_resume()
    resume["projects"].append({
        "title": title,
        "description": description,
        "bullets": bullets,
        "tech_stack": tech_stack
    })
    save_resume(resume)

def add_skills(skills):
    resume = load_resume()
    resume["skills"].extend(skills)
    resume["skills"] = list(set(resume["skills"]))  # remove duplicates
    save_resume(resume)

def add_education(education_entry):
    resume = load_resume()
    resume["education"].append(education_entry)
    save_resume(resume)

def add_achievement(achievement_entry):
    resume = load_resume()
    resume["achievements"].append(achievement_entry)
    save_resume(resume)

def update_contact_info(firstName, lastName, phoneNumber, email, location, linkedin, github):
    resume = load_resume()
    resume["firstName"] = firstName
    resume["lastName"] = lastName
    resume["phoneNumber"] = phoneNumber
    resume["email"] = email
    resume["location"] = location
    resume["linkedin"] = linkedin
    resume["github"] = github
    save_resume(resume)

def add_skills_category(category, skills):
    resume = load_resume()
    # Ensure skills is a dict with the required categories
    if "skills" not in resume or not isinstance(resume["skills"], dict):
        resume["skills"] = {"Programming": [], "Technologies": [], "Tools": []}
    if category not in resume["skills"]:
        resume["skills"][category] = []
    resume["skills"][category].extend(skills)
    # Remove duplicates
    resume["skills"][category] = list(set(resume["skills"][category]))
    save_resume(resume)
