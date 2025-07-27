import streamlit as st
import json
import shutil
import requests
from pathlib import Path
from typing import Dict, Any, Optional
import re
import logging
from contextlib import contextmanager
from utils.pdf_resume import generate_resume_pdf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
RESUME_PATH = Path("data/resume.json")
TAILORED_PATH = Path("data/tailored_resume.json")
OUTPUT_PATH = Path("output/tailored_resume.pdf")

class ResumeGenerator:
    """Handles resume generation and tailoring operations."""
    
    def __init__(self, model: str = "llama3"):
        self.model = model
        self.session_state = st.session_state
        
    @contextmanager
    def loading_spinner(self, text: str):
        """Context manager for loading spinners."""
        with st.spinner(text):
            yield
    
    def validate_inputs(self, job_desc: str) -> bool:
        """Validate user inputs."""
        if not job_desc.strip():
            st.error("Please enter a job description.")
            return False
        
        if not RESUME_PATH.exists():
            st.error(f"Resume file not found at {RESUME_PATH}")
            return False
        
        return True
    
    def load_resume(self) -> Optional[Dict[str, Any]]:
        """Load resume data from JSON file."""
        try:
            with open(RESUME_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            st.error(f"Error loading resume: {e}")
            return None
    
    def ollama_generate(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Call Ollama API with error handling and retries."""
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    OLLAMA_URL, 
                    json={"model": self.model, "prompt": prompt}, 
                    stream=True,
                    timeout=60
                )
                response.raise_for_status()
                
                output = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode("utf-8"))
                            output += data.get("response", "")
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
                
                return output.strip()
                
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    st.error(f"Failed to connect to Ollama after {max_retries} attempts: {e}")
                    return None
        
        return None
    
    def extract_json(self, text: str) -> Optional[str]:
        """Extract JSON from potentially messy text response."""
        # Remove markdown code blocks
        text = re.sub(r'```json\n?|```\n?', '', text)
        
        # Try to find JSON array or object
        patterns = [
            r'(\{.*\})',  # Object
            r'(\[.*\])',  # Array
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return None
    
    def extract_keywords(self, job_desc: str) -> Optional[str]:
        """Extract keywords from job description."""
        prompt = f"""Extract the most important skills, technologies, and keywords from this job description. 
        Focus on:
        - Technical skills and programming languages
        - Tools and frameworks
        - Industry-specific terms
        - Required qualifications
        
        Job Description:
        {job_desc}
        
        Provide a concise list of the most relevant keywords."""
        
        with self.loading_spinner("Extracting keywords from job description..."):
            return self.ollama_generate(prompt)
    
    def tailor_resume_section(self, section_name: str, section_data: Any, keywords: str) -> Any:
        """Tailor a specific resume section using extracted keywords."""
        prompt = f"""You are a professional resume optimization assistant WHO JUST GIVES JSON OUTPUT NOTHING ELSE

Your task is to enhance the following resume section by strategically incorporating relevant keywords from the job description. Follow these guidelines:

STRICT REQUIREMENTS:
1. Preserve ALL original content - do not remove any items, experiences, or skills
2. Only ADD or MODIFY existing content to include relevant keywords
3. Maintain the overall JSON structure exactly
4. Ensure all additions are truthful and relevant to existing content
5. Output JUST ONLY valid JSON with no explanations or commentary [This is strong demand]. ONLY JSON

Resume Section ({section_name}):
{json.dumps(section_data, indent=2)}

Relevant Keywords to Incorporate:
{keywords}

Instructions:
- For skills: Add relevant technologies that complement existing skills
- For experience: Enhance descriptions with relevant technical terms & keywords
- For projects: Improve descriptions with applicable keywords
- Maintain professional tone and accuracy

Return the enhanced section as valid JSON only:"""

        with self.loading_spinner(f"Tailoring {section_name} section..."):
            response = self.ollama_generate(prompt)
            
            if not response:
                return section_data
            
            # Show raw output in expander for debugging
            with st.expander(f"Raw AI output for {section_name} (click to view)"):
                st.code(response, language="json")
            
            try:
                # cleaned_json = self.extract_json(response)
                cleaned_json = response
                if cleaned_json:
                    parsed_data = json.loads(cleaned_json)
                    st.success(f"✅ Successfully enhanced {section_name} section")
                    return parsed_data
                else:
                    raise ValueError("No valid JSON found in response")
                    
            except (json.JSONDecodeError, ValueError) as e:
                st.warning(f"⚠️ Failed to parse AI output for {section_name}: {e}")
                st.info(f"Keeping original {section_name} section unchanged")
                return section_data
    
    def save_tailored_resume(self, resume_data: Dict[str, Any]) -> bool:
        """Save the tailored resume to file."""
        try:
            # Ensure directory exists
            TAILORED_PATH.parent.mkdir(parents=True, exist_ok=True)
            
            with open(TAILORED_PATH, "w", encoding="utf-8") as f:
                json.dump(resume_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            st.error(f"Error saving tailored resume: {e}")
            return False
    
    def generate_pdf(self) -> bool:
        """Generate PDF from tailored resume."""
        try:
            # Ensure output directory exists
            OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
            
            with self.loading_spinner("Generating PDF..."):
                generate_resume_pdf(str(TAILORED_PATH), str(OUTPUT_PATH))
            return True
        except Exception as e:
            st.error(f"Error generating PDF: {e}")
            return False

def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="AI Resume Tailor",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("🎯 AI-Powered Resume Tailor")
    st.markdown("*Intelligently customize your resume for any job description*")
    
    # Initialize session state
    if 'generator' not in st.session_state:
        st.session_state.generator = ResumeGenerator()
    
    generator = st.session_state.generator
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        model = st.selectbox(
            "AI Model",
            ["llama3", "llama3.1", "mistral", "codellama"],
            help="Select the AI model for resume tailoring"
        )
        generator.model = model
        
        st.header("📁 File Status")
        resume_exists = RESUME_PATH.exists()
        st.write(f"Resume file: {'✅' if resume_exists else '❌'}")
        if resume_exists:
            st.write(f"Path: `{RESUME_PATH}`")
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📋 Job Description")
        job_desc = st.text_area(
            "Paste the job description here:",
            height=300,
            placeholder="Paste the complete job description including requirements, responsibilities, and preferred qualifications..."
        )
        
        # Character count
        if job_desc:
            st.caption(f"Characters: {len(job_desc)}")
    
    with col2:
        st.header("📄 Resume Preview")
        resume_data = generator.load_resume()
        
        if resume_data:
            # Show resume sections
            for section in ["skills", "experience", "projects"]:
                if section in resume_data:
                    with st.expander(f"{section.title()} Section"):
                        st.json(resume_data[section])
        else:
            st.error("Could not load resume data")
    
    # Generation section
    st.header("🚀 Generate Tailored Resume")
    
    if st.button("Generate Tailored Resume", type="primary", use_container_width=True):
        if not generator.validate_inputs(job_desc):
            st.stop()
        
        resume_data = generator.load_resume()
        if not resume_data:
            st.stop()
        
        # Create backup
        shutil.copy(RESUME_PATH, TAILORED_PATH)
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Extract keywords
            status_text.text("Step 1/4: Extracting keywords...")
            progress_bar.progress(25)
            
            keywords = generator.extract_keywords(job_desc)
            if not keywords:
                st.error("Failed to extract keywords")
                st.stop()
            
            with st.expander("🔑 Extracted Keywords"):
                st.write(keywords)
            
            # Step 2: Tailor resume sections
            sections_to_tailor = ["skills", "experience", "projects"]
            tailored_resume = resume_data.copy()
            
            for i, section in enumerate(sections_to_tailor):
                status_text.text(f"Step {i+2}/4: Tailoring {section} section...")
                progress_bar.progress(25 + (i+1) * 20)
                
                if section in resume_data:
                    tailored_resume[section] = generator.tailor_resume_section(
                        section, resume_data[section], keywords
                    )
            
            # Step 3: Save tailored resume
            status_text.text("Step 4/4: Generating files...")
            progress_bar.progress(90)
            
            if not generator.save_tailored_resume(tailored_resume):
                st.stop()
            
            # Step 4: Generate PDF
            if generator.generate_pdf():
                progress_bar.progress(100)
                status_text.text("✅ Resume tailoring completed!")
                
                st.success("🎉 Tailored resume generated successfully!")
                
                # Download button
                try:
                    with open(OUTPUT_PATH, "rb") as pdf_file:
                        st.download_button(
                            label="📥 Download Tailored Resume PDF",
                            data=pdf_file.read(),
                            file_name="tailored_resume.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                except FileNotFoundError:
                    st.error("PDF file not found. Please try generating again.")
            
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            logger.error(f"Resume generation error: {e}", exc_info=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
        Made with ❤️ using Streamlit and Ollama
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()