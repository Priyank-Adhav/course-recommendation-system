// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';

// Import components
import HomePage from './pages/HomePage';
import QuizList from './components/QuizList';
import Quiz from './components/Quiz';
import ResultsPage from './pages/ResultsPage';
import UserResults from './pages/UserResults';
import Navigation from './components/Navigation';
import Footer from './components/Footer';

function App() {
  return (
    <Router>
      <div className="App">
        <Navigation />
        <main className="main-content">
          <Routes>
            {/* Home page */}
            <Route path="/" element={<HomePage />} />
            
            {/* Quiz listing page */}
            <Route path="/quizzes" element={<QuizList />} />
            
            {/* Individual quiz taking */}
            <Route path="/quiz/:quizId" element={<Quiz />} />
            
            {/* Results page after completing a quiz */}
            <Route path="/results/:resultId" element={<ResultsPage />} />
            
            {/* User's all results */}
            <Route path="/my-results" element={<UserResults />} />
            
            {/* 404 page */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

// 404 Component
function NotFound() {
  return (
    <div className="not-found">
      <div className="not-found-content">
        <h1>404</h1>
        <h2>Page Not Found</h2>
        <p>The page you're looking for doesn't exist.</p>
        <Link to="/" className="btn btn-primary">
          Go Home
        </Link>
      </div>
    </div>
  );
}

export default App;