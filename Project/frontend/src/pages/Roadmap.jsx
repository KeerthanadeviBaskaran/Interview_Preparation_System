import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

function Roadmap() {
  const [roadmap, setRoadmap] = useState(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadRoadmap();
  }, []);

  const loadRoadmap = async () => {
    setLoading(true);
    try {
      const result = await api.get('/roadmap');
      setRoadmap(result);
    } catch (err) {
      console.error('Error loading roadmap:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    setMessage('');

    try {
      const result = await api.post('/roadmap/generate');
      setRoadmap(result);
      setMessage('Roadmap generated successfully');
    } catch (err) {
      setMessage('Error generating roadmap: ' + err.message);
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading roadmap...</div>;
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
          <a href="/roadmap" className="active">Roadmap</a>
          <a href="/interview">Mock Interview</a>
          <a href="#" onClick={() => { localStorage.removeItem('access_token'); navigate('/login'); }} className="logout">Logout</a>
        </nav>
      </aside>
      <main className="main-content">
        <h1>Learning Roadmap</h1>
        
        <div className="card">
          <h2>Generate Your Roadmap</h2>
          <p style={{ marginBottom: '1rem', color: 'var(--gray-600)' }}>
            Create a personalized learning plan based on your skill gaps and target role.
          </p>
          <button
            className="btn btn-primary"
            onClick={handleGenerate}
            disabled={generating}
          >
            {generating ? '🗺️ Generating...' : '🗺️ Generate Roadmap'}
          </button>
          {message && <div className={message.includes('Error') ? 'error' : 'success'} style={{ marginTop: '1rem' }}>{message}</div>}
        </div>

        {roadmap && (
          <>
            <div className="card">
              <h2>Roadmap Summary</h2>
              <div className="stat">
                <span className="stat-label">Target Role</span>
                <span className="stat-value">{roadmap.target_role}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Total Skills to Learn</span>
                <span className="stat-value">{roadmap.total_skills_to_learn}</span>
              </div>
            </div>

            <div className="phase">
              <h3>🚀 Immediate Phase (1-2 Weeks)</h3>
              {roadmap.immediate_phase?.map((skill, index) => (
                <div key={index} className="skill-item">
                  <h4>{skill.skill_name}</h4>
                  <p>{skill.learning_objective}</p>
                  <div style={{ marginTop: '0.5rem' }}>
                    <span className="badge badge-secondary">{skill.difficulty}</span>
                    <span className="badge badge-primary" style={{ marginLeft: '0.5rem' }}>{skill.estimated_duration}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="phase">
              <h3>📈 Short-Term Phase (1 Month)</h3>
              {roadmap.short_term_phase?.map((skill, index) => (
                <div key={index} className="skill-item">
                  <h4>{skill.skill_name}</h4>
                  <p>{skill.learning_objective}</p>
                  <div style={{ marginTop: '0.5rem' }}>
                    <span className="badge badge-secondary">{skill.difficulty}</span>
                    <span className="badge badge-primary" style={{ marginLeft: '0.5rem' }}>{skill.estimated_duration}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="phase">
              <h3>🎯 Medium-Term Phase (2-3 Months)</h3>
              {roadmap.medium_term_phase?.map((skill, index) => (
                <div key={index} className="skill-item">
                  <h4>{skill.skill_name}</h4>
                  <p>{skill.learning_objective}</p>
                  <div style={{ marginTop: '0.5rem' }}>
                    <span className="badge badge-secondary">{skill.difficulty}</span>
                    <span className="badge badge-primary" style={{ marginLeft: '0.5rem' }}>{skill.estimated_duration}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="phase">
              <h3>🏆 Long-Term Phase (Beyond 3 Months)</h3>
              {roadmap.long_term_phase?.map((skill, index) => (
                <div key={index} className="skill-item">
                  <h4>{skill.skill_name}</h4>
                  <p>{skill.learning_objective}</p>
                  <div style={{ marginTop: '0.5rem' }}>
                    <span className="badge badge-secondary">{skill.difficulty}</span>
                    <span className="badge badge-primary" style={{ marginLeft: '0.5rem' }}>{skill.estimated_duration}</span>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default Roadmap;