from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.interview import InterviewSession
from app.models.learning_progress import LearningProgress
from app.models.skill_gap import SkillGapAnalysis
from app.models.roadmap import Roadmap


class ReadinessService:
    """
    Service logic for calculating interview readiness score.
    """

    @staticmethod
    def calculate_readiness_score(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Calculates overall interview readiness score from existing data.
        
        Weights:
        - Interview performance: 40%
        - Learning progress: 30%
        - Skill gap: 20%
        - Roadmap completion: 10%
        """
        breakdown = {
            "interview_performance": 0.0,
            "learning_progress": 0.0,
            "skill_gap": 0.0,
            "roadmap_completion": 0.0
        }
        
        # 1. Interview Performance (40%)
        # Use the latest completed interview session's average score
        latest_session = db.query(InterviewSession).filter(
            InterviewSession.user_id == user_id,
            InterviewSession.status == "completed"
        ).order_by(InterviewSession.id.desc()).first()
        
        if latest_session:
            # Get feedback for this session
            from app.models.feedback import Feedback
            feedback_list = db.query(Feedback).filter(
                Feedback.session_id == latest_session.id
            ).all()
            
            if feedback_list:
                avg_score = sum(f.score for f in feedback_list) / len(feedback_list)
                breakdown["interview_performance"] = avg_score
            else:
                # If no feedback, use answered questions count as a proxy
                if latest_session.total_questions > 0:
                    completion_rate = (latest_session.answered_questions_count / latest_session.total_questions) * 100
                    breakdown["interview_performance"] = completion_rate
        
        # 2. Learning Progress (30%)
        # Average progress percentage across all tracked skills
        progress_entries = db.query(LearningProgress).filter(
            LearningProgress.user_id == user_id
        ).all()
        
        if progress_entries:
            avg_progress = sum(p.progress_percentage for p in progress_entries) / len(progress_entries)
            breakdown["learning_progress"] = avg_progress
        
        # 3. Skill Gap (20%)
        # Use the match percentage from skill gap analysis
        skill_gap = db.query(SkillGapAnalysis).filter(
            SkillGapAnalysis.user_id == user_id
        ).first()
        
        if skill_gap:
            breakdown["skill_gap"] = skill_gap.match_percentage
        
        # 4. Roadmap Completion (10%)
        # Estimate based on total skills to learn vs current progress
        roadmap = db.query(Roadmap).filter(
            Roadmap.user_id == user_id
        ).first()
        
        if roadmap:
            if roadmap.total_skills_to_learn > 0:
                # Assume some completion based on learning progress
                if progress_entries:
                    completion = min(100.0, (len(progress_entries) / roadmap.total_skills_to_learn) * 100)
                    breakdown["roadmap_completion"] = completion
                else:
                    breakdown["roadmap_completion"] = 0.0
            else:
                breakdown["roadmap_completion"] = 0.0
        
        # Calculate weighted overall score
        overall_score = (
            breakdown["interview_performance"] * 0.40 +
            breakdown["learning_progress"] * 0.30 +
            breakdown["skill_gap"] * 0.20 +
            breakdown["roadmap_completion"] * 0.10
        )
        
        # Derive performance level
        if overall_score >= 85:
            performance_level = "Interview Ready"
        elif overall_score >= 70:
            performance_level = "Good"
        elif overall_score >= 40:
            performance_level = "Developing"
        else:
            performance_level = "Needs Improvement"
        
        return {
            "readiness_score": round(overall_score, 1),
            "performance_level": performance_level,
            "breakdown": breakdown
        }