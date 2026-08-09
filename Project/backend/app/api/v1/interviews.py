from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.interview import QuestionGenerateRequest, InterviewSessionResponse
from app.schemas.feedback import AnswerSubmitRequest, AnswerSubmitResponse, InterviewCompletionResponse, FeedbackResponse
from app.services.interview_service import InterviewService
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/interview", tags=["AI Interview Generator"])


@router.post("/questions/generate", response_model=InterviewSessionResponse, status_code=status.HTTP_201_CREATED)
def generate_interview_questions(
    req: QuestionGenerateRequest = QuestionGenerateRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Dynamically generates personalized AI interview questions using Candidate Profile,
    Resume Analysis, Skill Gap Analysis, and Selected Target Role context.

    Includes question categories:
    - Technical
    - Coding
    - Behavioral
    - Scenario-Based
    - HR

    Each question includes:
    - question text
    - category & difficulty (Easy, Medium, Hard)
    - expected_topics
    - ideal_answer_points
    - evaluation_criteria
    - estimated_time_minutes

    Stores the generated interview session in SQLite database.
    """
    return InterviewService.generate_questions_for_user(db=db, user_id=current_user.id, req=req)


@router.get("/questions", response_model=InterviewSessionResponse)
def get_interview_questions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve existing stored interview session and questions for the authenticated user.
    """
    session = InterviewService.get_user_latest_interview(db=db, user_id=current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No interview session found. Please generate questions first using POST /api/v1/interview/questions/generate."
        )
    return session


@router.post("/questions/{question_id}/answer", response_model=AnswerSubmitResponse, status_code=status.HTTP_200_OK)
def submit_question_answer(
    question_id: int,
    answer_request: AnswerSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Submit an answer to a specific interview question.
    
    The endpoint:
    - Requires authentication
    - Verifies the question belongs to the authenticated user's interview session
    - Accepts the user's answer
    - Validates that the answer is not empty
    - Persists the answer into InterviewQuestion.user_answer
    - Evaluates the answer and generates feedback
    - Prevents unauthorized access to another user's question
    - Returns the submitted answer and evaluation result
    """
    result = InterviewService.submit_answer(
        db=db,
        user_id=current_user.id,
        question_id=question_id,
        user_answer=answer_request.user_answer
    )
    
    return AnswerSubmitResponse(
        question_id=result["question_id"],
        session_id=result["session_id"],
        user_answer=result["user_answer"],
        answered_at=result["answered_at"],
        feedback=result["feedback"],
        message="Answer submitted successfully"
    )


@router.post("/{session_id}/complete", response_model=InterviewCompletionResponse, status_code=status.HTTP_200_OK)
def complete_interview_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Complete an interview session and generate overall evaluation.
    
    The endpoint:
    - Requires authentication
    - Verifies session ownership
    - Ensures questions have been answered
    - Calculates overall interview score
    - Marks the session as completed
    - Returns overall score, strengths, weaknesses, recommendations, and per-question feedback
    """
    result = InterviewService.complete_session(
        db=db,
        user_id=current_user.id,
        session_id=session_id
    )
    
    return InterviewCompletionResponse(
        session_id=result["session_id"],
        user_id=result["user_id"],
        target_role=result["target_role"],
        experience_level=result["experience_level"],
        overall_score=result["overall_score"],
        total_questions=result["total_questions"],
        answered_questions=result["answered_questions"],
        completed_at=result["completed_at"],
        duration_seconds=result["duration_seconds"],
        overall_strengths=result["overall_strengths"],
        overall_weaknesses=result["overall_weaknesses"],
        recommendations=result["recommendations"],
        feedback_summary=result["feedback_summary"],
        message="Interview completed successfully"
    )


@router.get("/{session_id}/feedback", response_model=list[FeedbackResponse])
def get_interview_feedback(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve detailed feedback for a completed interview session.
    
    Returns all question-level evaluations including scores, strengths, weaknesses,
    and suggestions for improvement.
    """
    feedback_list = InterviewService.get_session_feedback(
        db=db,
        user_id=current_user.id,
        session_id=session_id
    )
    
    if not feedback_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No feedback found for this session. Please complete the interview first."
        )
    
    return feedback_list
