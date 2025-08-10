const API_BASE = "/api"  // Use relative URLs for monorepo
import { authHeader, getUser } from "./auth"

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let msg = `HTTP ${res.status}`
    try {
      const data = await res.json()
      msg = (data as any)?.error ?? msg
    } catch {}
    throw new Error(msg)
  }
  return res.json()
}

export type Category = { id: number; category_name: string }
export type Quiz = { id: number; title: string; category_id: number; category_name?: string }
export type Question = {
  id: number
  question_text: string
  option_a?: string
  option_b?: string
  option_c?: string
  option_d?: string
}
export type SubmitResult = { result_id: number; score: number; total: number }
export type ResultDetail = {
  id: number
  question_id: number
  points: number
  correct_ans: number | null
  submitted_ans: number | null
  time_taken: number | null
}
export type UserResultSummary = {
  id: number
  title: string
  completed_at: string | null
  total_questions: number
  correct_questions: number
  time_taken: number | null
}

// Basic helpers
export const getCurrentUser = (): number => {
  const val = localStorage.getItem("userId")
  return val ? Number(val) : 1
}
export const setCurrentUser = (id: number) => localStorage.setItem("userId", String(id))

// Categories
export async function fetchCategories(): Promise<Category[]> {
  const res = await fetch(`${API_BASE}/categories`)
  return handleResponse(res)
}

// Quizzes
export async function fetchQuizzes(): Promise<Quiz[]> {
  const res = await fetch(`${API_BASE}/quizzes`)
  return handleResponse(res)
}

// Questions
export async function getQuestions(quizId: number | string): Promise<Question[]> {
  const res = await fetch(`${API_BASE}/questions/${quizId}`)
  return handleResponse(res)
}

// Submit
export async function submitAnswers(opts: {
  quizId: number | string
  answers: Record<number, number>
  times?: Record<number, number>
  timeTotal?: number
}) {
  const user = getUser()
  if (!user) throw new Error("Not authenticated")
  const res = await fetch(`${API_BASE}/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify({
      quiz_id: Number(opts.quizId),
      user_id: user.id,
      answers: opts.answers,
      times: opts.times ?? {},
      time_taken: opts.timeTotal ?? 0,
    }),
  })
  if (!res.ok) throw new Error((await res.json()).error || `HTTP ${res.status}`)
  return res.json()
}

// Results
export async function getResultDetails(resultId: number | string): Promise<ResultDetail[]> {
  const res = await fetch(`${API_BASE}/result_details/${resultId}`)
  return handleResponse(res)
}

export async function getUserResults(userId?: number | string) {
  const user = getUser()
  const id = userId ?? user?.id
  if (!id) throw new Error("Not authenticated")
  const res = await fetch(`${API_BASE}/results/${id}`, { headers: { ...authHeader() } })
  if (!res.ok) throw new Error((await res.json()).error || `HTTP ${res.status}`)
  return res.json()
}