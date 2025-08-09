import React from "react";
import { useParams } from "react-router-dom";
import Quiz from "../components/Quiz";

export default function QuizPage() {
  const { quizId } = useParams();
  return <Quiz quizId={quizId} />;
}
