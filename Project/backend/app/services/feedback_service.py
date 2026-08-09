from typing import Dict, Any, List, Optional, Set
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone
import json
import os

from app.models.feedback import Feedback
from app.models.interview import InterviewQuestion, InterviewSession
from app.schemas.feedback import FeedbackResponse, AnswerSubmitRequest
from app.core.config import settings


class FeedbackService:
    """
    Service logic for evaluating interview question answers and generating feedback.
    Uses Gemini AI evaluation with rule-based fallback.
    """

    @staticmethod
    def evaluate_answer(
        question: InterviewQuestion,
        user_answer: str
    ) -> Dict[str, Any]:
        """
        Evaluates a user's answer against the expected question criteria.
        Returns a dictionary containing scores, strengths, weaknesses, and suggestions.
        
        Attempts Gemini AI evaluation first, falls back to rule-based evaluation if AI fails.
        """
        # Try Gemini AI evaluation first
        try:
            gemini_result = FeedbackService._evaluate_with_gemini(question, user_answer)
            if gemini_result:
                return gemini_result
        except Exception as e:
            # Log error and fall back to rule-based
            print(f"Gemini evaluation failed: {str(e)}")
        
        # Fallback to rule-based evaluation
        return FeedbackService._evaluate_with_rules(question, user_answer)
    
    @staticmethod
    def _evaluate_with_gemini(
        question: InterviewQuestion,
        user_answer: str
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluates answer using Gemini AI.
        Returns None if evaluation fails.
        """
        try:
            from google import genai
            
            api_key = os.getenv("GEMINI_API_KEY")
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            
            if not api_key:
                return None
            
            client = genai.Client(api_key=api_key)
            
            # Construct the prompt
            prompt = f"""
You are an expert interview evaluator. Evaluate the candidate's answer to an interview question.

QUESTION: {question.question_text}
CATEGORY: {question.category}
DIFFICULTY: {question.difficulty}

EXPECTED TOPICS: {', '.join(question.expected_topics or [])}
IDEAL ANSWER POINTS: {', '.join(question.ideal_answer_points or [])}
EVALUATION CRITERIA: {', '.join(question.evaluation_criteria or [])}

CANDIDATE ANSWER: {user_answer}

Please evaluate this answer and return ONLY a valid JSON object with this exact structure:
{{
    "score": <number 0-100>,
    "relevance_score": <number 0-100>,
    "technical_correctness": <number 0-100>,
    "completeness": <number 0-100>,
    "clarity": <number 0-100>,
    "strengths": ["strength1", "strength2", ...],
    "weaknesses": ["weakness1", "weakness2", ...],
    "suggestions": ["suggestion1", "suggestion2", ...],
    "ideal_answer": "concise ideal answer",
    "evaluation": "brief evaluation summary"
}}

Return ONLY the JSON, no other text.
"""
            
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            response_text = response.candidates[0].content.parts[0].text.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            evaluation_data = json.loads(response_text)
            
            # Validate and structure the response
            validated = FeedbackService._validate_gemini_response(evaluation_data, question)
            
            return validated
            
        except Exception as e:
            print(f"Gemini API error: {str(e)}")
            return None
    
    @staticmethod
    def _validate_gemini_response(
        data: Dict[str, Any],
        question: InterviewQuestion
    ) -> Dict[str, Any]:
        """
        Validates and structures Gemini response to match expected format.
        """
        # Ensure all required fields exist with proper types
        validated = {
            "score": float(data.get("score", 50.0)),
            "relevance_score": float(data.get("relevance_score", 50.0)),
            "technical_correctness": float(data.get("technical_correctness", 50.0)),
            "completeness": float(data.get("completeness", 50.0)),
            "clarity": float(data.get("clarity", 50.0)),
            "strengths": list(data.get("strengths", [])),
            "weaknesses": list(data.get("weaknesses", [])),
            "suggestions": list(data.get("suggestions", [])),
            "ideal_answer": str(data.get("ideal_answer", "")) or ". ".join(question.ideal_answer_points or []),
            "evaluation": str(data.get("evaluation", ""))
        }
        
        # Clamp scores to 0-100 range
        for score_field in ["score", "relevance_score", "technical_correctness", "completeness", "clarity"]:
            validated[score_field] = max(0.0, min(100.0, validated[score_field]))
        
        # Round scores to 1 decimal place
        for score_field in ["score", "relevance_score", "technical_correctness", "completeness", "clarity"]:
            validated[score_field] = round(validated[score_field], 1)
        
        # Ensure list fields are not empty
        if not validated["strengths"]:
            validated["strengths"] = ["Answer provided"]
        if not validated["weaknesses"]:
            validated["weaknesses"] = []
        if not validated["suggestions"]:
            validated["suggestions"] = []
        
        # Ensure evaluation is not empty
        if not validated["evaluation"]:
            validated["evaluation"] = FeedbackService._generate_evaluation_summary(
                validated["score"], question.category, question.difficulty
            )
        
        return validated
    
    @staticmethod
    def _evaluate_with_rules(
        question: InterviewQuestion,
        user_answer: str
    ) -> Dict[str, Any]:
        """
        Rule-based evaluation fallback.
        """
        user_answer_lower = user_answer.lower()
        expected_topics = [t.lower() for t in (question.expected_topics or [])]
        ideal_points = [p.lower() for p in (question.ideal_answer_points or [])]
        
        # Initialize scores
        relevance_score = 0.0
        technical_correctness = 0.0
        completeness = 0.0
        clarity = 0.0
        
        strengths: List[str] = []
        weaknesses: List[str] = []
        suggestions: List[str] = []
        
        # 1. Relevance Score: Check if answer addresses expected topics
        matched_topics = 0
        for topic in expected_topics:
            if topic in user_answer_lower:
                matched_topics += 1
        
        if expected_topics:
            relevance_score = (matched_topics / len(expected_topics)) * 100
        else:
            relevance_score = 50.0  # Default if no topics specified
        
        if relevance_score >= 75:
            strengths.append("Answer addresses most of the expected topics")
        elif relevance_score >= 50:
            strengths.append("Answer addresses some expected topics")
            suggestions.append("Try to cover more of the key topics mentioned in the question")
        else:
            weaknesses.append("Answer does not adequately address the expected topics")
            suggestions.append("Focus on the key topics and requirements of the question")
        
        # 2. Technical Correctness: Check for ideal answer points
        matched_points = 0
        for point in ideal_points:
            if any(word in user_answer_lower for word in point.split()[:3]):  # Check first 3 words
                matched_points += 1
        
        if ideal_points:
            technical_correctness = (matched_points / len(ideal_points)) * 100
        else:
            technical_correctness = 50.0
        
        if technical_correctness >= 75:
            strengths.append("Demonstrates good technical understanding")
        elif technical_correctness >= 50:
            strengths.append("Shows basic technical knowledge")
            suggestions.append("Include more specific technical details and examples")
        else:
            weaknesses.append("Technical details are missing or incorrect")
            suggestions.append("Review the technical concepts and include accurate details")
        
        # 3. Completeness: Check answer length and structure
        word_count = len(user_answer.split())
        if word_count >= 50:
            completeness = min(100.0, (word_count / 100) * 100)
        else:
            completeness = (word_count / 50) * 100
            weaknesses.append("Answer is too brief")
            suggestions.append("Provide more detailed explanations and examples")
        
        if completeness >= 70:
            strengths.append("Answer is comprehensive and well-structured")
        
        # 4. Clarity: Check for clear structure and communication
        # Check for structural indicators
        has_structure = any(indicator in user_answer_lower for indicator in 
                          ['first', 'second', 'finally', 'however', 'therefore', 'because', 'example'])
        if has_structure:
            clarity = 80.0
            strengths.append("Answer is well-structured and easy to follow")
        else:
            clarity = 60.0
            suggestions.append("Use clear structure with logical flow (e.g., first, second, therefore)")
        
        # Check for jargon overload (too many technical terms without explanation)
        technical_terms = ['api', 'sql', 'http', 'json', 'xml', 'oauth', 'jwt', 'rest', 'graphql']
        tech_term_count = sum(1 for term in technical_terms if term in user_answer_lower)
        if tech_term_count > 5 and word_count < 100:
            clarity -= 20
            weaknesses.append("Heavy use of technical terms without sufficient explanation")
        
        clarity = max(0.0, min(100.0, clarity))
        
        # Calculate overall score (weighted average)
        overall_score = (
            relevance_score * 0.3 +
            technical_correctness * 0.35 +
            completeness * 0.2 +
            clarity * 0.15
        )
        
        # Generate evaluation summary
        evaluation_summary = FeedbackService._generate_evaluation_summary(
            overall_score, question.category, question.difficulty
        )
        
        # Generate ideal answer (from the stored ideal points)
        ideal_answer = ". ".join(question.ideal_answer_points) if question.ideal_answer_points else None
        
        return {
            "score": round(overall_score, 1),
            "relevance_score": round(relevance_score, 1),
            "technical_correctness": round(technical_correctness, 1),
            "completeness": round(completeness, 1),
            "clarity": round(clarity, 1),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "suggestions": suggestions,
            "ideal_answer": ideal_answer,
            "evaluation": evaluation_summary
        }
    
    @staticmethod
    def _generate_evaluation_summary(score: float, category: str, difficulty: str) -> str:
        """
        Generates a qualitative evaluation summary based on the score and question context.
        """
        if score >= 85:
            return f"Excellent {category} answer. Demonstrates strong understanding of {difficulty} level concepts."
        elif score >= 70:
            return f"Good {category} answer. Shows solid understanding with minor areas for improvement."
        elif score >= 50:
            return f"Adequate {category} answer. Covers basic concepts but needs more depth and detail for {difficulty} level."
        elif score >= 30:
            return f"Basic {category} answer. Identifies key concepts but lacks technical depth and completeness."
        else:
            return f"Insufficient {category} answer. Missing key concepts and technical details required for {difficulty} level."
    
    @staticmethod
    def create_feedback(
        db: Session,
        user_id: int,
        session_id: int,
        question_id: int,
        evaluation: Dict[str, Any]
    ) -> Feedback:
        """
        Creates and persists a Feedback record in the database.
        """
        feedback = Feedback(
            user_id=user_id,
            session_id=session_id,
            question_id=question_id,
            score=evaluation["score"],
            relevance_score=evaluation["relevance_score"],
            technical_correctness=evaluation["technical_correctness"],
            completeness=evaluation["completeness"],
            clarity=evaluation["clarity"],
            strengths=evaluation["strengths"],
            weaknesses=evaluation["weaknesses"],
            suggestions=evaluation["suggestions"],
            ideal_answer=evaluation["ideal_answer"],
            evaluation=evaluation["evaluation"]
        )
        
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback
    
    @staticmethod
    def get_feedback_by_question(db: Session, question_id: int) -> Optional[Feedback]:
        """
        Retrieves feedback for a specific question.
        """
        return db.query(Feedback).filter(Feedback.question_id == question_id).first()
    
    @staticmethod
    def get_session_feedback(db: Session, session_id: int) -> List[Feedback]:
        """
        Retrieves all feedback for questions in a specific session.
        """
        return db.query(Feedback).filter(Feedback.session_id == session_id).all()
    
    @staticmethod
    def calculate_interview_summary(
        feedback_list: List[Feedback],
        total_questions: int
    ) -> Dict[str, Any]:
        """
        Calculates overall interview summary from individual question feedback.
        """
        if not feedback_list:
            return {
                "overall_score": 0.0,
                "overall_strengths": [],
                "overall_weaknesses": [],
                "recommendations": ["No feedback available"]
            }
        
        # Calculate average scores
        avg_score = sum(f.score for f in feedback_list) / len(feedback_list)
        avg_relevance = sum(f.relevance_score for f in feedback_list) / len(feedback_list)
        avg_technical = sum(f.technical_correctness for f in feedback_list) / len(feedback_list)
        avg_completeness = sum(f.completeness for f in feedback_list) / len(feedback_list)
        avg_clarity = sum(f.clarity for f in feedback_list) / len(feedback_list)
        
        # Aggregate strengths and weaknesses
        all_strengths: List[str] = []
        all_weaknesses: List[str] = []
        all_suggestions: List[str] = []
        
        for feedback in feedback_list:
            all_strengths.extend(feedback.strengths)
            all_weaknesses.extend(feedback.weaknesses)
            all_suggestions.extend(feedback.suggestions)
        
        # Get unique items and limit to top items
        unique_strengths = list(set(all_strengths))[:5]
        unique_weaknesses = list(set(all_weaknesses))[:5]
        unique_suggestions = list(set(all_suggestions))[:5]
        
        # Generate overall assessment
        if avg_score >= 80:
            overall_assessment = "Strong performance across all areas. Ready for advanced interview preparation."
        elif avg_score >= 60:
            overall_assessment = "Good performance with room for improvement in technical depth and completeness."
        elif avg_score >= 40:
            overall_assessment = "Adequate performance. Focus on strengthening technical fundamentals and communication."
        else:
            overall_assessment = "Needs significant improvement. Focus on core concepts and structured communication."
        
        return {
            "overall_score": round(avg_score, 1),
            "average_relevance": round(avg_relevance, 1),
            "average_technical": round(avg_technical, 1),
            "average_completeness": round(avg_completeness, 1),
            "average_clarity": round(avg_clarity, 1),
            "overall_strengths": unique_strengths,
            "overall_weaknesses": unique_weaknesses,
            "recommendations": unique_suggestions,
            "overall_assessment": overall_assessment
        }