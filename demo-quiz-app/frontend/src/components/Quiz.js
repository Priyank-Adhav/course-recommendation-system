// src/components/Quiz.js
import React, { useEffect, useState } from "react";
import Question from "./Question";
import { getQuestions, submitAnswers } from "../services/api";
import { useNavigate, useParams } from "react-router-dom";

export default function Quiz() {
  const { quizId } = useParams(); // Get quizId from URL params
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [startTime] = useState(Date.now());
  const [questionTimes, setQuestionTimes] = useState({});
  const [questionStartTime, setQuestionStartTime] = useState(Date.now());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchQuestions() {
      try {
        setLoading(true);
        const res = await getQuestions(quizId);
        setQuestions(res);
        setQuestionStartTime(Date.now());
        setError(null);
      } catch (err) {
        setError("Failed to load quiz questions. Please try again.");
        console.error("Error fetching questions:", err);
      } finally {
        setLoading(false);
      }
    }
    
    if (quizId) {
      fetchQuestions();
    }
  }, [quizId]);

  const handleAnswerChange = (questionId, selectedOption) => {
    // Record time spent on current question
    const timeSpent = Math.floor((Date.now() - questionStartTime) / 1000);
    setQuestionTimes(prev => ({
      ...prev,
      [questionId]: timeSpent
    }));

    setAnswers((prev) => ({
      ...prev,
      [questionId]: selectedOption
    }));
  };

  const nextQuestion = () => {
    if (currentIndex < questions.length - 1) {
      // Record time for current question before moving
      const currentQuestion = questions[currentIndex];
      const timeSpent = Math.floor((Date.now() - questionStartTime) / 1000);
      setQuestionTimes(prev => ({
        ...prev,
        [currentQuestion.id]: timeSpent
      }));

      setCurrentIndex((prev) => prev + 1);
      setQuestionStartTime(Date.now());
    }
  };

  const prevQuestion = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
      setQuestionStartTime(Date.now());
    }
  };

  const handleSubmit = async () => {
    try {
      // Record time for last question
      const currentQuestion = questions[currentIndex];
      const timeSpent = Math.floor((Date.now() - questionStartTime) / 1000);
      const finalQuestionTimes = {
        ...questionTimes,
        [currentQuestion.id]: timeSpent
      };

      const totalTime = Math.floor((Date.now() - startTime) / 1000);
      
      // Get user ID (you might want to implement proper user authentication)
      const userId = localStorage.getItem('userId') || 1; // Default to user 1 for demo
      
      const res = await submitAnswers(
        quizId, 
        userId, 
        answers, 
        finalQuestionTimes, 
        totalTime
      );
      
      navigate(`/results/${res.result_id}`, { 
        state: { 
          scoreData: res,
          quizId: quizId
        } 
      });
    } catch (err) {
      setError("Failed to submit quiz. Please try again.");
      console.error("Error submitting quiz:", err);
    }
  };

  if (loading) {
    return (
      <div className="quiz-container">
        <div className="loading-spinner">Loading quiz...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="quiz-container">
        <div className="error-message">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={() => navigate('/')}>Go Home</button>
        </div>
      </div>
    );
  }

  if (!questions.length) {
    return (
      <div className="quiz-container">
        <div className="no-questions">
          <h2>No Questions Found</h2>
          <p>This quiz doesn't have any questions yet.</p>
          <button onClick={() => navigate('/')}>Go Home</button>
        </div>
      </div>
    );
  }

  const currentQuestion = questions[currentIndex];
  const progress = Math.round(((currentIndex + 1) / questions.length) * 100);

  return (
    <div className="quiz-container">
      <div className="quiz-header">
        <h2>Quiz</h2>
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        <p className="progress-text">
          Question {currentIndex + 1} of {questions.length}
        </p>
      </div>

      <Question
        question={currentQuestion}
        selectedAnswer={answers[currentQuestion.id]}
        onAnswerChange={handleAnswerChange}
      />

      <div className="quiz-navigation">
        {currentIndex > 0 && (
          <button 
            onClick={prevQuestion}
            className="nav-btn prev-btn"
          >
            Previous
          </button>
        )}
        
        <div className="nav-right">
          {currentIndex < questions.length - 1 ? (
            <button 
              onClick={nextQuestion}
              className="nav-btn next-btn"
            >
              Next
            </button>
          ) : (
            <button 
              onClick={handleSubmit}
              className="nav-btn submit-btn"
              disabled={Object.keys(answers).length !== questions.length}
            >
              Submit Quiz
            </button>
          )}
        </div>
      </div>

      {/* Answer Summary */}
      <div className="answer-summary">
        <h4>Progress:</h4>
        <div className="question-indicators">
          {questions.map((q, idx) => (
            <span
              key={q.id}
              className={`question-indicator ${
                answers[q.id] !== undefined ? 'answered' : ''
              } ${idx === currentIndex ? 'current' : ''}`}
              onClick={() => setCurrentIndex(idx)}
            >
              {idx + 1}
            </span>
          ))}
        </div>
        <p>
          Answered: {Object.keys(answers).length} / {questions.length}
        </p>
      </div>
    </div>
  );
}