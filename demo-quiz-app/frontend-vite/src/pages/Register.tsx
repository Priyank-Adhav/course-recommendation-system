import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import { register as apiRegister, saveAuth } from "@/services/auth"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

export default function Register() {
  const nav = useNavigate()
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setLoading(true); setError(null)
      const res = await apiRegister(name.trim(), email.trim(), password)
      saveAuth(res.token, res.user)
      nav("/")
    } catch (err: any) {
      setError(err?.message ?? "Registration failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-md px-4">
      <Card className="mt-10">
        <div className="h-1 w-full bg-gradient-to-r from-cyan-500 to-blue-600" />
        <CardHeader>
          <CardTitle>Create your account</CardTitle>
          <CardDescription>It only takes a minute</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="space-y-4">
            <div>
              <label className="mb-1 block text-sm text-muted-foreground">Name</label>
              <Input placeholder="Jane Doe" value={name} onChange={e=>setName(e.target.value)} required />
            </div>
            <div>
              <label className="mb-1 block text-sm text-muted-foreground">Email</label>
              <Input type="email" placeholder="you@example.com" value={email} onChange={e=>setEmail(e.target.value)} required />
            </div>
            <div>
              <label className="mb-1 block text-sm text-muted-foreground">Password</label>
              <Input type="password" placeholder="••••••••" value={password} onChange={e=>setPassword(e.target.value)} required />
            </div>
            {error && <p className="text-sm text-rose-600">{error}</p>}
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Creating…" : "Create account"}
            </Button>
            <p className="text-center text-sm text-muted-foreground">
              Already have an account? <Link className="text-primary underline underline-offset-4" to="/login">Sign in</Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}