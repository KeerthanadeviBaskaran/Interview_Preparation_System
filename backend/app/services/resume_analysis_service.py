import os
import re
from typing import Dict, Any, List, Optional
from pypdf import PdfReader
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.resume_analysis import ResumeAnalysis
from app.models.student_profile import StudentProfile
from app.services.student_profile_service import StudentProfileService
from app.utils.file_handler import UPLOAD_DIR

# Known technical dictionaries for NLP keyword matching
KNOWN_LANGUAGES = [
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Golang",
    "Rust", "Ruby", "PHP", "Swift", "Kotlin", "SQL", "HTML", "CSS", "R",
    "Scala", "Shell", "Bash", "Dart", "Elixir"
]

KNOWN_FRAMEWORKS = [
    "FastAPI", "Django", "Flask", "React", "Next.js", "Vue", "Vue.js", "Angular",
    "Node.js", "Express", "Spring Boot", "PyTorch", "TensorFlow", "Pandas",
    "NumPy", "Tailwind", "TailwindCSS", "Bootstrap", "Redux", "NestJS",
    "GraphQL", "Scikit-Learn", "Keras"
]

KNOWN_DATABASES = [
    "SQLite", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Cassandra",
    "DynamoDB", "Elasticsearch", "MariaDB", "Firebase", "Neo4j", "Oracle",
    "Snowflake", "Supabase"
]

KNOWN_TECH_SKILLS = [
    "Docker", "Kubernetes", "AWS", "GCP", "Azure", "Git", "GitHub", "GitLab",
    "CI/CD", "REST API", "Microservices", "System Design", "Linux", "Agile",
    "Jira", "Nginx", "Terraform", "WebSockets", "Kafka", "RabbitMQ", "Celery",
    "OpenCV", "BERT", "LLM", "Prompt Engineering"
]

KNOWN_CERT_KEYWORDS = [
    "AWS Certified", "GCP Certified", "Azure Certified", "Certified Kubernetes Administrator",
    "CKA", "PMP", "Coursera", "Udacity", "edX", "CompTIA", "Oracle Certified",
    "Scrum Master", "TensorFlow Developer"
]


class ResumeAnalysisService:
    """
    Service logic for parsing PDF resumes, extracting text, categorizing tech stack,
    and storing structured analysis in the SQLite database.
    """

    @staticmethod
    def extract_text_from_pdf(filepath: str) -> str:
        """
        Reads and extracts plain text from a local PDF document using pypdf.
        """
        if not os.path.exists(filepath):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume file not found on disk at: {filepath}"
            )

        try:
            reader = PdfReader(filepath)
            extracted_pages = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_pages.append(text)
            
            full_text = "\n".join(extracted_pages).strip()
            if not full_text:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not extract text from the PDF. The file may be image-based or password-protected."
                )
            return full_text
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to parse PDF document: {str(e)}"
            )

    @staticmethod
    def parse_resume_text(text: str) -> Dict[str, Any]:
        """
        Analyzes raw resume text and extracts structured skill categories,
        experience indicators, education history, and projects.
        """
        text_lower = text.lower()

        # Helper matching function respecting word boundaries
        def match_keywords(keyword_list: List[str]) -> List[str]:
            found = []
            for kw in keyword_list:
                # Escape special regex characters (e.g. C++, C#)
                escaped = re.escape(kw.lower())
                pattern = r"(?:\b|_)" + escaped + r"(?:\b|_)"
                if re.search(pattern, text_lower):
                    found.append(kw)
            return sorted(list(set(found)))

        extracted_languages = match_keywords(KNOWN_LANGUAGES)
        extracted_frameworks = match_keywords(KNOWN_FRAMEWORKS)
        extracted_databases = match_keywords(KNOWN_DATABASES)
        extracted_skills = match_keywords(KNOWN_TECH_SKILLS)

        # Certifications extraction
        extracted_certs = match_keywords(KNOWN_CERT_KEYWORDS)
        # Also check for general "Certificate" or "Certifications" lines
        cert_matches = re.findall(r"(?:certification|certified|certificate)s?\s*[:-]?\s*([^\n]+)", text, re.IGNORECASE)
        for cm in cert_matches:
            clean_cm = cm.strip()
            if clean_cm and len(clean_cm) < 100 and clean_cm not in extracted_certs:
                extracted_certs.append(clean_cm)

        # Experience extraction
        exp_data: Dict[str, Any] = {
            "years_mentioned": [],
            "roles_found": []
        }
        years_found = re.findall(r"(\d+\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)?)", text, re.IGNORECASE)
        if years_found:
            exp_data["years_mentioned"] = list(set([y.strip() for y in years_found]))

        role_keywords = ["Developer", "Engineer", "Architect", "Intern", "Manager", "Lead", "Consultant", "Analyst"]
        found_roles = [rk for rk in role_keywords if re.search(r"\b" + rk.lower() + r"\b", text_lower)]
        exp_data["roles_found"] = found_roles

        # Education extraction
        edu_data: Dict[str, Any] = {
            "degrees": [],
            "fields": []
        }
        degree_patterns = ["bachelor", "master", "phd", "b.s", "m.s", "b.tech", "m.tech", "b.e", "m.e", "diploma"]
        found_degrees = [dp.upper() for dp in degree_patterns if re.search(r"\b" + dp + r"\b", text_lower)]
        edu_data["degrees"] = found_degrees
        
        if "computer science" in text_lower:
            edu_data["fields"].append("Computer Science")
        if "information technology" in text_lower:
            edu_data["fields"].append("Information Technology")

        # Projects extraction
        extracted_projects: List[Dict[str, Any]] = []
        project_lines = re.findall(r"(?:project|portfolio)s?\s*[:-]?\s*([^\n]+)", text, re.IGNORECASE)
        for pl in project_lines[:5]:
            clean_p = pl.strip()
            if clean_p and len(clean_p) > 3:
                extracted_projects.append({"title": clean_p, "description": clean_p})

        # Summary generation
        total_items = len(extracted_languages) + len(extracted_frameworks) + len(extracted_databases) + len(extracted_skills)
        summary_text = (
            f"Analyzed resume contains {total_items} identified technical keywords including "
            f"{len(extracted_languages)} programming languages ({', '.join(extracted_languages[:3]) or 'N/A'}), "
            f"{len(extracted_frameworks)} frameworks ({', '.join(extracted_frameworks[:3]) or 'N/A'}), and "
            f"{len(extracted_databases)} database systems ({', '.join(extracted_databases[:3]) or 'N/A'})."
        )

        return {
            "programming_languages": extracted_languages,
            "frameworks": extracted_frameworks,
            "databases": extracted_databases,
            "technical_skills": extracted_skills,
            "projects": extracted_projects,
            "certifications": extracted_certs,
            "experience": exp_data,
            "education": edu_data,
            "summary": summary_text
        }

    @staticmethod
    def analyze_user_resume(db: Session, user_id: int) -> ResumeAnalysis:
        """
        Executes end-to-end PDF reading, text extraction, analysis parsing,
        and database storage for the user's uploaded resume.
        """
        profile = StudentProfileService.get_by_user_id(db, user_id=user_id)
        if not profile or not profile.resume_filename:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No uploaded resume found for this user. Please upload a PDF resume first."
            )

        filepath = os.path.join(UPLOAD_DIR, profile.resume_filename)
        
        # Extract text from PDF
        raw_text = ResumeAnalysisService.extract_text_from_pdf(filepath)

        # Parse text into structured resume components
        parsed = ResumeAnalysisService.parse_resume_text(raw_text)

        # Retrieve or create ResumeAnalysis record in SQLite DB
        analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.user_id == user_id).first()
        if not analysis:
            analysis = ResumeAnalysis(user_id=user_id)

        analysis.raw_text = raw_text
        analysis.programming_languages = parsed["programming_languages"]
        analysis.frameworks = parsed["frameworks"]
        analysis.databases = parsed["databases"]
        analysis.technical_skills = parsed["technical_skills"]
        analysis.projects = parsed["projects"]
        analysis.certifications = parsed["certifications"]
        analysis.experience = parsed["experience"]
        analysis.education = parsed["education"]
        analysis.summary = parsed["summary"]

        db.add(analysis)

        # Update profile skills automatically if empty
        if profile and not profile.skills:
            all_skills = list(set(parsed["programming_languages"] + parsed["frameworks"] + parsed["technical_skills"]))
            profile.skills = all_skills
            db.add(profile)

        db.commit()
        db.refresh(analysis)
        return analysis

    @staticmethod
    def get_user_analysis(db: Session, user_id: int) -> Optional[ResumeAnalysis]:
        """
        Retrieves the user's existing resume analysis record.
        """
        return db.query(ResumeAnalysis).filter(ResumeAnalysis.user_id == user_id).first()
