import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

function Interview() {
  const [session, setSession] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answer, setAnswer] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadSession();
  }, []);

  const loadSession = async () => {
    try {
      const result = await api.get('/interview/questions');
      setSession(result);
    } catch (err) {
      console.error('No existing session:', err);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    setMessage('');

    try {
      const result = await api.post('/interview/questions/generate', { num_questions: 5 });
      setSession(result);
      setCurrentQuestionIndex(0);
      setAnswer('');
      setFeedback(null);
      setCompleted(false);
    } catch (err) {
      setMessage('Error generating questions: ' + err.message);
    } finally {
      setGenerating(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!answer.trim()) {
      setMessage('Please enter an answer');
      return;
    }

    setSubmitting(true);
    setMessage('');

    try {
      const currentQuestion = session.questions[currentQuestionIndex];
      const result = await api.post(`/interview/questions/${currentQuestion.id}/answer`, {
        user_answer: answer,
      });
      setFeedback(result.feedback);
    } catch (err) {
      setMessage('Error submitting answer: ' + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < session.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setAnswer('');
      setFeedback(null);
    } else {
      handleCompleteInterview();
    }
  };

  const handleCompleteInterview = async () => {
    try {
      const result = await api.post(`/interview/${session.id}/complete`);
      setCompleted(true);
      navigate('/interview-result', { state: { result } });
    } catch (err) {
      setMessage('Error completing interview: ' + err.message);
    }
  };

  if (!session) {
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
            <a href="/interview" className="active">Mock Interview</a>
            <a href="#" onClick={() => { localStorage.removeItem('access_token'); navigate('/login'); }} className="logout">Logout</a>
          </nav>
        </aside>
        <main className="main-content">
          <h1>Mock Interview</h1>
          <div className="card">
            <h2>Start New Interview</h2>
            <p style={{ marginBottom: '1rem', color: 'var(--gray-600)' }}>
              Generate personalized interview questions based on your target role and experience level.
            </p>
            <button
              className="btn btn-primary btn-lg"
              onClick={handleGenerate}
              disabled={generating}
              style={{ marginTop: '1rem' }}
            >
              {generating ? '⏳ Generating...' : '🚀 Start Interview'}
            </button>
            {message && <div className={message.includes('Error') ? 'error' : 'success'} style={{ marginTop: '1rem' }}>{message}</div>}
          </div>
        </main>
      </div>
    );
  }

  const currentQuestion = session.questions[currentQuestionIndex];

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
          <a href="/interview" className="active">Mock Interview</a>
          <a href="#" onClick={() => { localStorage.removeItem('access_token'); navigate('/login'); }} className="logout">Logout</a>
        </nav>
      </aside>
      <main className="main-content">
        <h1>Mock Interview</h1>
        <p style={{ marginBottom: '1.5rem', color: 'var(--gray-600)', fontSize: '1.125rem' }}>
          Question {currentQuestionIndex + 1} of {session.questions.length}
        </p>
        
        <div className="question-card">
          <div style={{ marginBottom: '1rem' }}>
            <span className="category">{currentQuestion.category}</span>
            <span className="difficulty">{currentQuestion.difficulty}</span>
          </div>
          <h3>{currentQuestion.question}</h3>
          <div className="form-group">
            <label>Your Answer</label>
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Type your answer here..."
              disabled={feedback !== null}
            />
          </div>
          {!feedback && (
            <button
              className="btn btn-primary btn-lg"
              onClick={handleSubmitAnswer}
              disabled={submitting}
            >
              {submitting ? '⏳ Submitting...' : '✓ Submit Answer'}
            </button>
          )}
          {message && <div className={message.includes('Error') ? 'error' : 'success'} style={{ marginTop: '1rem' }}>{message}</div>}
        </div>

        {feedback && (
          <div className="feedback-card">
            <h4>📊 Your Feedback</h4>
            <div className="stat">
              <span className="stat-label">Score</span>
              <span className="stat-value" style={{ fontSize: '1.5rem', fontWeight: '700' }}>{feedback.score}/100</span>
            </div>
            <div className="stat">
              <span className="stat-label">Evaluation</span>
              <span className="stat-value">{feedback.evaluation}</span>
            </div>
            <h4 style={{ marginTop: '1.5rem' }}>✅ Strengths</h4>
            <ul>
              {feedback.strengths?.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
            <h4 style={{ marginTop: '1rem' }}>⚠️ Weaknesses</h4>
            <ul>
              {feedback.weaknesses?.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
            <h4 style={{ marginTop: '1rem' }}>💡 Suggestions</h4>
            <ul>
              {feedback.suggestions?.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
            <button
              className="btn btn-secondary btn-lg"
              onClick={handleNextQuestion}
              style={{ marginTop: '1.5rem' }}
            >
              {currentQuestionIndex < session.questions.length - 1 ? '➡️ Next Question' : '✅ Complete Interview'}
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

export default Interview;