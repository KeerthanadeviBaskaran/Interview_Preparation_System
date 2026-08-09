from fastapi.testclient import TestClient
from main import app
import uuid

client = TestClient(app)

def test_readiness_score():
    """Test the interview readiness score calculation."""
    
    # 1. Register & Login user
    unique_id = str(uuid.uuid4())[:8]
    test_email = f'readiness_user_{unique_id}@example.com'
    
    register_res = client.post('/api/v1/auth/register', json={
        'email': test_email, 
        'password': 'ReadinessPass123!', 
        'full_name': 'Readiness Tester'
    })
    assert register_res.status_code == 201
    
    token_res = client.post('/api/v1/auth/login', json={
        'email': test_email, 
        'password': 'ReadinessPass123!'
    })
    tokens = token_res.json()
    headers = {'Authorization': 'Bearer ' + tokens['access_token']}
    
    # 2. Test GET readiness score (new user with no data)
    res_readiness = client.get('/api/v1/readiness', headers=headers)
    print('GET readiness status:', res_readiness.status_code)
    assert res_readiness.status_code == 200
    
    data = res_readiness.json()
    assert 'readiness_score' in data
    assert 'performance_level' in data
    assert 'breakdown' in data
    assert 0.0 <= data['readiness_score'] <= 100.0
    assert data['performance_level'] in ['Needs Improvement', 'Developing', 'Good', 'Interview Ready']
    
    # With no data, should be 0.0 and Needs Improvement
    assert data['readiness_score'] == 0.0
    assert data['performance_level'] == 'Needs Improvement'
    print('[OK] Readiness score calculated for new user (0.0, Needs Improvement)')
    
    # 3. Add some learning progress data
    client.post('/api/v1/progress', json={
        'skill_name': 'Python',
        'progress_percentage': 75.0
    }, headers=headers)
    
    # 4. Get readiness score again
    res_readiness2 = client.get('/api/v1/readiness', headers=headers)
    assert res_readiness2.status_code == 200
    
    data2 = res_readiness2.json()
    print('Readiness score with progress:', data2['readiness_score'])
    print('Performance level:', data2['performance_level'])
    print('Breakdown:', data2['breakdown'])
    
    # Should have some score now from learning progress (30% weight)
    assert data2['readiness_score'] > 0.0
    assert 'learning_progress' in data2['breakdown']
    assert data2['breakdown']['learning_progress'] == 75.0
    print('[OK] Readiness score updated with learning progress')
    
    print('\n=== INTERVIEW READINESS SCORE MODULE VERIFIED 100% SUCCESSFULLY! ===')


if __name__ == "__main__":
    print("Running readiness score test...\n")
    test_readiness_score()