import { useEffect, useState } from "react"
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { BookOpen, Sparkles, Link2, Loader2 } from "lucide-react"

type Course = {
  title: string
  provider: string
  level: string
  url: string
  score: number
}

type Section = {
  title: string
  courses: Course[]
}

export default function Recommendations() {
  const [query, setQuery] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [searchResults, setSearchResults] = useState<Course[]>([])
  const [personalized, setPersonalized] = useState<{
    struggled_section?: Section
    strong_section?: Section
    interest_section?: Section
  }>({})

  const [userId, setUserId] = useState<number | null>(null)

  // load user ID from localStorage
  useEffect(() => {
    try {
      const storedUser = localStorage.getItem("user")
      if (storedUser) {
        const parsed = JSON.parse(storedUser)
        if (parsed?.id) {
          setUserId(parsed.id)
          fetchUserRecommendations(parsed.id)
        }
      }
    } catch (e) {
      console.error("Error reading user from localStorage:", e)
    }
  }, [])

  // 🔍 manual search
  async function fetchRecommendations() {
    if (!query.trim()) return
    setLoading(true)
    setError("")
    setSearchResults([])

    try {
      const res = await fetch(
        `http://localhost:5000/api/recommendations?query=${encodeURIComponent(
          query
        )}`
      )
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || "Failed to fetch recommendations")
      setSearchResults(data)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  // 🧠 personalized fetch by user_id
  async function fetchUserRecommendations(id: number) {
    setLoading(true)
    setError("")
    setPersonalized({})
    try {
      const res = await fetch(`http://localhost:5000/api/recommendations?user_id=${id}`)
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || "Failed to fetch personalized recommendations")
      setPersonalized(data)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-4 pb-10">
      {/* Header */}
      <header className="mb-6 mt-2 text-center">
        <h1 className="text-3xl font-bold flex justify-center items-center gap-2">
          <Sparkles className="text-cyan-500 h-7 w-7" />
          Course Recommendations
        </h1>
        <p className="text-muted-foreground">
          Personalized learning paths based on your quiz performance and interests.
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

      {/* Personalized trigger */}
      {userId && (
        <div className="flex justify-center mb-10">
          <Button
            variant="secondary"
            onClick={() => fetchUserRecommendations(userId)}
            disabled={loading}
          >
            {loading ? <Loader2 className="animate-spin h-4 w-4 mr-2" /> : null}
            Refresh My Personalized Recommendations
          </Button>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 p-4 text-red-700 mb-6 text-sm text-center">
          {error}
        </div>
      )}

      {/* Search Results */}
      {searchResults.length > 0 && (
        <>
          <h2 className="text-xl font-semibold mb-4">Search Results</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 mb-10">
            {searchResults.map((r, i) => (
              <CourseCard key={i} r={r} />
            ))}
          </div>
        </>
      )}

      {/* Personalized Sections */}
      {personalized.struggled_section && (
        <SectionBlock section={personalized.struggled_section} />
      )}
      {personalized.strong_section && (
        <SectionBlock section={personalized.strong_section} />
      )}
      {personalized.interest_section && (
        <SectionBlock section={personalized.interest_section} />
      )}

      {/* Empty State */}
      {!loading &&
        !error &&
        searchResults.length === 0 &&
        !personalized.struggled_section &&
        !personalized.strong_section &&
        !personalized.interest_section && (
          <div className="text-center mt-10 text-muted-foreground">
            Search for a topic or view your personalized course recommendations.
          </div>
        )}
    </div>
  )
}

function CourseCard({ r }: { r: Course }) {
  return (
    <Card className="transition-all hover:-translate-y-0.5 hover:shadow-md">
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
          <span className="text-xs text-muted-foreground">
            Score: {r.score.toFixed(3)}
          </span>
        </div>
      </CardContent>
    </Card>
  )
}

function SectionBlock({ section }: { section: Section }) {
  return (
    <div className="mb-12">
      <h2 className="text-xl font-semibold mb-4">{section.title}</h2>
      {section.courses.length === 0 ? (
        <p className="text-sm text-muted-foreground mb-6">
          No relevant courses found for this section.
        </p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {section.courses.map((r, i) => (
            <CourseCard key={i} r={r} />
          ))}
        </div>
      )}
    </div>
  )
}
