import React, { useEffect, useState } from "react";
import { getQuestions, submitAnswers } from "../services/api";
import Question from "../components/Question";
import { useParams, useNavigate } from "react-router-dom";

export default function QuizPage() {
  const { quizId } = useParams();
  const [questions, setQuestions] = useState([]);
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

  const handleSubmit = async () => {
    const res = await submitAnswers(quizId, answers);
    navigate(`/results`, { state: { scoreData: res } });
};

  return (
    <div>
      <h2>Quiz</h2>
      {questions.map((q) => (
        <Question
          key={q.id}
          question={q}
          selectedAnswer={answers[q.id]}
          onAnswerChange={handleAnswerChange}
        />
      ))}
      <button onClick={handleSubmit}>Submit</button>
    </div>
  );
}
