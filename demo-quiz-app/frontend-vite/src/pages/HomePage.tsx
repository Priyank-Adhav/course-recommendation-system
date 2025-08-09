import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { fetchCategories, fetchQuizzes } from "@/services/api"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Library, Tags, UserRound, PlayCircle, BarChart3, ArrowRight } from "lucide-react"

function AuroraBG() {
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
      <div className="absolute -top-32 -left-32 h-72 w-72 rounded-full bg-cyan-500/30 blur-3xl" />
      <div className="absolute top-20 -right-20 h-72 w-72 rounded-full bg-blue-600/30 blur-3xl" />
      <div className="absolute bottom-0 left-1/2 h-56 w-56 -translate-x-1/2 rounded-full bg-cyan-400/20 blur-2xl" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(255,255,255,0.08),transparent_50%)] dark:bg-[radial-gradient(ellipse_at_center,rgba(255,255,255,0.04),transparent_50%)]" />
    </div>
  )
}

export default function HomePage() {
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({ quizzes: 0, categories: 0 })

  useEffect(() => {
    ;(async () => {
      try {
        setLoading(true)
        const [qs, cs] = await Promise.all([fetchQuizzes(), fetchCategories()])
        setStats({ quizzes: qs.length, categories: cs.length })
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  return (
    <div className="mx-auto max-w-6xl px-4">
      {/* Hero */}
      <section className="relative mt-6 overflow-hidden rounded-2xl border bg-gradient-to-br from-cyan-500 to-blue-600 p-10 text-white shadow">
        <AuroraBG />
        <div className="relative z-10">
          <p className="text-sm uppercase tracking-widest text-white/80">Learn by doing</p>
          <h1 className="mt-2 bg-gradient-to-b from-white to-white/80 bg-clip-text text-4xl font-extrabold leading-tight text-transparent md:text-5xl">
            Quizzes that make learning engaging
          </h1>
          <p className="mt-3 max-w-2xl text-white/90">
            Browse categories, take quizzes, and visualize your progress with beautiful results.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link to="/quizzes">
              <Button size="lg" className="bg-white text-blue-700 hover:opacity-90">
                <PlayCircle className="mr-2 h-5 w-5" /> Browse Quizzes
              </Button>
            </Link>
            <Link to="/my-results">
              <Button size="lg" variant="secondary" className="border-white/20 bg-white/15 text-white hover:bg-white/20">
                <BarChart3 className="mr-2 h-5 w-5" /> My Results
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Quick stats */}
      <section className="mt-8 grid gap-4 md:grid-cols-3">
        <Card className="transition-all hover:-translate-y-0.5 hover:shadow-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Library className="h-5 w-5 text-cyan-500" /> Quizzes
            </CardTitle>
            <CardDescription>Total available</CardDescription>
          </CardHeader>
          <CardContent><p className="text-3xl font-bold">{loading ? "…" : stats.quizzes}</p></CardContent>
        </Card>
        <Card className="transition-all hover:-translate-y-0.5 hover:shadow-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Tags className="h-5 w-5 text-blue-600" /> Categories
            </CardTitle>
            <CardDescription>Topics to explore</CardDescription>
          </CardHeader>
          <CardContent><p className="text-3xl font-bold">{loading ? "…" : stats.categories}</p></CardContent>
        </Card>
        <Card className="transition-all hover:-translate-y-0.5 hover:shadow-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <UserRound className="h-5 w-5 text-cyan-500" /> Get Started
            </CardTitle>
            <CardDescription>Jump in now</CardDescription>
          </CardHeader>
          <CardContent><Link to="/quizzes"><Button className="group">Start a quiz <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-0.5" /></Button></Link></CardContent>
        </Card>
      </section>

      {/* Highlights */}
      <section className="mt-10">
        <div className="mb-4">
          <h2 className="text-xl font-semibold">Why you’ll love it</h2>
          <p className="text-sm text-muted-foreground">Beautiful UI, fast interactions, and clear feedback.</p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[
            { title: "Clean UI", desc: "Modern cards, badges, and smooth motion.", color: "from-cyan-500 to-blue-600" },
            { title: "Keyboard-friendly", desc: "Navigate options quickly and efficiently.", color: "from-blue-600 to-cyan-500" },
            { title: "Dark mode", desc: "Looks great day or night.", color: "from-cyan-400 to-blue-500" },
          ].map((f, i) => (
            <Card key={i} className="relative overflow-hidden transition-all hover:-translate-y-0.5 hover:shadow-md">
              <div className={`pointer-events-none absolute inset-x-0 top-0 h-1 bg-gradient-to-r ${f.color}`} />
              <CardHeader className="pb-2">
                <CardTitle className="text-base">{f.title}</CardTitle>
                <CardDescription>{f.desc}</CardDescription>
              </CardHeader>
              <CardContent />
            </Card>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="mt-10">
        <div className="mb-4">
          <h2 className="text-xl font-semibold">How it works</h2>
          <p className="text-sm text-muted-foreground">Three simple steps to get started.</p>
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          {[ "Choose a quiz", "Answer questions", "See results" ].map((s, i) => (
            <Card key={s} className="transition-all hover:-translate-y-0.5 hover:shadow-md">
              <CardHeader>
                <div className="mb-2 inline-flex h-10 w-10 items-center justify-center rounded-full bg-cyan-500/15 text-cyan-600 dark:bg-cyan-500/20 dark:text-cyan-400">
                  {i + 1}
                </div>
                <CardTitle className="text-base">{s}</CardTitle>
                <CardDescription>
                  {i === 0 && "Browse our collection of quizzes across categories."}
                  {i === 1 && "Pick answers with keyboard or mouse; change anytime."}
                  {i === 2 && "Instant feedback with a detailed breakdown."}
                </CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </section>
    </div>
  )
}