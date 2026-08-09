import random
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.interview import InterviewSession, InterviewQuestion
from app.services.student_profile_service import StudentProfileService
from app.services.resume_analysis_service import ResumeAnalysisService
from app.services.skill_gap_service import SkillGapService
from app.services.feedback_service import FeedbackService
from app.schemas.interview import QuestionGenerateRequest


class InterviewService:
    """
    AI Interview Question Generator service logic.
    Dynamically generates personalized interview questions using candidate profile,
    resume analysis, skill gaps, and target role context.
    """

    @staticmethod
    def generate_question_templates(
        role: str,
        level: str,
        extracted_skills: List[str],
        missing_skills: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Synthesizes dynamic questions across Technical, Coding, Behavioral, Scenario-Based, and HR categories.
        """
        primary_tech = extracted_skills[0] if extracted_skills else "Python"
        second_tech = extracted_skills[1] if len(extracted_skills) > 1 else "SQL"
        target_gap_skill = missing_skills[0] if missing_skills else "System Design"

        templates = [
            # 1. TECHNICAL QUESTION (Easy/Medium/Hard)
            {
                "question_text": f"How does memory management and async request handling work in {primary_tech}? Explain with practical examples relevant to {role}.",
                "category": "Technical",
                "difficulty": "Medium" if "Senior" not in level else "Hard",
                "expected_topics": [primary_tech, "Memory Management", "Concurrency", "Event Loop", "Performance Optimization"],
                "ideal_answer_points": [
                    f"Explanation of {primary_tech}'s memory allocation and garbage collection mechanism.",
                    "Difference between synchronous blocking vs asynchronous non-blocking event loops.",
                    f"Real-world application for handling high-concurrency requests in a {role} context."
                ],
                "evaluation_criteria": [
                    "Technical accuracy regarding language internals.",
                    "Clarity in explaining async execution flow.",
                    "Mention of real-world performance considerations."
                ],
                "estimated_time_minutes": 5
            },

            # 2. CODING QUESTION (Easy/Medium/Hard)
            {
                "question_text": f"Design an efficient function in {primary_tech} to parse and deduplicate log records using {second_tech} or in-memory data structures. Optimize for O(N) time complexity.",
                "category": "Coding",
                "difficulty": "Medium",
                "expected_topics": ["Data Structures", "Time Complexity O(N)", primary_tech, "Algorithmic Efficiency"],
                "ideal_answer_points": [
                    f"Choice of hash set or dict data structure in {primary_tech} for O(1) lookup.",
                    "Single pass iteration over log stream to maintain O(N) runtime.",
                    "Proper error handling for malformed log entries."
                ],
                "evaluation_criteria": [
                    "Correctness of data structure selection.",
                    "Time and space complexity optimal trade-offs.",
                    "Clean code formatting and edge-case handling."
                ],
                "estimated_time_minutes": 10
            },

            # 3. SCENARIO-BASED QUESTION
            {
                "question_text": f"You are tasked with introducing {target_gap_skill} into an existing legacy architecture for a {role} project. How would you plan this migration without downtime?",
                "category": "Scenario-Based",
                "difficulty": "Hard",
                "expected_topics": [target_gap_skill, "System Migration", "Zero Downtime", "Risk Mitigation", "Architecture"],
                "ideal_answer_points": [
                    "Phased rollout strategy (e.g. dual writing or feature flag toggles).",
                    "Monitoring key metrics (latency, error rates) during transition.",
                    "Rollback plan in case of unexpected performance degradation."
                ],
                "evaluation_criteria": [
                    "Pragmatic architectural decision making.",
                    "Risk awareness and zero-downtime strategy.",
                    "Structured step-by-step migration approach."
                ],
                "estimated_time_minutes": 7
            },

            # 4. BEHAVIORAL QUESTION
            {
                "question_text": f"Describe a challenging bug or production incident you faced while working with {primary_tech} or {second_tech}. How did you diagnose and resolve it?",
                "category": "Behavioral",
                "difficulty": "Easy" if "Entry" in level else "Medium",
                "expected_topics": ["Problem Solving", "Incident Response", "Debugging", "Communication", "Post-Mortem"],
                "ideal_answer_points": [
                    "Clear STAR format (Situation, Task, Action, Result).",
                    "Methodical debugging approach (analyzing logs, reproducing issue).",
                    "Long-term preventive measure implemented after resolution."
                ],
                "evaluation_criteria": [
                    "Use of STAR framework in response.",
                    "Methodical problem-solving approach.",
                    "Ownership and learning from past incidents."
                ],
                "estimated_time_minutes": 5
            },

            # 5. HR / CULTURAL FIT QUESTION
            {
                "question_text": f"Why are you interested in advancing your career as a {role}, and how do you stay updated with rapid technological developments in backend/cloud tools?",
                "category": "HR",
                "difficulty": "Easy",
                "expected_topics": ["Career Goals", "Continuous Learning", "Culture Fit", "Professional Motivation"],
                "ideal_answer_points": [
                    f"Genuine motivation and passion for the {role} domain.",
                    "Concrete habits for continuous learning (open-source contributions, technical blogs, courses).",
                    "Alignment of personal career growth with team goals."
                ],
                "evaluation_criteria": [
                    "Articulate communication and enthusiasm.",
                    "Concrete examples of self-directed learning.",
                    "Strong alignment with target role."
                ],
                "estimated_time_minutes": 3
            },

            # 6. ADDITIONAL TECHNICAL QUESTION
            {
                "question_text": f"Explain the differences between SQL relational databases (e.g. PostgreSQL) and NoSQL stores (e.g. MongoDB or Redis) when architecting a system for a {role}.",
                "category": "Technical",
                "difficulty": "Medium",
                "expected_topics": ["Databases", "SQL vs NoSQL", "ACID Compliance", "CAP Theorem", "Schema Design"],
                "ideal_answer_points": [
                    "ACID transactions and strict schemas in SQL vs horizontal scaling in NoSQL.",
                    "Use case analysis: complex joins/financial data vs fast document key-value lookup.",
                    "Trade-offs regarding consistency vs availability."
                ],
                "evaluation_criteria": [
                    "Depth of database knowledge.",
                    "Clear trade-off analysis.",
                    "Appropriate recommendation based on requirements."
                ],
                "estimated_time_minutes": 5
            },

            # 7. ADDITIONAL CODING / SYSTEM QUESTION
            {
                "question_text": f"How would you implement secure JWT-based authentication and permission middleware in {primary_tech}? Highlight password hashing and token validation.",
                "category": "Coding",
                "difficulty": "Medium",
                "expected_topics": ["JWT Authentication", "Security", "Password Hashing (bcrypt)", "Middleware", primary_tech],
                "ideal_answer_points": [
                    "Use of bcrypt/argon2 for salt-hashed password storage.",
                    "Cryptographic signing of JWT payloads with access and refresh expiry.",
                    "Middleware validation of Authorization Bearer headers."
                ],
                "evaluation_criteria": [
                    "Security best practices awareness.",
                    "Proper token lifecycle understanding.",
                    "Implementation clarity."
                ],
                "estimated_time_minutes": 8
            }
        ]

        return templates

    @staticmethod
    def generate_questions_for_user(
        db: Session,
        user_id: int,
        req: QuestionGenerateRequest
    ) -> InterviewSession:
        """
        Generates personalized interview questions, creates a new InterviewSession,
        stores child InterviewQuestion records in SQLite, and returns the session object.
        """
        # 1. Fetch Student Profile for target role
        profile = StudentProfileService.get_by_user_id(db, user_id=user_id)
        if not profile or not profile.target_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target role not selected yet. Please select a target role first."
            )

        target_role = profile.target_role
        experience_level = profile.experience_level or "Entry Level"

        # 2. Fetch Resume Analysis
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

        extracted_skills = (
            (resume_analysis.programming_languages or []) +
            (resume_analysis.frameworks or []) +
            (resume_analysis.technical_skills or [])
        )
        missing_skills = skill_gap.missing_skills or []

        # 4. Generate dynamic question templates
        all_templates = InterviewService.generate_question_templates(
            role=target_role,
            level=experience_level,
            extracted_skills=extracted_skills,
            missing_skills=missing_skills
        )

        num_q = req.num_questions if req.num_questions else 5
        selected_templates = all_templates[:num_q]

        # Override difficulty if user specifically requested a fixed difficulty
        if req.difficulty:
            for t in selected_templates:
                t["difficulty"] = req.difficulty

        # 5. Create InterviewSession in SQLite DB
        session = InterviewSession(
            user_id=user_id,
            target_role=target_role,
            experience_level=experience_level,
            total_questions=len(selected_templates),
            status="generated"
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        # 6. Create child InterviewQuestion objects
        for tmpl in selected_templates:
            q_obj = InterviewQuestion(
                session_id=session.id,
                question_text=tmpl["question_text"],
                category=tmpl["category"],
                difficulty=tmpl["difficulty"],
                expected_topics=tmpl["expected_topics"],
                ideal_answer_points=tmpl["ideal_answer_points"],
                evaluation_criteria=tmpl["evaluation_criteria"],
                estimated_time_minutes=tmpl["estimated_time_minutes"]
            )
            db.add(q_obj)

        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_user_latest_interview(db: Session, user_id: int) -> Optional[InterviewSession]:
        """
        Retrieves the latest generated interview session for the user.
        """
        return db.query(InterviewSession).filter(
            InterviewSession.user_id == user_id
        ).order_by(InterviewSession.id.desc()).first()

    @staticmethod
    def get_question_by_id(db: Session, question_id: int) -> Optional[InterviewQuestion]:
        """
        Retrieves a specific interview question by ID.
        """
        return db.query(InterviewQuestion).filter(InterviewQuestion.id == question_id).first()

    @staticmethod
    def submit_answer(
        db: Session,
        user_id: int,
        question_id: int,
        user_answer: str
    ) -> Dict[str, Any]:
        """
        Submits a user's answer to an interview question, evaluates it, and stores feedback.
        """
        # 1. Verify question exists and belongs to user's session
        question = InterviewService.get_question_by_id(db, question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )

        # 2. Verify session ownership
        session = db.query(InterviewSession).filter(
            InterviewSession.id == question.session_id,
            InterviewSession.user_id == user_id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this question"
            )

        # 3. Update question with user answer
        question.user_answer = user_answer
        question.answered_at = datetime.now(timezone.utc)
        
        # 4. Update session status and answered count
        if session.status == "generated":
            session.status = "in_progress"
            session.start_time = datetime.now(timezone.utc)
        
        # Count answered questions
        answered_count = db.query(InterviewQuestion).filter(
            InterviewQuestion.session_id == session.id,
            InterviewQuestion.user_answer.isnot(None)
        ).count()
        
        session.answered_questions_count = answered_count
        db.add(question)
        db.add(session)
        db.commit()
        db.refresh(question)
        db.refresh(session)

        # 5. Evaluate the answer
        evaluation = FeedbackService.evaluate_answer(question, user_answer)
        
        # 6. Create and store feedback
        feedback = FeedbackService.create_feedback(
            db=db,
            user_id=user_id,
            session_id=session.id,
            question_id=question_id,
            evaluation=evaluation
        )

        return {
            "question_id": question_id,
            "session_id": session.id,
            "user_answer": user_answer,
            "answered_at": question.answered_at,
            "feedback": feedback
        }

    @staticmethod
    def complete_session(
        db: Session,
        user_id: int,
        session_id: int
    ) -> Dict[str, Any]:
        """
        Completes an interview session, calculates overall scores, and returns summary.
        """
        # 1. Verify session exists and belongs to user
        session = db.query(InterviewSession).filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == user_id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found"
            )

        # 2. Check if all questions are answered
        total_questions = len(session.questions)
        answered_questions = sum(1 for q in session.questions if q.user_answer)
        
        if answered_questions < total_questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot complete session. {total_questions - answered_questions} question(s) still unanswered"
            )

        # 3. Get all feedback for the session
        feedback_list = FeedbackService.get_session_feedback(db, session_id)
        
        # 4. Calculate interview summary
        summary = FeedbackService.calculate_interview_summary(feedback_list, total_questions)
        
        # 5. Update session status and timing
        session.status = "completed"
        session.end_time = datetime.now(timezone.utc)
        
        if session.start_time:
            # Ensure both datetimes are timezone-aware
            if session.start_time.tzinfo is None:
                start_time = session.start_time.replace(tzinfo=timezone.utc)
            else:
                start_time = session.start_time
            duration = (session.end_time - start_time).total_seconds()
            session.total_duration_seconds = int(duration)
        
        db.add(session)
        db.commit()
        db.refresh(session)

        return {
            "session_id": session.id,
            "user_id": session.user_id,
            "target_role": session.target_role,
            "experience_level": session.experience_level,
            "overall_score": summary["overall_score"],
            "total_questions": total_questions,
            "answered_questions": answered_questions,
            "completed_at": session.end_time,
            "duration_seconds": session.total_duration_seconds,
            "overall_strengths": summary["overall_strengths"],
            "overall_weaknesses": summary["overall_weaknesses"],
            "recommendations": summary["recommendations"],
            "feedback_summary": feedback_list,
            "overall_assessment": summary["overall_assessment"]
        }

    @staticmethod
    def get_session_feedback(
        db: Session,
        user_id: int,
        session_id: int
    ) -> List:
        """
        Retrieves all feedback for a completed interview session.
        """
        # Verify session ownership
        session = db.query(InterviewSession).filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == user_id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found"
            )

        return FeedbackService.get_session_feedback(db, session_id)
