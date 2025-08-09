// src/services/api.js
const API_BASE = "http://localhost:5000"; // Flask backend URL

export const fetchQuizzes = async () => {
    const res = await fetch(`${API_BASE}/quiz/list`);
    return res.json();
};

export const submitAnswers = async (quizId, answers) => {
    const res = await fetch(`${API_BASE}/quiz/submit_answers`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quiz_id: quizId, answers })
    });
    return res.json();
};

export async function getQuestions(quizId) {
  const res = await fetch(`${API_BASE}/quiz/questions/${quizId}`);
  return await res.json();
}

