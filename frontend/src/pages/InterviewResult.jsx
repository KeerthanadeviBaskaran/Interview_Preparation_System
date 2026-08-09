import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import api from '../api';

function InterviewResult() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (location.state?.result) {
      setResult(location.state.result);
      setLoading(false);
    } else {
      setLoading(false);
    }
  }, [location]);

  const getScoreClass = (score) => {
    if (score >= 70) return 'score-high';
    if (score >= 40) return 'score-medium';
    return 'score-low';
  };

  if (loading) {
    return <div className="loading">Loading results...</div>;
  }

  if (!result) {
    return (
      <div className="dashboard-container">
        <aside className="sidebar">
          <h2>🎯 Interview Prep</h2>
          <nav>
            <a href="/">Dashboard</a>
            <a href="/profile">Profile</a>
            <a href="/resume">Resume</a>
            <a href="/skill-gap">Skill Gap</a>
            <a href="/roadmap">Roadmap</a>
            <a href="/interview">Mock Interview</a>
            <a href="#" onClick={() => { localStorage.removeItem('access_token'); navigate('/login'); }} className="logout">Logout</a>
          </nav>
        </aside>
        <main className="main-content">
          <h1>Interview Results</h1>
          <div className="empty-state">
            <h3>No results available</h3>
            <p>Complete a mock interview to see your results and feedback.</p>
            <button className="btn btn-primary" onClick={() => navigate('/interview')}>
              🚀 Start Interview
            </button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <aside className="sidebar">
        <h2>🎯 Interview Prep</h2>
        <nav>
          <a href="/">Dashboard</a>
          <a href="/profile">Profile</a>
          <a href="/resume">Resume</a>
          <a href="/skill-gap">Skill Gap</a>
          <a href="/roadmap">Roadmap</a>
          <a href="/interview">Mock Interview</a>
          <a href="#" onClick={() => { localStorage.removeItem('access_token'); navigate('/login'); }} className="logout">Logout</a>
        </nav>
      </aside>
      <main className="main-content">
        <h1>Interview Results</h1>
        
        <div className="score-card">
          <h2>Overall Score</h2>
          <div className="score-value">{result.overall_score.toFixed(1)}</div>
          <div className="score-label">out of 100</div>
          <div style={{ marginTop: '1rem' }}>
            <span className={`score-badge ${getScoreClass(result.overall_score)}`}>
              {result.overall_score >= 70 ? 'Excellent' : result.overall_score >= 40 ? 'Good' : 'Needs Improvement'}
            </span>
          </div>
        </div>

        <div className="card">
          <h2>Interview Summary</h2>
          <div className="stat">
            <span className="stat-label">Questions Answered</span>
            <span className="stat-value">{result.answered_questions}/{result.total_questions}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Duration</span>
            <span className="stat-value">{Math.floor(result.duration_seconds / 60)} min {result.duration_seconds % 60} sec</span>
          </div>
        </div>

        <div className="card">
          <h2>✅ Overall Strengths</h2>
          <ul>
            {result.overall_strengths?.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </div>

        <div className="card">
          <h2>⚠️ Overall Weaknesses</h2>
          <ul>
            {result.overall_weaknesses?.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </div>

        <div className="card">
          <h2>💡 Recommendations</h2>
          <ul>
            {result.recommendations?.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </div>

        <div className="card">
          <h2>📝 Question-by-Question Feedback</h2>
          {result.feedback_summary?.map((feedback, index) => (
            <div key={index} style={{ marginBottom: '1.5rem', paddingBottom: '1.5rem', borderBottom: '1px solid var(--gray-200)' }}>
              <h4 style={{ marginBottom: '0.75rem' }}>Question {index + 1}</h4>
              <div className="stat">
                <span className="stat-label">Score</span>
                <span className="stat-value" style={{ fontSize: '1.25rem', fontWeight: '600' }}>{feedback.score}/100</span>
              </div>
              <p style={{ marginTop: '0.5rem', color: 'var(--gray-700)' }}><strong>Evaluation:</strong> {feedback.evaluation}</p>
              <p style={{ marginTop: '0.25rem', color: 'var(--gray-700)' }}><strong>Strengths:</strong> {feedback.strengths?.join(', ')}</p>
              <p style={{ marginTop: '0.25rem', color: 'var(--gray-700)' }}><strong>Weaknesses:</strong> {feedback.weaknesses?.join(', ')}</p>
            </div>
          ))}
        </div>

        <button className="btn btn-primary btn-lg" onClick={() => navigate('/')}>
          🏠 Back to Dashboard
        </button>
      </main>
    </div>
  );
}

export default InterviewResult;