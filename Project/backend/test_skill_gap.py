from fastapi.testclient import TestClient
from main import app
import uuid

client = TestClient(app)

# Use unique email to avoid conflicts with existing data
unique_id = str(uuid.uuid4())[:8]
test_email = f'gap_user_{unique_id}@example.com'

# 1. Register & Login user
client.post('/api/v1/auth/register', json={'email': test_email, 'password': 'GapPassword123!', 'full_name': 'Gap Tester'})
token_res = client.post('/api/v1/auth/login', json={'email': test_email, 'password': 'GapPassword123!'})
tokens = token_res.json()
headers = {'Authorization': 'Bearer ' + tokens['access_token']}

# 2. Test GET result before analyze -> 404
res_get_empty = client.get('/api/v1/skill-gap/result', headers=headers)
print('GET result empty status:', res_get_empty.status_code)
assert res_get_empty.status_code == 404

# 3. Test POST analyze before selecting role -> 400
res_post_norole = client.post('/api/v1/skill-gap/analyze', headers=headers)
print('POST analyze without role status:', res_post_norole.status_code)
assert res_post_norole.status_code == 400

# 4. Select Target Role -> "Backend Engineer"
res_role = client.post('/api/v1/role/me', json={'target_role': 'Backend Engineer', 'experience_level': 'Mid Level'}, headers=headers)
assert res_role.status_code == 200
print('Selected Role:', res_role.json()['target_role'])

# 5. Test POST analyze before resume analysis -> 400
res_post_noanalysis = client.post('/api/v1/skill-gap/analyze', headers=headers)
print('POST analyze without resume analysis status:', res_post_noanalysis.status_code)
assert res_post_noanalysis.status_code == 400

# 6. Upload PDF Resume and trigger Resume Analysis
sample_pdf_bytes = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n4 0 obj\n<< /Length 200 >>\nstream\nBT\n/F1 12 Tf\n50 700 Td\n(Backend Engineer skilled in Python, FastAPI, SQL, PostgreSQL, REST API, Redis, and Docker.) Tj\nET\nendstream\nendobj\n5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000238 00000 n \n0000000488 00000 n \ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n565\n%%EOF'

client.post('/api/v1/resume/upload', files={'file': ('backend_resume.pdf', sample_pdf_bytes, 'application/pdf')}, headers=headers)
client.post('/api/v1/resume/analyze', headers=headers)

# 7. Trigger POST /api/v1/skill-gap/analyze
res_gap = client.post('/api/v1/skill-gap/analyze', headers=headers)
print('POST /skill-gap/analyze status:', res_gap.status_code)
assert res_gap.status_code == 200

data = res_gap.json()
print('Target Role:', data['target_role'])
print('Match Percentage:', data['match_percentage'], '%')
print('Strong Skills:', data['strong_skills'])
print('Missing Skills:', data['missing_skills'])
print('Recommended Skills:', data['recommended_skills'])
print('Overall Assessment:', data['overall_assessment'])

assert data['target_role'] == 'Backend Engineer'
assert data['match_percentage'] > 0.0

# 8. Trigger GET /api/v1/skill-gap/result
res_fetch = client.get('/api/v1/skill-gap/result', headers=headers)
print('GET /skill-gap/result status:', res_fetch.status_code)
assert res_fetch.status_code == 200
assert res_fetch.json()['id'] == data['id']

print('--- SKILL GAP ANALYSIS MODULE VERIFIED 100% SUCCESSFULLY! ---')
