import streamlit as st
import json
import shutil
import requests
from utils.pdf_resume import generate_resume_pdf

st.title("Job Description Tailored Resume Generator")

# Step 1: Enter Job Description
st.header("Paste Job Description")
job_desc = st.text_area("Job Description", height=200)

# Step 2: Load Resume
resume_path = "data/resume.json"
with open(resume_path, "r") as f:
    resume = json.load(f)

# Helper function to call Ollama and handle streaming JSON responses
def ollama_generate(model, prompt):
    ollama_url = "http://localhost:11434/api/generate"
    response = requests.post(ollama_url, json={"model": model, "prompt": prompt}, stream=True)
    output = ""
    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            output += data.get("response", "")
            if data.get("done", False):
                break
    return output.strip()

# Step 3: Modify Resume with Ollama
if st.button("Generate Tailored Resume"):
    if not job_desc.strip():
        st.error("Please enter a job description.")
        st.stop()

    # Save a copy of resume.json
    tailored_path = "data/tailored_resume.json"
    shutil.copy(resume_path, tailored_path)

    # --- Call Ollama to get keywords ---
    keywords = ollama_generate(
        "llama3",
        f"Extract the most important skills, technologies, and keywords from this job description:\n{job_desc}"
    )
    st.write("Extracted Keywords:")
    st.info(keywords)

    # --- Call Ollama to rewrite resume sections ---
    for section in ["skills", "experience", "projects"]:
        prompt = (
            f"Here is my resume section:\n{json.dumps(resume[section], indent=2)}\n\n"
            f"Here are the job keywords:\n{keywords}\n\n"
            "Rewrite this section to better match the job description, using relevant keywords and removing unrelated content. "
            "Keep it concise and impactful. Return ONLY valid JSON (array or object) without any extra text."
        )
        rewritten = ollama_generate("llama3", prompt)

        # Show raw output for debugging
        st.text_area(f"Raw Ollama output for {section}", rewritten, height=150)

        try:
            resume[section] = json.loads(rewritten)
        except Exception as e:
            st.error(f"Failed to parse Ollama output for {section}: {e}")
            st.warning(f"Keeping original {section} section.")
            # fallback to original section

    # Save tailored resume
    with open(tailored_path, "w") as f:
        json.dump(resume, f, indent=2)

    # Generate PDF
    pdf_path = "output/tailored_resume.pdf"
    generate_resume_pdf(tailored_path, pdf_path)
    st.success("Tailored resume generated!")
    st.download_button("Download PDF", open(pdf_path, "rb"), file_name="tailored_resume.pdf")
