// src/pages/ResultsPage.js
import React, { useEffect, useState } from "react";
import { useLocation, useParams, Link } from "react-router-dom";
import { getResultDetails, getQuestions } from "../services/api";

export default function ResultsPage() {
  const { resultId } = useParams();
  const { state } = useLocation();
  const [resultDetails, setResultDetails] = useState([]);
  const [questions, setQuestions] = useState({});
  const [loading, setLoading] = useState(true);
  
  const scoreData = state?.scoreData || {};
  const { score, total } = scoreData;
  
  useEffect(() => {
    async function fetchResultDetails() {
      try {
        if (resultId) {
          // Fetch detailed results
          const details = await getResultDetails(resultId);
          setResultDetails(details);

          // If we have quizId, fetch questions for display
          if (state?.quizId) {
            const quizQuestions = await getQuestions(state.quizId);
            const questionMap = {};
            quizQuestions.forEach(q => {
              questionMap[q.id] = q;
            });
            setQuestions(questionMap);
          }
        }
      } catch (error) {
        console.error("Error fetching result details:", error);
      } finally {
        setLoading(false);
      }
    }

    fetchResultDetails();
  }, [resultId, state?.quizId]);

  const getScorePercentage = () => {
    if (!total || total === 0) return 0;
    return Math.round((score / total) * 100);
  };

  const getScoreColor = () => {
    const percentage = getScorePercentage();
    if (percentage >= 80) return '#4CAF50'; // Green
    if (percentage >= 60) return '#FF9800'; // Orange
    return '#f44336'; // Red
  };

  const formatTime = (seconds) => {
    if (!seconds) return '0s';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
  };

  if (loading) {
    return (
      <div className="results-container">
        <div className="loading-spinner">Loading results...</div>
      </div>
    );
  }

  return (
    <div className="results-container">
      <div className="results-header">
        <h1>Quiz Results</h1>
        <div className="score-display" style={{ borderColor: getScoreColor() }}>
          <div className="score-circle" style={{ backgroundColor: getScoreColor() }}>
            <span className="score-text">{getScorePercentage()}%</span>
          </div>
          <div className="score-details">
            <h2>Your Score</h2>
            <p className="score-fraction">{score} / {total}</p>
            <p className="score-label">
              {getScorePercentage() >= 80 ? 'Excellent!' :
               getScorePercentage() >= 60 ? 'Good Job!' : 'Keep Practicing!'}
            </p>
          </div>
        </div>
      </div>

      {resultDetails.length > 0 && (
        <div className="detailed-results">
          <h3>Question-by-Question Results</h3>
          <div className="question-results">
            {resultDetails.map((detail, index) => {
              const question = questions[detail.question_id];
              const isCorrect = detail.points > 0;
              
              return (
                <div key={detail.id} className={`question-result ${isCorrect ? 'correct' : 'incorrect'}`}>
                  <div className="question-header">
                    <span className="question-number">Question {index + 1}</span>
                    <span className={`result-badge ${isCorrect ? 'correct' : 'incorrect'}`}>
                      {isCorrect ? '✓ Correct' : '✗ Incorrect'}
                    </span>
                    <span className="time-taken">
                      Time: {formatTime(detail.time_taken)}
                    </span>
                  </div>
                  
                  {question && (
                    <div className="question-content">
                      <p className="question-text">{question.question_text}</p>
                      
                      <div className="answer-comparison">
                        <div className="submitted-answer">
                          <strong>Your Answer:</strong>
                          <span className={isCorrect ? 'correct-answer' : 'wrong-answer'}>
                            {getOptionText(question, detail.submitted_ans)}
                          </span>
                        </div>
                        
                        {!isCorrect && (
                          <div className="correct-answer-display">
                            <strong>Correct Answer:</strong>
                            <span className="correct-answer">
                              {getOptionText(question, detail.correct_ans)}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="results-actions">
        <Link to="/" className="btn btn-primary">
          Back to Home
        </Link>
        <Link to="/quizzes" className="btn btn-secondary">
          Take Another Quiz
        </Link>
      </div>
    </div>
  );
}

// Helper function to get option text
function getOptionText(question, optionIndex) {
  if (!question || optionIndex === null || optionIndex === undefined) {
    return 'No answer';
  }
  
  const options = ['option_a', 'option_b', 'option_c', 'option_d'];
  const optionKey = options[optionIndex];
  const optionText = question[optionKey];
  const optionLetter = String.fromCharCode(65 + optionIndex); // A, B, C, D
  
  return optionText ? `${optionLetter}. ${optionText}` : 'No answer';
}