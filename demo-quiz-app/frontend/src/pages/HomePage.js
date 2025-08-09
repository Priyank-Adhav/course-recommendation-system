// src/components/Home.js
import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchQuizzes, fetchCategories, getCurrentUser } from "../services/api";

export default function Home() {
  const [stats, setStats] = useState({
    totalQuizzes: 0,
    totalCategories: 0
  });
  const [recentQuizzes, setRecentQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);
  const userId = getCurrentUser();

  useEffect(() => {
    async function loadHomeData() {
      try {
        setLoading(true);
        
        const [quizzesData, categoriesData] = await Promise.all([
          fetchQuizzes(),
          fetchCategories()
        ]);
        
        setStats({
          totalQuizzes: quizzesData.length,
          totalCategories: categoriesData.length
        });
        
        // Get first 3 quizzes as "recent"
        setRecentQuizzes(quizzesData.slice(0, 3));
        
      } catch (error) {
        console.error("Error loading home data:", error);
      } finally {
        setLoading(false);
      }
    }

    loadHomeData();
  }, []);

  if (loading) {
    return (
      <div className="home-container">
        <div className="loading-spinner">Loading...</div>
      </div>
    );
  }

  return (
    <div className="home-container">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            Welcome to QuizMaster
          </h1>
          <p className="hero-subtitle">
            Test your knowledge, track your progress, and learn something new every day
          </p>
          <div className="hero-actions">
            <Link to="/quizzes" className="btn btn-primary btn-large">
              Browse Quizzes
            </Link>
            <Link to={`/my-results`} className="btn btn-secondary btn-large">
              View My Results
            </Link>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats-section">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📚</div>
            <div className="stat-number">{stats.totalQuizzes}</div>
            <div className="stat-label">Available Quizzes</div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">🏷️</div>
            <div className="stat-number">{stats.totalCategories}</div>
            <div className="stat-label">Categories</div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">👤</div>
            <div className="stat-number">User #{userId}</div>
            <div className="stat-label">Your Profile</div>
          </div>
        </div>
      </section>

      {/* Featured Quizzes */}
      {recentQuizzes.length > 0 && (
        <section className="featured-section">
          <h2>Featured Quizzes</h2>
          <div className="featured-grid">
            {recentQuizzes.map(quiz => (
              <div key={quiz.id} className="featured-card">
                <div className="featured-card-header">
                  <h3>{quiz.title}</h3>
                  <span className="category-badge">
                    {quiz.category_name}
                  </span>
                </div>
                <div className="featured-card-body">
                  <p>Challenge yourself with this {quiz.category_name.toLowerCase()} quiz</p>
                </div>
                <div className="featured-card-footer">
                  <Link to={`/quiz/${quiz.id}`} className="btn btn-primary">
                    Start Quiz
                  </Link>
                </div>
              </div>
            ))}
          </div>
          <div className="featured-actions">
            <Link to="/quizzes" className="btn btn-outline">
              View All Quizzes →
            </Link>
          </div>
        </section>
      )}

      {/* How It Works */}
      <section className="how-it-works">
        <h2>How It Works</h2>
        <div className="steps-grid">
          <div className="step-card">
            <div className="step-number">1</div>
            <h3>Choose a Quiz</h3>
            <p>Browse our collection of quizzes across different categories</p>
          </div>
          <div className="step-card">
            <div className="step-number">2</div>
            <h3>Answer Questions</h3>
            <p>Take your time and answer multiple-choice questions at your own pace</p>
          </div>
          <div className="step-card">
            <div className="step-number">3</div>
            <h3>See Results</h3>
            <p>Get instant feedback with detailed results and explanations</p>
          </div>
        </div>
      </section>
    </div>
  );
}