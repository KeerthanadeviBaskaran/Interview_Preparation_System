from fastapi.testclient import TestClient
from main import app
import time
import uuid

client = TestClient(app)

def test_complete_interview_flow():
    """Test the complete interview flow from generation to completion."""
    
    # 1. Register & Login user
    unique_id = str(uuid.uuid4())[:8]
    register_res = client.post('/api/v1/auth/register', json={
        'email': f'flow_user_{unique_id}@example.com', 
        'password': 'FlowPass123!', 
        'full_name': 'Flow Tester'
    })
    assert register_res.status_code == 201
    
    token_res = client.post('/api/v1/auth/login', json={
        'email': f'flow_user_{unique_id}@example.com', 
        'password': 'FlowPass123!'
    })
    tokens = token_res.json()
    headers = {'Authorization': 'Bearer ' + tokens['access_token']}
    
    # 2. Select Target Role
    res_role = client.post('/api/v1/role/me', json={
        'target_role': 'Backend Engineer', 
        'experience_level': 'Mid Level'
    }, headers=headers)
    assert res_role.status_code == 200
    print("[OK] Role selected successfully")
    
    # 3. Upload PDF Resume
    sample_pdf_bytes = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n4 0 obj\n<< /Length 200 >>\nstream\nBT\n/F1 12 Tf\n50 700 Td\n(Backend Engineer skilled in Python, FastAPI, SQL, PostgreSQL, REST API, Redis, and Docker.) Tj\nET\nendstream\nendobj\n5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000238 00000 n \n0000000488 00000 n \ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n565\n%%EOF'
    
    res_upload = client.post('/api/v1/resume/upload', files={
        'file': ('backend_resume.pdf', sample_pdf_bytes, 'application/pdf')
    }, headers=headers)
    assert res_upload.status_code == 201
    print("[OK] Resume uploaded successfully")
    
    # 4. Analyze Resume
    res_analyze = client.post('/api/v1/resume/analyze', headers=headers)
    assert res_analyze.status_code == 200
    print("[OK] Resume analyzed successfully")
    
    # 5. Generate Interview Questions
    res_gen = client.post('/api/v1/interview/questions/generate', json={
        'num_questions': 3
    }, headers=headers)
    assert res_gen.status_code == 201
    session_data = res_gen.json()
    session_id = session_data['id']
    questions = session_data['questions']
    assert len(questions) == 3
    print(f"[OK] Generated {len(questions)} interview questions")
    
    # 6. Test submitting empty answer (should fail)
    first_question_id = questions[0]['id']
    res_empty = client.post(f'/api/v1/interview/questions/{first_question_id}/answer', json={
        'user_answer': ''
    }, headers=headers)
    assert res_empty.status_code == 422  # Validation error
    print("[OK] Empty answer rejected correctly")
    
    # 7. Test accessing another user's question (should fail)
    # Create another user
    other_unique_id = str(uuid.uuid4())[:8]
    client.post('/api/v1/auth/register', json={
        'email': f'other_user_{other_unique_id}@example.com', 
        'password': 'OtherPass123!', 
        'full_name': 'Other User'
    })
    other_token_res = client.post('/api/v1/auth/login', json={
        'email': f'other_user_{other_unique_id}@example.com', 
        'password': 'OtherPass123!'
    })
    other_tokens = other_token_res.json()
    other_headers = {'Authorization': 'Bearer ' + other_tokens['access_token']}
    
    res_unauthorized = client.post(f'/api/v1/interview/questions/{first_question_id}/answer', json={
        'user_answer': 'This is an unauthorized answer'
    }, headers=other_headers)
    assert res_unauthorized.status_code == 403
    print("[OK] Unauthorized access rejected correctly")
    
    # 8. Submit valid answers to all questions
    for i, question in enumerate(questions):
        question_id = question['id']
        answer_text = f"This is my answer to question {i+1}. I understand the concepts of Python, FastAPI, and database systems. The answer addresses the expected topics and provides technical details with examples."
        
        res_answer = client.post(f'/api/v1/interview/questions/{question_id}/answer', json={
            'user_answer': answer_text
        }, headers=headers)
        assert res_answer.status_code == 200
        
        answer_data = res_answer.json()
        assert 'feedback' in answer_data
        assert answer_data['feedback']['score'] >= 0.0
        assert answer_data['feedback']['score'] <= 100.0
        assert 'strengths' in answer_data['feedback']
        assert 'weaknesses' in answer_data['feedback']
        assert 'suggestions' in answer_data['feedback']
        print(f"[OK] Answer {i+1} submitted and evaluated (score: {answer_data['feedback']['score']})")
    
    # Add a small delay to ensure session duration > 0
    time.sleep(0.1)
    
    # 9. Test completing session with unanswered questions (should fail)
    # Generate a new session with more questions
    res_gen2 = client.post('/api/v1/interview/questions/generate', json={
        'num_questions': 2
    }, headers=headers)
    session2_data = res_gen2.json()
    session2_id = session2_data['id']
    
    # Answer only one question
    first_q_id = session2_data['questions'][0]['id']
    client.post(f'/api/v1/interview/questions/{first_q_id}/answer', json={
        'user_answer': 'Partial answer'
    }, headers=headers)
    
    # Try to complete incomplete session
    res_incomplete = client.post(f'/api/v1/interview/{session2_id}/complete', headers=headers)
    assert res_incomplete.status_code == 400
    print("[OK] Incomplete session completion rejected correctly")
    
    # 10. Complete the first session successfully
    res_complete = client.post(f'/api/v1/interview/{session_id}/complete', headers=headers)
    assert res_complete.status_code == 200
    
    completion_data = res_complete.json()
    assert completion_data['session_id'] == session_id
    assert completion_data['overall_score'] >= 0.0
    assert completion_data['overall_score'] <= 100.0
    assert completion_data['total_questions'] == 3
    assert completion_data['answered_questions'] == 3
    assert 'overall_strengths' in completion_data
    assert 'overall_weaknesses' in completion_data
    assert 'recommendations' in completion_data
    assert 'feedback_summary' in completion_data
    assert len(completion_data['feedback_summary']) == 3
    print(f"[OK] Session completed successfully (overall score: {completion_data['overall_score']})")
    
    # 11. Retrieve feedback for completed session
    res_feedback = client.get(f'/api/v1/interview/{session_id}/feedback', headers=headers)
    assert res_feedback.status_code == 200
    
    feedback_list = res_feedback.json()
    assert len(feedback_list) == 3
    for feedback in feedback_list:
        assert 'score' in feedback
        assert 'relevance_score' in feedback
        assert 'technical_correctness' in feedback
        assert 'completeness' in feedback
        assert 'clarity' in feedback
        assert 'strengths' in feedback
        assert 'weaknesses' in feedback
        assert 'suggestions' in feedback
    print("[OK] Feedback retrieved successfully")
    
    # 12. Test accessing another user's session feedback (should fail)
    res_unauthorized_feedback = client.get(f'/api/v1/interview/{session_id}/feedback', headers=other_headers)
    assert res_unauthorized_feedback.status_code == 404
    print("[OK] Unauthorized feedback access rejected correctly")
    
    # 13. Test session timing
    assert 'duration_seconds' in completion_data
    # Duration might be 0 if completed very quickly, but should not be None
    assert completion_data['duration_seconds'] is not None
    assert completion_data['duration_seconds'] >= 0
    print(f"[OK] Session timing tracked correctly ({completion_data['duration_seconds']} seconds)")
    
    print("\n=== COMPLETE INTERVIEW FLOW TEST PASSED ===")


def test_answer_persistence():
    """Test that answers are properly persisted in the database."""
    
    # 1. Register & Login
    unique_id = str(uuid.uuid4())[:8]
    client.post('/api/v1/auth/register', json={
        'email': f'persist_user_{unique_id}@example.com', 
        'password': 'PersistPass123!', 
        'full_name': 'Persistence Tester'
    })
    token_res = client.post('/api/v1/auth/login', json={
        'email': f'persist_user_{unique_id}@example.com', 
        'password': 'PersistPass123!'
    })
    headers = {'Authorization': 'Bearer ' + token_res.json()['access_token']}
    
    # 2. Setup interview
    client.post('/api/v1/role/me', json={
        'target_role': 'Backend Engineer', 
        'experience_level': 'Mid Level'
    }, headers=headers)
    
    sample_pdf = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n4 0 obj\n<< /Length 200 >>\nstream\nBT\n/F1 12 Tf\n50 700 Td\n(Python Developer with FastAPI and SQL experience.) Tj\nET\nendstream\nendobj\n5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000238 00000 n \n0000000488 00000 n \ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n565\n%%EOF'
    
    client.post('/api/v1/resume/upload', files={
        'file': ('resume.pdf', sample_pdf, 'application/pdf')
    }, headers=headers)
    client.post('/api/v1/resume/analyze', headers=headers)
    
    # 3. Generate questions
    res_gen = client.post('/api/v1/interview/questions/generate', json={
        'num_questions': 1
    }, headers=headers)
    question_id = res_gen.json()['questions'][0]['id']
    
    # 4. Submit answer
    test_answer = "This is a detailed answer about Python memory management and async handling."
    res_answer = client.post(f'/api/v1/interview/questions/{question_id}/answer', json={
        'user_answer': test_answer
    }, headers=headers)
    assert res_answer.status_code == 200
    
    # 5. Retrieve questions and verify answer persistence
    res_get = client.get('/api/v1/interview/questions', headers=headers)
    questions = res_get.json()['questions']
    assert questions[0]['user_answer'] == test_answer
    assert questions[0]['answered_at'] is not None
    
    print("[OK] Answer persistence verified")


def test_evaluation_response_structure():
    """Test that evaluation response has the correct structure."""
    
    # 1. Setup
    unique_id = str(uuid.uuid4())[:8]
    client.post('/api/v1/auth/register', json={
        'email': f'eval_user_{unique_id}@example.com', 
        'password': 'EvalPass123!', 
        'full_name': 'Evaluation Tester'
    })
    token_res = client.post('/api/v1/auth/login', json={
        'email': f'eval_user_{unique_id}@example.com', 
        'password': 'EvalPass123!'
    })
    headers = {'Authorization': 'Bearer ' + token_res.json()['access_token']}
    
    client.post('/api/v1/role/me', json={
        'target_role': 'Backend Engineer', 
        'experience_level': 'Mid Level'
    }, headers=headers)
    
    sample_pdf = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n4 0 obj\n<< /Length 200 >>\nstream\nBT\n/F1 12 Tf\n50 700 Td\n(Python Developer with FastAPI and SQL experience.) Tj\nET\nendstream\nendobj\n5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000238 00000 n \n0000000488 00000 n \ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n565\n%%EOF'
    
    client.post('/api/v1/resume/upload', files={
        'file': ('resume.pdf', sample_pdf, 'application/pdf')
    }, headers=headers)
    client.post('/api/v1/resume/analyze', headers=headers)
    
    # 2. Generate and answer
    res_gen = client.post('/api/v1/interview/questions/generate', json={
        'num_questions': 1
    }, headers=headers)
    question_id = res_gen.json()['questions'][0]['id']
    
    res_answer = client.post(f'/api/v1/interview/questions/{question_id}/answer', json={
        'user_answer': 'Python uses reference counting for memory management. Async handling uses event loops for non-blocking I/O operations. This is important for high-performance web applications.'
    }, headers=headers)
    
    feedback = res_answer.json()['feedback']
    
    # 3. Verify response structure
    required_fields = [
        'id', 'user_id', 'session_id', 'question_id',
        'score', 'relevance_score', 'technical_correctness', 
        'completeness', 'clarity',
        'strengths', 'weaknesses', 'suggestions',
        'ideal_answer', 'evaluation', 'created_at'
    ]
    
    for field in required_fields:
        assert field in feedback, f"Missing field: {field}"
    
    # 4. Verify score ranges
    assert 0.0 <= feedback['score'] <= 100.0
    assert 0.0 <= feedback['relevance_score'] <= 100.0
    assert 0.0 <= feedback['technical_correctness'] <= 100.0
    assert 0.0 <= feedback['completeness'] <= 100.0
    assert 0.0 <= feedback['clarity'] <= 100.0
    
    # 5. Verify list fields
    assert isinstance(feedback['strengths'], list)
    assert isinstance(feedback['weaknesses'], list)
    assert isinstance(feedback['suggestions'], list)
    
    print("[OK] Evaluation response structure verified")


if __name__ == "__main__":
    print("Running complete interview flow tests...\n")
    test_complete_interview_flow()
    print("\n" + "="*50 + "\n")
    test_answer_persistence()
    print("\n" + "="*50 + "\n")
    test_evaluation_response_structure()
    print("\n" + "="*50)
    print("ALL NEW TESTS PASSED SUCCESSFULLY!")
    print("="*50)