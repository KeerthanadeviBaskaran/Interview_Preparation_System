from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.roadmap import Roadmap
from app.services.student_profile_service import StudentProfileService
from app.services.resume_analysis_service import ResumeAnalysisService
from app.services.skill_gap_service import SkillGapService

# Comprehensive Tech Skill Knowledge Base
SKILL_KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    "System Design": {
        "learning_objective": "Master high-level architecture design, load balancing, caching, and database partitioning.",
        "difficulty": "Advanced",
        "estimated_duration": "2 Weeks",
        "resources": [
            {"title": "System Design Primer (GitHub)", "url": "https://github.com/donnemartin/system-design-primer"},
            {"title": "Designing Data-Intensive Applications", "url": "https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/"}
        ],
        "practice_project": "Design a scalable URL Shortener or Distributed Rate Limiter service.",
        "interview_tips": "Focus on trade-offs (CAP theorem, latency vs throughput) and estimate storage/bandwidth metrics."
    },
    "Git": {
        "learning_objective": "Understand version control workflows, branching strategies, rebasing, and merge conflict resolution.",
        "difficulty": "Beginner",
        "estimated_duration": "3-5 Days",
        "resources": [
            {"title": "Pro Git Book (Free)", "url": "https://git-scm.com/book/en/v2"},
            {"title": "Interactive Git Branching", "url": "https://learngitbranching.js.org/"}
        ],
        "practice_project": "Set up a GitHub repository with feature branches, PR templates, and branch protection rules.",
        "interview_tips": "Be prepared to explain git rebase vs git merge and how git stores object blobs internally."
    },
    "Docker": {
        "learning_objective": "Learn containerization concepts, Dockerfile creation, multi-stage builds, and Docker Compose.",
        "difficulty": "Intermediate",
        "estimated_duration": "1 Week",
        "resources": [
            {"title": "Docker Official Documentation", "url": "https://docs.docker.com/get-started/"},
            {"title": "Docker Curriculum", "url": "https://docker-curriculum.com/"}
        ],
        "practice_project": "Containerize a full-stack application (FastAPI backend + React frontend + PostgreSQL DB) using Docker Compose.",
        "interview_tips": "Explain image layer caching, container networking, and security best practices for Dockerfiles."
    },
    "Kubernetes": {
        "learning_objective": "Understand container orchestration, Pods, Deployments, Services, and ConfigMaps.",
        "difficulty": "Advanced",
        "estimated_duration": "2-3 Weeks",
        "resources": [
            {"title": "Kubernetes Basics Tutorial", "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/"},
            {"title": "KodeKloud Kubernetes Course", "url": "https://kodekloud.com/courses/kubernetes-for-the-absolute-beginners-hands-on/"}
        ],
        "practice_project": "Deploy a microservice cluster locally using Minikube or Kind with ingress routing.",
        "interview_tips": "Be ready to explain how Kubernetes control plane components (kube-apiserver, etcd, scheduler) communicate."
    },
    "PostgreSQL": {
        "learning_objective": "Master relational database design, indexing strategies, transactions (ACID), and query optimization.",
        "difficulty": "Intermediate",
        "estimated_duration": "1-2 Weeks",
        "resources": [
            {"title": "PostgreSQL Official Tutorial", "url": "https://www.postgresqltutorial.com/"},
            {"title": "Use The Index, Luke!", "url": "https://use-the-index-luke.com/"}
        ],
        "practice_project": "Optimize slow SQL queries using EXPLAIN ANALYZE and implement B-tree index optimizations.",
        "interview_tips": "Be ready to discuss isolation levels, B-tree indexes vs Hash indexes, and foreign key cascades."
    },
    "Redis": {
        "learning_objective": "Learn in-memory data structures, caching patterns, pub/sub messaging, and rate limiting.",
        "difficulty": "Intermediate",
        "estimated_duration": "5 Days",
        "resources": [
            {"title": "Redis University", "url": "https://university.redis.com/"},
            {"title": "Redis Crash Course", "url": "https://redis.io/docs/latest/develop/get-started/"}
        ],
        "practice_project": "Build an API response caching layer and token bucket rate limiter backed by Redis.",
        "interview_tips": "Explain cache invalidation strategies (Cache-Aside, Write-Through) and Redis persistence models (RDB vs AOF)."
    },
    "CI/CD": {
        "learning_objective": "Automate testing, linting, building, and deployment pipelines using GitHub Actions or GitLab CI.",
        "difficulty": "Intermediate",
        "estimated_duration": "1 Week",
        "resources": [
            {"title": "GitHub Actions Documentation", "url": "https://docs.github.com/en/actions"},
            {"title": "Continuous Delivery Guide", "url": "https://minimumviablecd.com/"}
        ],
        "practice_project": "Create a GitHub Actions workflow that runs pytest, builds Docker images, and deploys on push to main.",
        "interview_tips": "Discuss blue-green deployments, canary releases, and secret management in CI pipelines."
    },
    "FastAPI": {
        "learning_objective": "Build high-performance REST APIs with asynchronous Python, Pydantic validation, and dependency injection.",
        "difficulty": "Intermediate",
        "estimated_duration": "1 Week",
        "resources": [
            {"title": "FastAPI Official Documentation", "url": "https://fastapi.tiangolo.com/tutorial/"},
            {"title": "Full Stack FastAPI Template", "url": "https://github.com/fastapi/full-stack-fastapi-template"}
        ],
        "practice_project": "Develop a production-ready REST API with OAuth2 authentication, SQLAlchemy ORM, and automated tests.",
        "interview_tips": "Explain ASGI vs WSGI, Python asyncio event loops, and Pydantic validation mechanics."
    },
    "React": {
        "learning_objective": "Master modern component architecture, hooks (useState, useEffect, useMemo), and state management.",
        "difficulty": "Intermediate",
        "estimated_duration": "2 Weeks",
        "resources": [
            {"title": "React Official Documentation", "url": "https://react.dev/learn"},
            {"title": "Full Stack Open (University of Helsinki)", "url": "https://fullstackopen.com/en/"}
        ],
        "practice_project": "Build an interactive dashboard consuming backend REST endpoints with live state updates.",
        "interview_tips": "Explain Virtual DOM reconciliation, custom hooks creation, and state lifting principles."
    },
    "AWS": {
        "learning_objective": "Learn core cloud infrastructure services (EC2, S3, RDS, Lambda, IAM, VPC).",
        "difficulty": "Intermediate",
        "estimated_duration": "2 Weeks",
        "resources": [
            {"title": "AWS Skill Builder (Free)", "url": "https://explore.skillbuilder.aws/"},
            {"title": "AWS Cloud Practitioner Essentials", "url": "https://aws.amazon.com/training/course-descriptions/cloud-practitioner-essentials/"}
        ],
        "practice_project": "Deploy a web application on EC2 behind an Application Load Balancer with RDS PostgreSQL.",
        "interview_tips": "Explain IAM roles vs policies, S3 security policies, and VPC subnet architecture."
    }
}


class RoadmapService:
    """
    Service logic for generating structured, multi-phase personalized learning roadmaps.
    """

    @staticmethod
    def get_skill_details(skill_name: str, phase: str) -> Dict[str, Any]:
        """
        Retrieves skill metadata from knowledge base or constructs a tailored template.
        """
        # Exact or partial match in knowledge base
        matched_kb = None
        for key in SKILL_KNOWLEDGE_BASE:
            if key.lower() == skill_name.lower() or key.lower() in skill_name.lower():
                matched_kb = SKILL_KNOWLEDGE_BASE[key]
                break

        if matched_kb:
            details = dict(matched_kb)
            details["skill_name"] = skill_name
            details["phase"] = phase
            return details

        # Generic template fallback for unlisted skills
        return {
            "skill_name": skill_name,
            "phase": phase,
            "learning_objective": f"Master fundamental and advanced principles of {skill_name} for production engineering.",
            "difficulty": "Intermediate",
            "estimated_duration": "1-2 Weeks",
            "resources": [
                {"title": f"{skill_name} Official Documentation & Guides", "url": f"https://www.google.com/search?q={skill_name}+documentation"},
                {"title": f"{skill_name} Masterclass & Tutorials", "url": f"https://www.coursera.org/search?query={skill_name}"}
            ],
            "practice_project": f"Build a mini-application incorporating {skill_name} into your portfolio project.",
            "interview_tips": f"Review core syntax, common pitfalls, memory/performance implications, and typical interview questions for {skill_name}."
        }

    @staticmethod
    def generate_roadmap(db: Session, user_id: int) -> Roadmap:
        """
        Generates a personalized, multi-horizon learning roadmap based on Student Profile,
        Resume Analysis, and Skill Gap Analysis. Persists result in SQLite database.
        """
        # 1. Verify Student Profile and Target Role
        profile = StudentProfileService.get_by_user_id(db, user_id=user_id)
        if not profile or not profile.target_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target role not selected yet. Please select a target role first."
            )

        target_role = profile.target_role
        experience_level = profile.experience_level or "Entry Level"

        # 2. Verify Resume Analysis
        resume_analysis = ResumeAnalysisService.get_user_analysis(db, user_id=user_id)
        if not resume_analysis:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume analysis not found. Please upload and analyze your PDF resume first."
            )

        # 3. Get or trigger Skill Gap Analysis
        skill_gap = SkillGapService.get_user_skill_gap(db, user_id=user_id)
        if not skill_gap:
            skill_gap = SkillGapService.analyze_skill_gap(db, user_id=user_id)

        missing_skills = skill_gap.missing_skills or []
        recommended_skills = skill_gap.recommended_skills or []

        # Combine unique skills to learn
        all_to_learn = list(dict.fromkeys(missing_skills + recommended_skills))

        # Distribute skills across the 4 time horizons
        immediate_items: List[Dict[str, Any]] = []
        short_term_items: List[Dict[str, Any]] = []
        medium_term_items: List[Dict[str, Any]] = []
        long_term_items: List[Dict[str, Any]] = []

        for idx, skill in enumerate(all_to_learn):
            if idx == 0 or idx == 1:
                # Top 1-2 missing core skills -> Immediate (1-2 Weeks)
                item = RoadmapService.get_skill_details(skill, "immediate")
                item["difficulty"] = "Intermediate"
                item["estimated_duration"] = "1-2 Weeks"
                immediate_items.append(item)
            elif idx == 2 or idx == 3:
                # Next skills -> Short-Term (1 Month)
                item = RoadmapService.get_skill_details(skill, "short_term")
                item["difficulty"] = "Intermediate"
                item["estimated_duration"] = "2 Weeks"
                short_term_items.append(item)
            elif idx == 4 or idx == 5:
                # Next skills -> Medium-Term (2-3 Months)
                item = RoadmapService.get_skill_details(skill, "medium_term")
                item["difficulty"] = "Advanced"
                item["estimated_duration"] = "3-4 Weeks"
                medium_term_items.append(item)
            else:
                # Remaining -> Long-Term (Beyond 3 Months)
                item = RoadmapService.get_skill_details(skill, "long_term")
                item["difficulty"] = "Advanced"
                item["estimated_duration"] = "1 Month"
                long_term_items.append(item)

        # Always ensure Long-Term phase includes System Design & Mock Interview Practice
        if not any(it["skill_name"] == "System Design" for it in immediate_items + short_term_items + medium_term_items + long_term_items):
            sys_item = RoadmapService.get_skill_details("System Design", "long_term")
            long_term_items.append(sys_item)

        mock_item = {
            "skill_name": "Mock Interview & Technical Speech Practice",
            "phase": "long_term",
            "learning_objective": "Practice answering live technical questions, whiteboarding, and STAR method behavioral responses.",
            "difficulty": "Advanced",
            "estimated_duration": "Ongoing",
            "resources": [
                {"title": "Pramp - Peer Mock Interviews", "url": "https://www.pramp.com/"},
                {"title": "LeetCode Interview Preparation", "url": "https://leetcode.com/interview/"}
            ],
            "practice_project": "Conduct 5 live mock technical interviews and record video responses to evaluate communication clarity.",
            "interview_tips": "Structure answers clearly using the STAR framework (Situation, Task, Action, Result) and think out loud during coding."
        }
        long_term_items.append(mock_item)

        total_skills_count = len(immediate_items) + len(short_term_items) + len(medium_term_items) + len(long_term_items)
        summary = (
            f"Personalized Learning Roadmap for target role '{target_role}' ({experience_level}). "
            f"Divided into 4 strategic phases covering {total_skills_count} key technical competencies, "
            f"practice projects, and interview tips."
        )

        # Save or update Roadmap in SQLite DB
        roadmap_record = db.query(Roadmap).filter(Roadmap.user_id == user_id).first()
        if not roadmap_record:
            roadmap_record = Roadmap(user_id=user_id)

        roadmap_record.target_role = target_role
        roadmap_record.experience_level = experience_level
        roadmap_record.total_skills_to_learn = total_skills_count
        roadmap_record.immediate_phase = immediate_items
        roadmap_record.short_term_phase = short_term_items
        roadmap_record.medium_term_phase = medium_term_items
        roadmap_record.long_term_phase = long_term_items
        roadmap_record.summary_notes = summary

        db.add(roadmap_record)
        db.commit()
        db.refresh(roadmap_record)

        return roadmap_record

    @staticmethod
    def get_user_roadmap(db: Session, user_id: int) -> Optional[Roadmap]:
        """
        Retrieves stored Roadmap record for user.
        """
        return db.query(Roadmap).filter(Roadmap.user_id == user_id).first()
