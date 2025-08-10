const API = import.meta.env.VITE_API_BASE ?? "http://localhost:5000"

type User = { id: number; name: string; email: string }
type AuthResponse = { token: string; user: User }

export async function register(name: string, email: string, password: string): Promise<AuthResponse> {
  const r = await fetch(`${API}/api/auth/register`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password })
  })
  const j = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(j.error || `HTTP ${r.status}`)
  return j
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  const r = await fetch(`${API}/api/auth/login`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  })
  const j = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(j.error || `HTTP ${r.status}`)
  return j
}

export function saveAuth(token: string, user: User) {
  localStorage.setItem("token", token)
  localStorage.setItem("user", JSON.stringify(user))
}
export function logout() {
  localStorage.removeItem("token")
  localStorage.removeItem("user")
}
export function getToken(): string | null { return localStorage.getItem("token") }
export function getUser(): User | null {
  const s = localStorage.getItem("user")
  return s ? JSON.parse(s) as User : null
}
export function authHeader(): HeadersInit {
  const t = getToken()
  return t ? { Authorization: `Bearer ${t}` } : {}
}