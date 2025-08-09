// src/components/QuizList.js
import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchQuizzes, fetchCategories } from "../services/api";

export default function QuizList() {
  const [quizzes, setQuizzes] = useState([]);
  const [categories, setCategories] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        
        // Fetch quizzes and categories in parallel
        const [quizzesData, categoriesData] = await Promise.all([
          fetchQuizzes(),
          fetchCategories()
        ]);
        
        setQuizzes(quizzesData);
        
        // Convert categories array to object for easy lookup
        const categoryMap = {};
        categoriesData.forEach(cat => {
          categoryMap[cat.id] = cat;
        });
        setCategories(categoryMap);
        
        setError(null);
      } catch (err) {
        setError("Failed to load quizzes. Please try again.");
        console.error("Error loading data:", err);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const filteredQuizzes = selectedCategory === 'all' 
    ? quizzes 
    : quizzes.filter(quiz => quiz.category_id === parseInt(selectedCategory));

  const uniqueCategories = [...new Set(quizzes.map(quiz => quiz.category_id))]
    .map(categoryId => categories[categoryId])
    .filter(Boolean);

  if (loading) {
    return (
      <div className="quiz-list-container">
        <div className="loading-spinner">Loading quizzes...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="quiz-list-container">
        <div className="error-message">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Try Again</button>
        </div>
      </div>
    );
  }

  return (
    <div className="quiz-list-container">
      <div className="quiz-list-header">
        <h1>Available Quizzes</h1>
        <p>Choose a quiz to test your knowledge!</p>
      </div>

      {/* Category Filter */}
      <div className="category-filter">
        <label htmlFor="category-select">Filter by Category:</label>
        <select 
          id="category-select"
          value={selectedCategory} 
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="category-select"
        >
          <option value="all">All Categories</option>
          {uniqueCategories.map(category => (
            <option key={category.id} value={category.id}>
              {category.category_name}
            </option>
          ))}
        </select>
      </div>

      {/* Quiz Grid */}
      <div className="quiz-grid">
        {filteredQuizzes.length === 0 ? (
          <div className="no-quizzes">
            <h3>No quizzes found</h3>
            <p>
              {selectedCategory === 'all' 
                ? "There are no quizzes available yet." 
                : "No quizzes found for the selected category."}
            </p>
          </div>
        ) : (
          filteredQuizzes.map(quiz => (
            <div key={quiz.id} className="quiz-card">
              <div className="quiz-card-header">
                <h3 className="quiz-title">{quiz.title}</h3>
                {categories[quiz.category_id] && (
                  <span className="quiz-category">
                    {categories[quiz.category_id].category_name}
                  </span>
                )}
              </div>
              
              <div className="quiz-card-body">
                <p className="quiz-description">
                  Test your knowledge in {categories[quiz.category_id]?.category_name || 'this subject'}
                </p>
              </div>
              
              <div className="quiz-card-footer">
                <Link 
                  to={`/quiz/${quiz.id}`} 
                  className="btn btn-primary quiz-start-btn"
                >
                  Start Quiz
                </Link>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Stats */}
      <div className="quiz-stats">
        <div className="stat-item">
          <span className="stat-number">{quizzes.length}</span>
          <span className="stat-label">Total Quizzes</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{Object.keys(categories).length}</span>
          <span className="stat-label">Categories</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{filteredQuizzes.length}</span>
          <span className="stat-label">Showing</span>
        </div>
      </div>
    </div>
  );
}