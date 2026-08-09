import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

function Profile() {
  const [user, setUser] = useState(null);
  const [role, setRole] = useState(null);
  const [targetRole, setTargetRole] = useState('');
  const [experienceLevel, setExperienceLevel] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadProfileData();
  }, []);

  const loadProfileData = async () => {
    try {
      const [userData, roleData] = await Promise.all([
        api.get('/auth/me'),
        api.get('/role/me').catch(() => null),
      ]);
      setUser(userData);
      setRole(roleData);
      if (roleData) {
        setTargetRole(roleData.target_role);
        setExperienceLevel(roleData.experience_level);
      }
    } catch (err) {
      console.error('Error loading profile:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveRole = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');

    try {
      await api.post('/role/me', {
        target_role: targetRole,
        experience_level: experienceLevel,
      });
      setMessage('Role updated successfully');
      loadProfileData();
    } catch (err) {
      setMessage('Error updating role: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading profile...</div>;
  }

  return (
    <div className="dashboard-container">
      <aside className="sidebar">
        <h2>🎯 Interview Prep</h2>
        <nav>
          <a href="/">Dashboard</a>
          <a href="/profile" className="active">Profile</a>
          <a href="/resume">Resume</a>
          <a href="/skill-gap">Skill Gap</a>
          <a href="/roadmap">Roadmap</a>
          <a href="/interview">Mock Interview</a>
          <a href="#" onClick={() => { localStorage.removeItem('access_token'); navigate('/login'); }} className="logout">Logout</a>
        </nav>
      </aside>
      <main className="main-content">
        <h1>Profile Settings</h1>
        
        <div className="card">
          <h2>Basic Information</h2>
          <div className="stat">
            <span className="stat-label">Name</span>
            <span className="stat-value">{user?.full_name}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Email</span>
            <span className="stat-value">{user?.email}</span>
          </div>
        </div>

        <div className="card">
          <h2>Target Role</h2>
          <form onSubmit={handleSaveRole}>
            <div className="form-group">
              <label>Target Role</label>
              <select
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                required
              >
                <option value="">Select a role</option>
                <option value="Software Engineer">Software Engineer</option>
                <option value="Backend Engineer">Backend Engineer</option>
                <option value="Frontend Engineer">Frontend Engineer</option>
                <option value="Full Stack Developer">Full Stack Developer</option>
                <option value="Data Scientist">Data Scientist</option>
                <option value="DevOps Engineer">DevOps Engineer</option>
                <option value="Machine Learning Engineer">Machine Learning Engineer</option>
                <option value="Product Manager">Product Manager</option>
              </select>
            </div>
            <div className="form-group">
              <label>Experience Level</label>
              <select
                value={experienceLevel}
                onChange={(e) => setExperienceLevel(e.target.value)}
                required
              >
                <option value="">Select experience level</option>
                <option value="Entry Level">Entry Level</option>
                <option value="Junior Level">Junior Level</option>
                <option value="Mid Level">Mid Level</option>
                <option value="Senior Level">Senior Level</option>
                <option value="Lead Level">Lead Level</option>
              </select>
            </div>
            {message && <div className={message.includes('Error') ? 'error' : 'success'}>{message}</div>}
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving...' : '💾 Save Role'}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}

export default Profile;