import { useEffect, useMemo, useState } from "react"
import { Link } from "react-router-dom"
import { fetchCategories, fetchQuizzes } from "@/services/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import { Skeleton } from "@/components/ui/skeleton"

type Category = { id: number; category_name: string }
type Quiz = { id: number; title: string; category_id: number }

export default function QuizList() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [quizzes, setQuizzes] = useState<Quiz[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [selected, setSelected] = useState<string>("all")
  const [query, setQuery] = useState("")

  useEffect(() => {
    ;(async () => {
      try {
        setLoading(true)
        const [qs, cs] = await Promise.all([fetchQuizzes(), fetchCategories()])
        setQuizzes(qs)
        setCategories(cs)
        setError(null)
      } catch (e: any) {
        setError(e?.message ?? "Failed to load quizzes.")
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  const filtered = useMemo(() => {
    let list = quizzes
    if (selected !== "all") list = list.filter(q => String(q.category_id) === selected)
    if (query.trim()) list = list.filter(q => q.title.toLowerCase().includes(query.toLowerCase()))
    return list
  }, [quizzes, selected, query])

  return (
    <div className="mx-auto max-w-6xl px-4">
      <header className="mb-6 mt-2">
        <h1 className="text-2xl font-bold">Available Quizzes</h1>
        <p className="text-muted-foreground">Choose a quiz to test your knowledge.</p>
      </header>

      <div className="mb-6 flex flex-wrap items-center gap-3">
        <Input
          placeholder="Search quizzes…"
          className="max-w-xs"
          value={query}
          onChange={e => setQuery(e.target.value)}
        />
        <ToggleGroup type="single" value={selected} onValueChange={(v) => setSelected(v || "all")} className="flex flex-wrap">
          <ToggleGroupItem value="all">All</ToggleGroupItem>
          {categories.map(c => (
            <ToggleGroupItem key={c.id} value={String(c.id)}>{c.category_name}</ToggleGroupItem>
          ))}
        </ToggleGroup>
      </div>

      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i} className="p-4">
              <Skeleton className="h-5 w-1/2" />
              <Skeleton className="mt-3 h-4 w-2/3" />
              <Skeleton className="mt-6 h-10 w-full" />
            </Card>
          ))}
        </div>
      ) : error ? (
        <div className="rounded-md border p-4 text-sm">
          <p className="font-medium text-destructive">Error</p>
          <p className="text-muted-foreground">{error}</p>
        </div>
      ) : filtered.length === 0 ? (
        <div className="rounded-lg border p-10 text-center">
          <h3 className="text-lg font-semibold">No quizzes found</h3>
          <p className="text-muted-foreground">Try a different category or search.</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map(q => (
            <Card key={q.id} className="flex flex-col">
              <CardHeader>
                <CardTitle className="flex items-center justify-between gap-2">
                  <span className="line-clamp-1">{q.title}</span>
                  {categories.find(c => c.id === q.category_id) && (
                    <Badge variant="outline">{categories.find(c => c.id === q.category_id)?.category_name}</Badge>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent className="mt-auto">
                <Link to={`/quiz/${q.id}`}><Button className="w-full">Start quiz</Button></Link>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}