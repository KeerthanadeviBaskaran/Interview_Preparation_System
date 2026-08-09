import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

function SkillGap() {
  const [skillGap, setSkillGap] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadSkillGap();
  }, []);

  const loadSkillGap = async () => {
    setLoading(true);
    try {
      const result = await api.get('/skill-gap/result');
      setSkillGap(result);
    } catch (err) {
      console.error('Error loading skill gap:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setMessage('');

    try {
      const result = await api.post('/skill-gap/analyze');
      setSkillGap(result);
      setMessage('Skill gap analyzed successfully');
    } catch (err) {
      setMessage('Error analyzing skill gap: ' + err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading skill gap...</div>;
  }

  return (
    <div className="dashboard-container">
      <aside className="sidebar">
        <h2>🎯 Interview Prep</h2>
        <nav>
          <a href="/">Dashboard</a>
          <a href="/profile">Profile</a>
          <a href="/resume">Resume</a>
          <a href="/skill-gap" className="active">Skill Gap</a>
          <a href="/roadmap">Roadmap</a>
          <a href="/interview">Mock Interview</a>
          <a href="#" onClick={() => { localStorage.removeItem('access_token'); navigate('/login'); }} className="logout">Logout</a>
        </nav>
      </aside>
      <main className="main-content">
        <h1>Skill Gap Analysis</h1>
        
        <div className="card">
          <h2>Analyze Your Skills</h2>
          <p style={{ marginBottom: '1rem', color: 'var(--gray-600)' }}>
            Compare your skills against your target role requirements to identify gaps.
          </p>
          <button
            className="btn btn-primary"
            onClick={handleAnalyze}
            disabled={analyzing}
          >
            {analyzing ? '🔍 Analyzing...' : '🔍 Analyze Skill Gap'}
          </button>
          {message && <div className={message.includes('Error') ? 'error' : 'success'} style={{ marginTop: '1rem' }}>{message}</div>}
        </div>

        {skillGap && (
          <>
            <div className="score-card">
              <h2>Skill Match</h2>
              <div className="score-value">{skillGap.match_percentage.toFixed(1)}%</div>
              <div className="score-label">Match with {skillGap.target_role}</div>
            </div>

            <div className="card">
              <h2>Overall Assessment</h2>
              <p style={{ color: 'var(--gray-700)', lineHeight: '1.6' }}>{skillGap.overall_assessment}</p>
            </div>

            <div className="card">
              <h2>Strong Skills ✅</h2>
              <ul className="skill-list">
                {skillGap.strong_skills?.map((skill, index) => (
                  <li key={index}>
                    <span className="skill-badge skill-strong">{skill}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="card">
              <h2>Missing Skills ⚠️</h2>
              <ul className="skill-list">
                {skillGap.missing_skills?.map((skill, index) => (
                  <li key={index}>
                    <span className="skill-badge skill-missing">{skill}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="card">
              <h2>Recommended Skills 📚</h2>
              <ul className="skill-list">
                {skillGap.recommended_skills?.map((skill, index) => (
                  <li key={index}>
                    <span className="skill-badge skill-recommended">{skill}</span>
                  </li>
                ))}
              </ul>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default SkillGap;