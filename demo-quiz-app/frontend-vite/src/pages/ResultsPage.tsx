import { useEffect, useMemo, useState } from "react"
import { Link, useLocation, useParams } from "react-router-dom"
import { getResultDetails, getQuestions, type ResultDetail, type Question } from "@/services/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"

export default function ResultsPage() {
  const { resultId } = useParams()
  const { state } = useLocation() as { state?: { scoreData?: { score: number; total: number }, quizId?: number | string } }
  const [loading, setLoading] = useState(true)
  const [details, setDetails] = useState<ResultDetail[]>([])
  const [qMap, setQMap] = useState<Record<number, Question>>({})

  const score = state?.scoreData?.score ?? 0
  const total = state?.scoreData?.total ?? 0

  useEffect(() => {
    ;(async () => {
      try {
        setLoading(true)
        const d = await getResultDetails(String(resultId))
        setDetails(d)
        if (state?.quizId) {
          const qs = await getQuestions(state.quizId)
          const map: Record<number, Question> = {}
          qs.forEach(q => { map[q.id] = q })
          setQMap(map)
        }
      } finally {
        setLoading(false)
      }
    })()
  }, [resultId, state?.quizId])

  const percentage = useMemo(() => {
    const denom = total || (details.length || 1)
    const correct = details.reduce((s, r) => s + (r.points > 0 ? 1 : 0), 0)
    return Math.round(((state?.scoreData ? score : correct) / denom) * 100)
  }, [details, score, total, state?.scoreData])

  const color = percentage >= 80 ? "bg-green-500" : percentage >= 60 ? "bg-amber-500" : "bg-rose-500"

  if (loading) {
    return (
      <div className="mx-auto max-w-5xl px-4">
        <Card className="mt-6 p-6">
          <Skeleton className="h-6 w-1/3" />
          <Skeleton className="mt-4 h-24 w-full" />
        </Card>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-5xl px-4">
      <header className="my-4">
        <h1 className="text-2xl font-bold">Quiz Results</h1>
      </header>

      <Card>
        <CardContent className="flex flex-col items-center gap-6 p-6 md:flex-row md:items-center md:justify-center">
          <div className={`flex h-28 w-28 items-center justify-center rounded-full text-xl font-bold text-white ${color}`}>
            {percentage}%
          </div>
          <div className="text-center md:text-left">
            <h2 className="text-xl font-semibold">Your Score</h2>
            <p className="text-muted-foreground">
              {state?.scoreData ? `${score} / ${total}` : `${percentage}%`}
            </p>
            <p className="mt-1 text-sm">
              {percentage >= 80 ? "Excellent!" : percentage >= 60 ? "Good job!" : "Keep practicing!"}
            </p>
          </div>
        </CardContent>
      </Card>

      {details.length > 0 && (
        <Card className="mt-6">
          <CardHeader><CardTitle>Question-by-question</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            {details.map((d, idx) => {
              const q = qMap[d.question_id]
              const isCorrect = d.points > 0
              return (
                <div key={d.id} className={`rounded-md border p-4 ${isCorrect ? "bg-green-50 dark:bg-green-950/20" : "bg-rose-50 dark:bg-rose-950/20"}`}>
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-sm font-medium">Question {idx + 1}</span>
                    <Badge variant={isCorrect ? "success" : "danger"}>{isCorrect ? "✓ Correct" : "✗ Incorrect"}</Badge>
                    {typeof d.time_taken === "number" && <span className="text-xs text-muted-foreground">Time: {formatSec(d.time_taken)}</span>}
                  </div>
                  {q && (
                    <div className="mt-2 space-y-1">
                      <p className="font-medium">{q.question_text}</p>
                      <p className="text-sm">
                        <strong>Your answer:</strong>{" "}
                        <span className={isCorrect ? "" : "text-rose-600 dark:text-rose-400"}>
                          {optionLabel(q, d.submitted_ans)}
                        </span>
                      </p>
                      {!isCorrect && (
                        <p className="text-sm">
                          <strong>Correct answer:</strong>{" "}
                          <span className="text-green-600 dark:text-green-400">
                            {optionLabel(q, d.correct_ans)}
                          </span>
                        </p>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </CardContent>
        </Card>
      )}

      <div className="mt-6 flex flex-wrap gap-3">
        <Link to="/"><Button>Back to Home</Button></Link>
        <Link to="/quizzes"><Button variant="secondary">Take another quiz</Button></Link>
      </div>
    </div>
  )
}

function formatSec(s?: number | null) {
  if (!s) return "0s"
  const m = Math.floor(s / 60)
  const r = s % 60
  return m > 0 ? `${m}m ${r}s` : `${r}s`
}
function optionLabel(q: Question, idx?: number | null) {
  if (idx === undefined || idx === null) return "No answer"
  const keys = ["option_a", "option_b", "option_c", "option_d"] as const
  const key = keys[idx]
  const txt = (q as any)[key] as string | undefined
  const letter = String.fromCharCode(65 + idx)
  return txt ? `${letter}. ${txt}` : "No answer"
}