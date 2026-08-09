import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

function Dashboard() {
  const [user, setUser] = useState(null);
  const [readiness, setReadiness] = useState(null);
  const [role, setRole] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [userData, readinessData, roleData] = await Promise.all([
        api.get('/auth/me'),
        api.get('/readiness').catch(() => ({ readiness_score: 0, performance_level: 'Needs Improvement' })),
        api.get('/role/me').catch(() => null),
      ]);
      setUser(userData);
      setReadiness(readinessData);
      setRole(roleData);
    } catch (err) {
      console.error('Error loading dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    navigate('/login');
  };

  const getScoreClass = (score) => {
    if (score >= 70) return 'score-high';
    if (score >= 40) return 'score-medium';
    return 'score-low';
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard-container">
      <aside className="sidebar">
        <h2>🎯 Interview Prep</h2>
        <nav>
          <a href="/" className="active">Dashboard</a>
          <a href="/profile">Profile</a>
          <a href="/resume">Resume</a>
          <a href="/skill-gap">Skill Gap</a>
          <a href="/roadmap">Roadmap</a>
          <a href="/interview">Mock Interview</a>
          <a href="#" onClick={handleLogout} className="logout">Logout</a>
        </nav>
      </aside>
      <main className="main-content">
        <h1>Welcome back, {user?.full_name || 'User'} 👋</h1>
        
        <div className="score-card">
          <h2>Interview Readiness Score</h2>
          <div className="score-value">{readiness?.readiness_score || 0}</div>
          <div className="score-label">out of 100</div>
          <div style={{ marginTop: '1rem' }}>
            <span className={`score-badge ${getScoreClass(readiness?.readiness_score || 0)}`}>
              {readiness?.performance_level || 'Needs Improvement'}
            </span>
          </div>
        </div>

        <div className="card">
          <h2>Target Role</h2>
          <div className="stat">
            <span className="stat-label">Role</span>
            <span className="stat-value">{role?.target_role || 'Not selected'}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Experience Level</span>
            <span className="stat-value">{role?.experience_level || 'Not selected'}</span>
          </div>
        </div>

        <div className="card">
          <h2>Score Breakdown</h2>
          {readiness?.breakdown ? (
            <>
              <div style={{ marginBottom: '1rem' }}>
                <div className="stat">
                  <span className="stat-label">Interview Performance (40%)</span>
                  <span className="stat-value">{readiness.breakdown.interview_performance.toFixed(1)}%</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${readiness.breakdown.interview_performance}%` }}></div>
                </div>
              </div>
              <div style={{ marginBottom: '1rem' }}>
                <div className="stat">
                  <span className="stat-label">Learning Progress (30%)</span>
                  <span className="stat-value">{readiness.breakdown.learning_progress.toFixed(1)}%</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${readiness.breakdown.learning_progress}%` }}></div>
                </div>
              </div>
              <div style={{ marginBottom: '1rem' }}>
                <div className="stat">
                  <span className="stat-label">Skill Gap (20%)</span>
                  <span className="stat-value">{readiness.breakdown.skill_gap.toFixed(1)}%</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${readiness.breakdown.skill_gap}%` }}></div>
                </div>
              </div>
              <div>
                <div className="stat">
                  <span className="stat-label">Roadmap Completion (10%)</span>
                  <span className="stat-value">{readiness.breakdown.roadmap_completion.toFixed(1)}%</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${readiness.breakdown.roadmap_completion}%` }}></div>
                </div>
              </div>
            </>
          ) : (
            <div className="empty-state">
              <h3>No data available</h3>
              <p>Complete your profile and upload your resume to see your readiness score breakdown.</p>
            </div>
          )}
        </div>

        <button className="btn btn-primary btn-lg" onClick={() => navigate('/interview')}>
          🚀 Start Mock Interview
        </button>
      </main>
    </div>
  );
}

export default Dashboard;