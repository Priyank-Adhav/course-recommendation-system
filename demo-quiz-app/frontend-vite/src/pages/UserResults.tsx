import { useEffect, useMemo, useState } from "react"
import { Link } from "react-router-dom"
import { getCurrentUser, getUserResults, type UserResultSummary } from "@/services/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"

export default function UserResults() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [results, setResults] = useState<UserResultSummary[]>([])
  const userId = getCurrentUser()

  useEffect(() => {
    ;(async () => {
      try {
        setLoading(true)
        const rs = await getUserResults(userId)
        rs.sort((a, b) => new Date(b.completed_at || 0).getTime() - new Date(a.completed_at || 0).getTime())
        setResults(rs)
        setError(null)
      } catch (e: any) {
        setError(e?.message ?? "Failed to load your results.")
      } finally {
        setLoading(false)
      }
    })()
  }, [userId])

  const stats = useMemo(() => {
    if (!results.length) return { count: 0, avg: 0, best: 0 }
    const percents = results.map(r => Math.round((r.correct_questions / Math.max(1, r.total_questions)) * 100))
    const avg = Math.round(percents.reduce((s, v) => s + v, 0) / percents.length)
    const best = Math.max(...percents)
    return { count: results.length, avg, best }
  }, [results])

  if (loading) {
    return (
      <div className="mx-auto max-w-6xl px-4">
        <div className="grid gap-4 md:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => <Card key={i} className="p-6"><Skeleton className="h-6 w-1/2" /><Skeleton className="mt-3 h-4 w-1/3" /></Card>)}
        </div>
      </div>
    )
  }
  if (error) {
    return (
      <div className="mx-auto max-w-6xl px-4">
        <div className="rounded-md border p-4">
          <p className="font-medium text-destructive">Error</p>
          <p className="text-muted-foreground">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-6xl px-4">
      <header className="mb-6 mt-2">
        <h1 className="text-2xl font-bold">Your Results</h1>
        <p className="text-muted-foreground">Track your progress and see improvements.</p>
      </header>

      <section className="grid gap-4 md:grid-cols-3">
        <Card><CardHeader><CardTitle>Quizzes Taken</CardTitle></CardHeader><CardContent><p className="text-3xl font-bold">{stats.count}</p></CardContent></Card>
        <Card><CardHeader><CardTitle>Average Score</CardTitle></CardHeader><CardContent><p className="text-3xl font-bold">{stats.avg}%</p></CardContent></Card>
        <Card><CardHeader><CardTitle>Best Score</CardTitle></CardHeader><CardContent><p className="text-3xl font-bold">{stats.best}%</p></CardContent></Card>
      </section>

      {results.length === 0 ? (
        <div className="mt-8 rounded-lg border p-10 text-center">
          <h3 className="text-lg font-semibold">No results yet</h3>
          <p className="text-muted-foreground">Take your first quiz to see results here.</p>
          <div className="mt-4"><Link to="/quizzes"><Button>Browse quizzes</Button></Link></div>
        </div>
      ) : (
        <section className="mt-8">
          <h2 className="mb-3 text-lg font-semibold">Recent Results</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {results.map(r => {
              const pct = Math.round((r.correct_questions / Math.max(1, r.total_questions)) * 100)
              const chip = pct >= 80 ? "bg-green-500" : pct >= 60 ? "bg-amber-500" : "bg-rose-500"
              return (
                <Card key={r.id} className="flex flex-col">
                  <CardHeader>
                    <CardTitle className="line-clamp-1">{r.title}</CardTitle>
                  </CardHeader>
                  <CardContent className="mt-auto">
                    <div className="mb-3 flex items-center gap-3">
                      <div className={`flex h-10 w-10 items-center justify-center rounded-full text-xs font-bold text-white ${chip}`}>{pct}%</div>
                      <div className="text-sm text-muted-foreground">{formatDate(r.completed_at)}</div>
                    </div>
                    <Link to={`/results/${r.id}`}><Button variant="outline" className="w-full">View details</Button></Link>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </section>
      )}
    </div>
  )
}

function formatDate(d: string | null) {
  if (!d) return "Unknown"
  try {
    return new Date(d).toLocaleString()
  } catch {
    return d
  }
}