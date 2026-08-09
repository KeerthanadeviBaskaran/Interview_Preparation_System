from fastapi.testclient import TestClient
from main import app
import uuid

client = TestClient(app)

# Use unique email to avoid conflicts with existing data
unique_id = str(uuid.uuid4())[:8]
test_email = f'interview_user_{unique_id}@example.com'

# 1. Register & Login user
client.post('/api/v1/auth/register', json={'email': test_email, 'password': 'InterviewPass123!', 'full_name': 'Interview Tester'})
token_res = client.post('/api/v1/auth/login', json={'email': test_email, 'password': 'InterviewPass123!'})
tokens = token_res.json()
headers = {'Authorization': 'Bearer ' + tokens['access_token']}

# 2. Test GET questions before generation -> 404
res_get_empty = client.get('/api/v1/interview/questions', headers=headers)
print('GET questions empty status:', res_get_empty.status_code)
assert res_get_empty.status_code == 404

# 3. Test POST generate before selecting role -> 400
res_gen_norole = client.post('/api/v1/interview/questions/generate', json={'num_questions': 5}, headers=headers)
print('POST generate without role status:', res_gen_norole.status_code)
assert res_gen_norole.status_code == 400

# 4. Select Target Role -> "Backend Engineer"
res_role = client.post('/api/v1/role/me', json={'target_role': 'Backend Engineer', 'experience_level': 'Senior Level'}, headers=headers)
assert res_role.status_code == 200

# 5. Upload PDF Resume and trigger Resume Analysis
sample_pdf_bytes = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n4 0 obj\n<< /Length 180 >>\nstream\nBT\n/F1 12 Tf\n50 700 Td\n(Senior Backend Engineer experienced in Python, FastAPI, PostgreSQL, and Docker.) Tj\nET\nendstream\nendobj\n5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000238 00000 n \n0000000468 00000 n \ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n545\n%%EOF'

client.post('/api/v1/resume/upload', files={'file': ('senior_resume.pdf', sample_pdf_bytes, 'application/pdf')}, headers=headers)
client.post('/api/v1/resume/analyze', headers=headers)

# 6. Trigger POST /api/v1/interview/questions/generate
res_gen = client.post('/api/v1/interview/questions/generate', json={'num_questions': 5}, headers=headers)
print('POST /interview/questions/generate status:', res_gen.status_code)
assert res_gen.status_code == 201

data = res_gen.json()
print('Session ID:', data['id'])
print('Target Role:', data['target_role'])
print('Total Questions:', data['total_questions'])
assert len(data['questions']) == 5

# Verify question attributes
categories_found = set()
for idx, q in enumerate(data['questions']):
    print(f"\nQuestion {idx+1} [{q['category']}] ({q['difficulty']}):")
    print(f"  Q: {q['question']}")
    print(f"  Expected Topics: {q['expected_topics']}")
    print(f"  Ideal Answer Points: {q['ideal_answer_points']}")
    print(f"  Evaluation Criteria: {q['evaluation_criteria']}")
    print(f"  Estimated Time: {q['estimated_time_minutes']} minutes")

    categories_found.add(q['category'])
    assert 'question' in q
    assert 'category' in q
    assert 'difficulty' in q
    assert 'expected_topics' in q and len(q['expected_topics']) > 0
    assert 'ideal_answer_points' in q and len(q['ideal_answer_points']) > 0
    assert 'evaluation_criteria' in q and len(q['evaluation_criteria']) > 0
    assert 'estimated_time_minutes' in q

print('\nCategories Found in Session:', categories_found)
assert len(categories_found) >= 3

# 7. Trigger GET /api/v1/interview/questions
res_fetch = client.get('/api/v1/interview/questions', headers=headers)
print('GET /interview/questions status:', res_fetch.status_code)
assert res_fetch.status_code == 200
assert res_fetch.json()['id'] == data['id']

print('\n--- AI INTERVIEW QUESTION GENERATOR MODULE VERIFIED 100% SUCCESSFULLY! ---')
