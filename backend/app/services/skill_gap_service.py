from typing import Dict, Any, List, Optional, Set
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.skill_gap import SkillGapAnalysis
from app.services.student_profile_service import StudentProfileService
from app.services.resume_analysis_service import ResumeAnalysisService

# Predefined Skill Requirements per Target Job Role
ROLE_SKILL_REQUIREMENTS: Dict[str, Dict[str, List[str]]] = {
    "Backend Engineer": {
        "required": ["Python", "SQL", "REST API", "System Design", "PostgreSQL", "Git"],
        "recommended": ["FastAPI", "Django", "Docker", "Redis", "Microservices", "CI/CD"]
    },
    "Frontend Engineer": {
        "required": ["JavaScript", "TypeScript", "React", "HTML", "CSS", "Git"],
        "recommended": ["Next.js", "Redux", "Tailwind", "WebSockets", "REST API"]
    },
    "Fullstack Developer": {
        "required": ["JavaScript", "Python", "React", "SQL", "REST API", "Git", "HTML"],
        "recommended": ["FastAPI", "PostgreSQL", "Docker", "Next.js", "Redis", "CI/CD"]
    },
    "AI / ML Engineer": {
        "required": ["Python", "PyTorch", "TensorFlow", "NumPy", "Pandas", "Scikit-Learn", "Git"],
        "recommended": ["LLM", "BERT", "Docker", "SQL", "Prompt Engineering", "OpenCV"]
    },
    "DevOps Engineer": {
        "required": ["Linux", "Docker", "Kubernetes", "AWS", "CI/CD", "Git", "Terraform", "Shell"],
        "recommended": ["Python", "Nginx", "GCP", "Azure", "WebSockets"]
    },
    "Data Scientist": {
        "required": ["Python", "SQL", "Pandas", "NumPy", "Scikit-Learn", "R", "Git"],
        "recommended": ["PyTorch", "TensorFlow", "PostgreSQL", "Docker", "Elasticsearch"]
    },
    "Mobile App Developer (iOS/Android)": {
        "required": ["Swift", "Kotlin", "React", "REST API", "Git", "SQLite"],
        "recommended": ["Firebase", "CI/CD", "TypeScript", "Docker"]
    },
    "Cloud Architect": {
        "required": ["AWS", "GCP", "Azure", "System Design", "Microservices", "Terraform", "Docker", "Kubernetes"],
        "recommended": ["Python", "Linux", "CI/CD", "Nginx"]
    },
    "Cybersecurity Engineer": {
        "required": ["Linux", "Python", "Shell", "Git", "REST API"],
        "recommended": ["Docker", "AWS", "C++", "System Design"]
    },
    "Product Manager": {
        "required": ["Agile", "Jira", "System Design", "SQL"],
        "recommended": ["REST API", "Python", "Git"]
    },
    "Default": {
        "required": ["Python", "JavaScript", "SQL", "Git", "REST API"],
        "recommended": ["Docker", "PostgreSQL", "FastAPI", "React", "CI/CD"]
    }
}


class SkillGapService:
    """
    Service logic for computing Skill Gap Analysis comparing candidate skills against target role requirements.
    """

    @staticmethod
    def get_requirements_for_role(role_name: str) -> Dict[str, List[str]]:
        """
        Retrieves matching required & recommended skill sets for a given role name.
        """
        # Exact match
        if role_name in ROLE_SKILL_REQUIREMENTS:
            return ROLE_SKILL_REQUIREMENTS[role_name]
        
        # Partial/case-insensitive match
        role_lower = role_name.lower()
        for key, reqs in ROLE_SKILL_REQUIREMENTS.items():
            if key.lower() in role_lower or role_lower in key.lower():
                return reqs
                
        return ROLE_SKILL_REQUIREMENTS["Default"]

    @staticmethod
    def analyze_skill_gap(db: Session, user_id: int) -> SkillGapAnalysis:
        """
        Calculates Skill Gap Analysis by cross-referencing candidate's Resume Analysis skills
        with target role requirements, and persists the result in SQLite.
        """
        # 1. Fetch Student Profile for selected target role
        profile = StudentProfileService.get_by_user_id(db, user_id=user_id)
        if not profile or not profile.target_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target role not selected yet. Please select a target role first."
            )

        target_role = profile.target_role

        # 2. Fetch Resume Analysis for extracted candidate skills
        resume_analysis = ResumeAnalysisService.get_user_analysis(db, user_id=user_id)
        if not resume_analysis:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume analysis not found. Please upload and analyze your PDF resume first."
            )

        # Combine all extracted candidate skill tokens (case-insensitive for comparison)
        candidate_skills_raw = (
            (resume_analysis.programming_languages or []) +
            (resume_analysis.frameworks or []) +
            (resume_analysis.databases or []) +
            (resume_analysis.technical_skills or [])
        )
        candidate_skills_set: Set[str] = {s.strip().lower() for s in candidate_skills_raw if s}

        # Map lower-case tokens back to neat display strings
        display_map = {s.strip().lower(): s.strip() for s in candidate_skills_raw if s}

        # 3. Fetch role requirements
        role_reqs = SkillGapService.get_requirements_for_role(target_role)
        required_list = role_reqs.get("required", [])
        recommended_list = role_reqs.get("recommended", [])

        # Calculate Strong (Matched) Skills
        strong_skills = []
        for req in required_list + recommended_list:
            req_lower = req.lower()
            if req_lower in candidate_skills_set:
                strong_skills.append(display_map.get(req_lower, req))

        # Include additional candidate skills that fit the role
        for c_lower, c_display in display_map.items():
            if c_display not in strong_skills:
                strong_skills.append(c_display)

        strong_skills = sorted(list(set(strong_skills)))

        # Calculate Missing Required Skills
        missing_skills = []
        for req in required_list:
            if req.lower() not in candidate_skills_set:
                missing_skills.append(req)

        # Calculate Recommended Skills to Learn
        recommended_skills = []
        for rec in recommended_list:
            if rec.lower() not in candidate_skills_set:
                recommended_skills.append(rec)
        
        # Ensure missing core skills are prioritized in recommended
        for m in missing_skills:
            if m not in recommended_skills:
                recommended_skills.insert(0, m)

        # Calculate Match Percentage
        total_required = len(required_list)
        matched_required_count = len([req for req in required_list if req.lower() in candidate_skills_set])
        
        if total_required > 0:
            match_percentage = round((matched_required_count / total_required) * 100.0, 1)
        else:
            match_percentage = 100.0

        # Cap match percentage within [0.0, 100.0]
        match_percentage = max(0.0, min(100.0, match_percentage))

        # Generate Overall Assessment text
        if match_percentage >= 80.0:
            assessment = (
                f"High Skill Match ({match_percentage}%). Candidate demonstrates strong alignment with core "
                f"requirements for '{target_role}'. Ready for targeted interview preparation."
            )
        elif match_percentage >= 50.0:
            missing_sample = ", ".join(missing_skills[:3]) if missing_skills else "advanced topics"
            assessment = (
                f"Moderate Skill Match ({match_percentage}%). Candidate possesses foundational skills for '{target_role}' "
                f"but has gaps in key areas ({missing_sample}). Focus on recommended skills prior to interviewing."
            )
        else:
            missing_sample = ", ".join(missing_skills[:4]) if missing_skills else "core principles"
            assessment = (
                f"Skill Gap Identified ({match_percentage}%). Significant skill gap for '{target_role}'. "
                f"Immediate focus recommended on mastering {missing_sample}."
            )

        # 4. Save or update SkillGapAnalysis record in SQLite DB
        gap_record = db.query(SkillGapAnalysis).filter(SkillGapAnalysis.user_id == user_id).first()
        if not gap_record:
            gap_record = SkillGapAnalysis(user_id=user_id)

        gap_record.target_role = target_role
        gap_record.match_percentage = match_percentage
        gap_record.strong_skills = strong_skills
        gap_record.missing_skills = missing_skills
        gap_record.recommended_skills = recommended_skills
        gap_record.overall_assessment = assessment

        db.add(gap_record)
        db.commit()
        db.refresh(gap_record)

        return gap_record

    @staticmethod
    def get_user_skill_gap(db: Session, user_id: int) -> Optional[SkillGapAnalysis]:
        """
        Retrieves existing saved Skill Gap Analysis result for user.
        """
        return db.query(SkillGapAnalysis).filter(SkillGapAnalysis.user_id == user_id).first()
