from utils.storage import add_experience, add_project, add_skills, load_resume
from utils.jd_parser import extract_keywords

def input_list(prompt):
    return [item.strip() for item in input(prompt).split(",")]

def show_menu():
    print("\n==== Resume Optimizer ====")
    print("1. Add Experience")
    print("2. Add Project")
    print("3. Add Skills")
    print("4. View Resume")
    print("5. Input Job Description")
    print("6. Exit")

def main():
    while True:
        show_menu()
        choice = input("Enter your choice: ")

        if choice == "1":
            role = input("Enter role: ")
            company = input("Enter company: ")
            description = input("Describe your role: ")
            skills = input_list("Skills used (comma separated): ")
            add_experience(role, company, description, skills)

        elif choice == "2":
            title = input("Project title: ")
            description = input("Describe the project: ")
            tech_stack = input_list("Tech used (comma separated): ")
            add_project(title, description, tech_stack)

        elif choice == "3":
            skills = input_list("Enter new skills (comma separated): ")
            add_skills(skills)

        elif choice == "4":
            resume = load_resume()
            print("\n--- Resume Data ---")
            print(resume)

        elif choice == "5":
            jd = input("Paste the job description:\n")
            keywords = extract_keywords(jd)
            print("\nTop Keywords Extracted:")
            print(keywords)

        elif choice == "6":
            print("Exiting.")
            break

        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
