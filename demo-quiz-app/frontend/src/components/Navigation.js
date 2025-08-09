// src/components/Navigation.js
import React from "react";
import { Link } from "react-router-dom";

export default function Navigation() {
  return (
    <nav className="main-nav">
      <div className="nav-container">
        <Link to="/" className="nav-brand">
          <h2>🎓 QuizMaster</h2>
        </Link>
        <div className="nav-links">
          <Link to="/" className="nav-link">Home</Link>
          <Link to="/quizzes" className="nav-link">Quizzes</Link>
          <Link to="/my-results" className="nav-link">My Results</Link>
        </div>
      </div>
    </nav>
  );
}