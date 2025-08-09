// src/components/Footer.js
import React from "react";
import { Link } from "react-router-dom";

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="main-footer">
      <div className="footer-container">
        <div className="footer-content">
          <div className="footer-section">
            <h3 className="footer-brand">🎓 QuizMaster</h3>
            <p className="footer-description">
              Challenge yourself with interactive quizzes and track your progress.
            </p>
          </div>
          
          <div className="footer-section">
            <h4>Quick Links</h4>
            <ul className="footer-links">
              <li><Link to="/">Home</Link></li>
              <li><Link to="/quizzes">Browse Quizzes</Link></li>
              <li><Link to="/my-results">My Results</Link></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>Features</h4>
            <ul className="footer-links">
              <li>Interactive Quizzes</li>
              <li>Progress Tracking</li>
              <li>Score Analytics</li>
              <li>Multiple Categories</li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>Connect</h4>
            <div className="social-links">
              <a href="#" className="social-link">📧</a>
              <a href="#" className="social-link">🐦</a>
              <a href="#" className="social-link">📘</a>
              <a href="#" className="social-link">💼</a>
            </div>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p>&copy; {currentYear} QuizMaster. Built with React & Flask.</p>
          <div className="footer-bottom-links">
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
            <a href="#">Contact</a>
          </div>
        </div>
      </div>
    </footer>
  );
}