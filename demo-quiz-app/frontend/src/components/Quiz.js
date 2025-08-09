// src/components/Quiz.js
import React, { useEffect, useState } from "react";
import Question from "./Question";
import { getQuestions, submitAnswers } from "../services/api";
import { useNavigate } from "react-router-dom";

export default function Quiz({ quizId }) {
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchQuestions() {
      const res = await getQuestions(quizId);
      setQuestions(res);
    }
    fetchQuestions();
  }, [quizId]);

  const handleAnswerChange = (questionId, selectedOption) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: selectedOption
    }));
  };

  const nextQuestion = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    }
  };

  const prevQuestion = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
    }
  };

  const handleSubmit = async () => {
    const res = await submitAnswers(quizId, answers);
    navigate(`/results`, { state: { scoreData: res } });
  };

  if (!questions.length) return <p>Loading quiz...</p>;

  return (
    <div>
      <h2>Quiz</h2>
      <Question
        question={questions[currentIndex]}
        selectedAnswer={answers[questions[currentIndex].id]}
        onAnswerChange={handleAnswerChange}
      />

      <div style={{ marginTop: "1rem" }}>
        {currentIndex > 0 && (
          <button onClick={prevQuestion}>Previous</button>
        )}
        {currentIndex < questions.length - 1 ? (
          <button onClick={nextQuestion}>Next</button>
        ) : (
          <button onClick={handleSubmit}>Submit</button>
        )}
      </div>
      <p>
        Question {currentIndex + 1} of {questions.length}
      </p>
    </div>
  );
}
