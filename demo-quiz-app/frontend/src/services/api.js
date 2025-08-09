// src/services/api.js
const API_BASE = "http://localhost:5000"; // Flask backend URL

// Helper function to handle API responses
const handleResponse = async (response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Network error' }));
    throw new Error(errorData.error || `HTTP ${response.status}`);
  }
  return response.json();
};

// Users API
export const createUser = async (name, email) => {
  const response = await fetch(`${API_BASE}/users`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email })
  });
  return handleResponse(response);
};

// Categories API
export const fetchCategories = async () => {
  const response = await fetch(`${API_BASE}/categories`);
  return handleResponse(response);
};

export const createCategory = async (unique_id, name) => {
  const response = await fetch(`${API_BASE}/categories`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ unique_id, name })
  });
  return handleResponse(response);
};

// Quizzes API
export const fetchQuizzes = async () => {
  const response = await fetch(`${API_BASE}/quizzes`);
  return handleResponse(response);
};

export const createQuiz = async (title, category_id) => {
  const response = await fetch(`${API_BASE}/quizzes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, category_id })
  });
  return handleResponse(response);
};

// Questions API
export const getQuestions = async (quizId) => {
  const response = await fetch(`${API_BASE}/questions/${quizId}`);
  return handleResponse(response);
};

export const addQuestions = async (questions) => {
  const response = await fetch(`${API_BASE}/questions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(questions)
  });
  return handleResponse(response);
};

// Submit Quiz Answers
export const submitAnswers = async (quizId, userId, answers, times = {}, timeTotal = 0) => {
  const response = await fetch(`${API_BASE}/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      quiz_id: parseInt(quizId),
      user_id: parseInt(userId),
      answers: answers,
      times: times,
      time_taken: timeTotal
    })
  });
  return handleResponse(response);
};

// Results API
export const getUserResults = async (userId) => {
  const response = await fetch(`${API_BASE}/results/${userId}`);
  return handleResponse(response);
};

export const getResultDetails = async (resultId) => {
  const response = await fetch(`${API_BASE}/result_details/${resultId}`);
  return handleResponse(response);
};

// Utility API
export const clearAllData = async () => {
  const response = await fetch(`${API_BASE}/clear_all`, {
    method: "POST",
    headers: { "Content-Type": "application/json" }
  });
  return handleResponse(response);
};

// Authentication helpers (for demo purposes)
export const setCurrentUser = (userId) => {
  localStorage.setItem('userId', userId.toString());
};

export const getCurrentUser = () => {
  return localStorage.getItem('userId') || '1'; // Default to user 1
};

export const clearCurrentUser = () => {
  localStorage.removeItem('userId');
};