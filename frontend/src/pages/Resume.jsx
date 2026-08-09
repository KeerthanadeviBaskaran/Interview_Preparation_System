import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

function Resume() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setMessage('Please select a file');
      return;
    }

    setUploading(true);
    setMessage('');

    try {
      await api.upload('/resume/upload', file);
      setMessage('Resume uploaded successfully');
      setFile(null);
    } catch (err) {
      setMessage('Error uploading resume: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setMessage('');

    try {
      const result = await api.post('/resume/analyze');
      setAnalysis(result);
      setMessage('Resume analyzed successfully');
    } catch (err) {
      setMessage('Error analyzing resume: ' + err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="dashboard-container">
      <aside className="sidebar">
        <h2>🎯 Interview Prep</h2>
        <nav>
          <a href="/">Dashboard</a>
          <a href="/profile">Profile</a>
          <a href="/resume" className="active">Resume</a>
          <a href="/skill-gap">Skill Gap</a>
          <a href="/roadmap">Roadmap</a>
          <a href="/interview">Mock Interview</a>
          <a href="#" onClick={() => { localStorage.removeItem('access_token'); navigate('/login'); }} className="logout">Logout</a>
        </nav>
      </aside>
      <main className="main-content">
        <h1>Resume Management</h1>
        
        <div className="card">
          <h2>Upload Resume</h2>
          <div className="file-upload" onClick={() => document.getElementById('fileInput').click()}>
            <input
              id="fileInput"
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
            />
            <p style={{ fontSize: '1.125rem', fontWeight: '500', marginBottom: '0.5rem' }}>
              {file ? '📄 ' + file.name : '📁 Click to upload PDF'}
            </p>
            <p style={{ fontSize: '0.875rem', color: 'var(--gray-500)' }}>
              Maximum file size: 5MB
            </p>
          </div>
          <button
            className="btn btn-primary"
            onClick={handleUpload}
            disabled={uploading || !file}
            style={{ marginTop: '1rem' }}
          >
            {uploading ? '⏳ Uploading...' : '📤 Upload Resume'}
          </button>
          {message && <div className={message.includes('Error') ? 'error' : 'success'} style={{ marginTop: '1rem' }}>{message}</div>}
        </div>

        <div className="card">
          <h2>Analyze Resume</h2>
          <p style={{ marginBottom: '1rem', color: 'var(--gray-600)' }}>
            Extract skills, experience, and qualifications from your resume to personalize your interview preparation.
          </p>
          <button
            className="btn btn-secondary"
            onClick={handleAnalyze}
            disabled={analyzing}
          >
            {analyzing ? '🔍 Analyzing...' : '🔍 Analyze Resume'}
          </button>
        </div>

        {analysis && (
          <div className="card">
            <h2>Resume Analysis Results</h2>
            <div className="stat">
              <span className="stat-label">Technical Skills</span>
              <span className="stat-value">{analysis.technical_skills?.join(', ') || 'None'}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Programming Languages</span>
              <span className="stat-value">{analysis.programming_languages?.join(', ') || 'None'}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Frameworks</span>
              <span className="stat-value">{analysis.frameworks?.join(', ') || 'None'}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Databases</span>
              <span className="stat-value">{analysis.databases?.join(', ') || 'None'}</span>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default Resume;