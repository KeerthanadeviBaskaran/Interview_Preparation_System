from fastapi.testclient import TestClient
from main import app
import uuid

client = TestClient(app)

# Use unique email to avoid conflicts with existing data
unique_id = str(uuid.uuid4())[:8]
test_email = f'roadmap_user_{unique_id}@example.com'

# 1. Register & Login user
client.post('/api/v1/auth/register', json={'email': test_email, 'password': 'RoadmapPass123!', 'full_name': 'Roadmap Tester'})
token_res = client.post('/api/v1/auth/login', json={'email': test_email, 'password': 'RoadmapPass123!'})
tokens = token_res.json()
headers = {'Authorization': 'Bearer ' + tokens['access_token']}

# 2. Test GET roadmap before generation -> 404
res_get_empty = client.get('/api/v1/roadmap', headers=headers)
print('GET roadmap empty status:', res_get_empty.status_code)
assert res_get_empty.status_code == 404

# 3. Test POST generate before selecting role -> 400
res_gen_norole = client.post('/api/v1/roadmap/generate', headers=headers)
print('POST generate without role status:', res_gen_norole.status_code)
assert res_gen_norole.status_code == 400

# 4. Select Target Role -> "Backend Engineer"
res_role = client.post('/api/v1/role/me', json={'target_role': 'Backend Engineer', 'experience_level': 'Mid Level'}, headers=headers)
assert res_role.status_code == 200

# 5. Upload PDF Resume and trigger Resume Analysis
sample_pdf_bytes = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n4 0 obj\n<< /Length 180 >>\nstream\nBT\n/F1 12 Tf\n50 700 Td\n(Software Developer skilled in Python, FastAPI, SQL, and PostgreSQL.) Tj\nET\nendstream\nendobj\n5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000238 00000 n \n0000000468 00000 n \ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n545\n%%EOF'

client.post('/api/v1/resume/upload', files={'file': ('my_resume.pdf', sample_pdf_bytes, 'application/pdf')}, headers=headers)
client.post('/api/v1/resume/analyze', headers=headers)

# 6. Trigger POST /api/v1/roadmap/generate
res_roadmap = client.post('/api/v1/roadmap/generate', headers=headers)
print('POST /roadmap/generate status:', res_roadmap.status_code)
assert res_roadmap.status_code == 200

data = res_roadmap.json()
print('Target Role:', data['target_role'])
print('Total Skills to Learn:', data['total_skills_to_learn'])
print('Immediate Phase (1-2 Weeks) Count:', len(data['immediate_phase']))
print('Short-Term Phase (1 Month) Count:', len(data['short_term_phase']))
print('Medium-Term Phase (2-3 Months) Count:', len(data['medium_term_phase']))
print('Long-Term Phase (Beyond 3 Months) Count:', len(data['long_term_phase']))

# Verify item attributes
sample_item = data['immediate_phase'][0] if data['immediate_phase'] else data['long_term_phase'][0]
print('Sample Skill Item:', sample_item['skill_name'])
print('Learning Objective:', sample_item['learning_objective'])
print('Difficulty:', sample_item['difficulty'])
print('Duration:', sample_item['estimated_duration'])
print('Resources:', sample_item['resources'])
print('Practice Project:', sample_item['practice_project'])
print('Interview Tips:', sample_item['interview_tips'])

assert 'learning_objective' in sample_item
assert 'resources' in sample_item
assert len(sample_item['resources']) > 0
assert 'title' in sample_item['resources'][0]
assert 'url' in sample_item['resources'][0]

# 7. Trigger GET /api/v1/roadmap
res_fetch = client.get('/api/v1/roadmap', headers=headers)
print('GET /roadmap status:', res_fetch.status_code)
assert res_fetch.status_code == 200
assert res_fetch.json()['id'] == data['id']

print('--- PERSONALIZED LEARNING ROADMAP MODULE VERIFIED 100% SUCCESSFULLY! ---')
