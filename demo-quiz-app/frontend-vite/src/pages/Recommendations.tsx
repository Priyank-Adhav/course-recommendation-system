import { useState } from "react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { BookOpen, Sparkles, Link2, Loader2 } from "lucide-react"

type Recommendation = {
  title: string
  provider: string
  level: string
  url: string
  score: number
}

export default function Recommendations() {
  const [query, setQuery] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [results, setResults] = useState<Recommendation[]>([])

  async function fetchRecommendations() {
    if (!query.trim()) return
    setLoading(true)
    setError("")
    setResults([])

    try {
      const res = await fetch(`http://localhost:5000/api/recommendations?query=${encodeURIComponent(query)}`)
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || "Failed to fetch recommendations")
      setResults(data)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-4">
      {/* Header */}
      <header className="mb-6 mt-2 text-center">
        <h1 className="text-3xl font-bold flex justify-center items-center gap-2">
          <Sparkles className="text-cyan-500 h-7 w-7" />
          Course Recommendations
        </h1>
        <p className="text-muted-foreground">
          Discover relevant courses and resources tailored to your interests.
        </p>
      </header>

      {/* Search bar */}
      <div className="flex flex-wrap justify-center gap-3 mb-8">
        <Input
          placeholder="Enter a topic or skill (e.g. data science, AI, cybersecurity)…"
          className="max-w-lg"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && fetchRecommendations()}
        />
        <Button onClick={fetchRecommendations} disabled={loading || !query.trim()}>
          {loading ? <Loader2 className="animate-spin h-4 w-4 mr-2" /> : null}
          {loading ? "Searching…" : "Search"}
        </Button>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 p-4 text-red-700 mb-6 text-sm">
          {error}
        </div>
      )}

      {/* Results */}
      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i} className="p-4 animate-pulse">
              <div className="h-5 w-3/4 bg-gray-200 rounded mb-2" />
              <div className="h-4 w-1/2 bg-gray-200 rounded mb-4" />
              <div className="h-10 w-full bg-gray-200 rounded" />
            </Card>
          ))}
        </div>
      ) : results.length === 0 && !error ? (
        <div className="text-center mt-10 text-muted-foreground">
          {query
            ? "No recommendations found. Try a different keyword."
            : "Search for a topic to get personalized course suggestions."}
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {results.map((r, i) => (
            <Card key={i} className="transition-all hover:-translate-y-0.5 hover:shadow-md">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <BookOpen className="h-5 w-5 text-cyan-500" /> {r.title}
                </CardTitle>
                <CardDescription className="text-sm text-muted-foreground">
                  {r.provider} • {r.level}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <a
                    href={r.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-sm text-blue-600 hover:underline"
                  >
                    <Link2 className="h-4 w-4" /> View Course
                  </a>
                  <span className="text-xs text-muted-foreground">Score: {r.score.toFixed(3)}</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
