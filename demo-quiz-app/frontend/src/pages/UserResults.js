// src/pages/UserResults.js
import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getUserResults, getCurrentUser } from "../services/api";

export default function UserResults() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const userId = getCurrentUser();

  useEffect(() => {
    async function fetchResults() {
      try {
        setLoading(true);
        const userResults = await getUserResults(userId);
        // Sort results by completion date (most recent first)
        const sortedResults = userResults.sort((a, b) => 
          new Date(b.completed_at) - new Date(a.completed_at)
        );
        setResults(sortedResults);
        setError(null);
      } catch (err) {
        setError("Failed to load your results. Please try again.");
        console.error("Error fetching results:", err);
      } finally {
        setLoading(false);
      }
    }

    if (userId) {
      fetchResults();
    }
  }, [userId]);

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown date';
    
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (error) {
      return 'Invalid date';
    }
  };

  const formatTime = (seconds) => {
    if (!seconds) return '0s';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
  };

  const getScorePercentage = (score, total) => {
    if (!total || total === 0) return 0;
    return Math.round((score / total) * 100);
  };

  const getScoreColor = (percentage) => {
    if (percentage >= 80) return '#4CAF50'; // Green
    if (percentage >= 60) return '#FF9800'; // Orange
    return '#f44336'; // Red
  };

  const calculateStats = () => {
    if (results.length === 0) return { avgScore: 0, totalQuizzes: 0, bestScore: 0 };
    
    const totalScore = results.reduce((sum, result) => {
      const score = getScorePercentage(result.correct_questions || 0, result.total_questions || 1);
      return sum + score;
    }, 0);
    
    const avgScore = Math.round(totalScore / results.length);
    const bestScore = Math.max(...results.map(result => 
      getScorePercentage(result.correct_questions || 0, result.total_questions || 1)
    ));
    
    return {
      avgScore,
      totalQuizzes: results.length,
      bestScore
    };
  };

  if (loading) {
    return (
      <div className="user-results-container">
        <div className="loading-spinner">Loading your results...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="user-results-container">
        <div className="error-message">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Try Again</button>
        </div>
      </div>
    );
  }

  const stats = calculateStats();

  return (
    <div className="user-results-container">
      <div className="results-header">
        <h1>Your Quiz Results</h1>
        <p>Track your progress and see how you're improving!</p>
      </div>

      {/* Stats Overview */}
      <div className="stats-overview">
        <div className="stat-card">
          <div className="stat-number">{stats.totalQuizzes}</div>
          <div className="stat-label">Quizzes Taken</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{stats.avgScore}%</div>
          <div className="stat-label">Average Score</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{stats.bestScore}%</div>
          <div className="stat-label">Best Score</div>
        </div>
      </div>

      {/* Results List */}
      {results.length === 0 ? (
        <div className="no-results">
          <h3>No Results Yet</h3>
          <p>You haven't taken any quizzes yet. Start with your first quiz!</p>
          <div className="no-results-actions">
            <Link to="/quizzes" className="btn btn-primary">
              Browse Quizzes
            </Link>
          </div>
        </div>
      ) : (
        <div className="results-list">
          <h2>Recent Results</h2>
          <div className="results-grid">
            {results.map(result => {
              const percentage = getScorePercentage(result.correct_questions, result.total_questions);
              const scoreColor = getScoreColor(percentage);
              
              return (
                <div key={result.id} className="result-card">
                  <div className="result-header">
                    <h3 className="quiz-title">{result.title}</h3>
                    <span className="result-date">
                      {formatDate(result.completed_at)}
                    </span>
                  </div>
                  
                  <div className="result-body">
                    <div className="score-display">
                      <div 
                        className="score-circle-small" 
                        style={{ backgroundColor: scoreColor }}
                      >
                        {percentage}%
                      </div>
                      <div className="score-details">
                        <span className="score-fraction">
                          {result.correct_questions} / {result.total_questions}
                        </span>
                        <span className="score-label">
                          {percentage >= 80 ? 'Excellent' : 
                           percentage >= 60 ? 'Good' : 'Needs Work'}
                        </span>
                      </div>
                    </div>
                    
                    <div className="result-meta">
                      <span className="time-taken">
                        ⏱️ {formatTime(result.time_taken)}
                      </span>
                    </div>
                  </div>
                  
                  <div className="result-actions">
                    <Link 
                      to={`/results/${result.id}`}
                      className="btn btn-sm btn-outline"
                    >
                      View Details
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {results.length > 0 && (
        <div className="results-actions">
          <Link to="/quizzes" className="btn btn-primary">
            Take Another Quiz
          </Link>
          <Link to="/" className="btn btn-secondary">
            Back to Home
          </Link>
        </div>
      )}
    </div>
  );
}