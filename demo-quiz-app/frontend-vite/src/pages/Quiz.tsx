import { useEffect, useMemo, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { getQuestions, submitAnswers, type Question } from "@/services/api"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { RadioGroup, RadioCard } from "@/components/ui/radio-group"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import * as Dialog from "@radix-ui/react-dialog"
import { X, ListChecks, Check } from "lucide-react"

export default function Quiz() {
  const { quizId } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [questions, setQuestions] = useState<Question[]>([])
  const [current, setCurrent] = useState(0)
  const [answers, setAnswers] = useState<Record<number, number>>({})
  const [startTime] = useState(Date.now())
  const [qStart, setQStart] = useState(Date.now())
  const [qTimes, setQTimes] = useState<Record<number, number>>({})
  const [reviewOpen, setReviewOpen] = useState(false)
  const [confirmOpen, setConfirmOpen] = useState(false)

  useEffect(() => {
    ;(async () => {
      try {
        setLoading(true)
        const qs = await getQuestions(Number(quizId))
        setQuestions(qs)
        setQStart(Date.now())
        setError(null)
      } catch (e: any) {
        setError(e?.message ?? "Failed to load quiz questions.")
      } finally {
        setLoading(false)
      }
    })()
  }, [quizId])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (!questions.length) return
      if (e.key === "ArrowRight") { e.preventDefault(); next() }
      if (e.key === "ArrowLeft") { e.preventDefault(); prev() }
      const idx = ["1","2","3","4"].indexOf(e.key)
      if (idx >= 0) {
        const q = questions[current]
        if (!q) return
        onSelect(q.id, idx)
      }
    }
    window.addEventListener("keydown", onKey)
    return () => window.removeEventListener("keydown", onKey)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [questions, current, qStart])

  const progress = useMemo(() => (questions.length ? Math.round(((current + 1) / questions.length) * 100) : 0), [current, questions])

  const onSelect = (qid: number, optIndex: number) => {
    const spent = Math.floor((Date.now() - qStart) / 1000)
    setQTimes(prev => ({ ...prev, [qid]: spent }))
    setAnswers(prev => ({ ...prev, [qid]: optIndex }))
  }

  const next = () => {
    if (current < questions.length - 1) {
      const cq = questions[current]
      const spent = Math.floor((Date.now() - qStart) / 1000)
      setQTimes(prev => ({ ...prev, [cq.id]: spent }))
      setCurrent(c => c + 1)
      setQStart(Date.now())
    }
  }
  const prev = () => {
    if (current > 0) {
      setCurrent(c => c - 1)
      setQStart(Date.now())
    }
  }

  const submit = async () => {
    try {
      const cq = questions[current]
      const spent = Math.floor((Date.now() - qStart) / 1000)
      const finalTimes = { ...qTimes, [cq.id]: spent }
      const total = Math.floor((Date.now() - startTime) / 1000)
      const res = await submitAnswers({
        quizId: Number(quizId),
        answers,
        times: finalTimes,
        timeTotal: total,
      })
      navigate(`/results/${res.result_id}`, { state: { scoreData: res, quizId } })
    } catch (e: any) {
      setError(e?.message ?? "Failed to submit quiz.")
    }
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-3xl px-4">
        <Card className="mt-4 p-6">
          <Skeleton className="h-6 w-1/3" />
          <Skeleton className="mt-3 h-2 w-full" />
          <div className="mt-6 space-y-3">
            {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}
          </div>
        </Card>
      </div>
    )
  }
  if (error) {
    return (
      <div className="mx-auto max-w-3xl px-4">
        <div className="rounded-md border p-4">
          <p className="font-medium text-destructive">Error</p>
          <p className="text-muted-foreground">{error}</p>
        </div>
      </div>
    )
  }
  if (!questions.length) {
    return (
      <div className="mx-auto max-w-3xl px-4">
        <div className="rounded-md border p-8 text-center">
          <h3 className="text-lg font-semibold">No questions found</h3>
          <p className="text-muted-foreground">This quiz doesn’t have questions yet.</p>
        </div>
      </div>
    )
  }

  const q = questions[current]
  const options = ["option_a", "option_b", "option_c", "option_d"] as const

  return (
    <div className="mx-auto max-w-3xl px-4">
      {/* Sticky top progress (below main nav) */}
      <div className="sticky top-14 z-40 -mx-4 border-b bg-background/80 px-4 py-3 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex items-center justify-between gap-3">
          <div className="min-w-0">
            <p className="truncate text-sm font-medium">Question {current + 1} of {questions.length}</p>
          </div>
          <div className="w-40">
            <Progress value={progress} />
          </div>
          <div className="flex gap-2">
            <Dialog.Root open={reviewOpen} onOpenChange={setReviewOpen}>
              <Dialog.Trigger asChild>
                <Button variant="outline" size="sm"><ListChecks className="mr-2 h-4 w-4" /> Review</Button>
              </Dialog.Trigger>
              <Dialog.Portal>
                <Dialog.Overlay className="fixed inset-0 z-50 bg-black/30 data-[state=open]:animate-in data-[state=closed]:animate-out" />
                <Dialog.Content className="fixed right-0 top-0 z-50 h-full w-full max-w-sm border-l bg-background p-4 shadow-lg data-[state=open]:animate-in data-[state=closed]:animate-out">
                  <div className="mb-3 flex items-center justify-between">
                    <Dialog.Title className="text-sm font-medium">Review answers</Dialog.Title>
                    <Dialog.Close asChild>
                      <Button size="icon" variant="outline" aria-label="Close"><X className="h-4 w-4" /></Button>
                    </Dialog.Close>
                  </div>
                  <div className="grid grid-cols-6 gap-2">
                    {questions.map((qq, idx) => {
                      const answered = answers[qq.id] !== undefined
                      const isCurrent = idx === current
                      return (
                        <button
                          key={qq.id}
                          onClick={() => { setCurrent(idx); setReviewOpen(false) }}
                          className={[
                            "flex h-10 items-center justify-center rounded-md border text-sm",
                            answered ? "bg-primary text-primary-foreground border-transparent" : "hover:bg-accent",
                            isCurrent ? "ring-2 ring-ring" : "",
                          ].join(" ")}
                        >
                          {idx + 1}
                        </button>
                      )
                    })}
                  </div>
                </Dialog.Content>
              </Dialog.Portal>
            </Dialog.Root>
            <Button
              size="sm"
              variant="default"
              onClick={() => setConfirmOpen(true)}
              disabled={Object.keys(answers).length !== questions.length}
            >
              <Check className="mr-2 h-4 w-4" /> Submit
            </Button>
          </div>
        </div>
      </div>

      <Card className="mt-4">
        <CardHeader>
          <CardTitle className="text-lg">Question</CardTitle>
        </CardHeader>
        <CardContent className="space-y-5">
          <div>
            <h3 className="text-base font-medium">{q.question_text}</h3>
            <RadioGroup
              className="mt-4"
              value={answers[q.id]?.toString() ?? ""}
              onValueChange={(v) => onSelect(q.id, Number(v))}
            >
              {options.map((key, idx) => {
                const text = (q as any)[key] as string | undefined
                if (!text) return null
                return (
                  <RadioCard key={key} value={String(idx)}>
                    <span className="inline-flex h-6 w-6 items-center justify-center rounded-full border bg-background text-sm font-semibold">
                      {String.fromCharCode(65 + idx)}
                    </span>
                    <span>{text}</span>
                  </RadioCard>
                )
              })}
            </RadioGroup>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="text-sm text-muted-foreground">
              Answered: {Object.keys(answers).length} / {questions.length}
            </div>
            <div className="flex gap-2">
              {current > 0 && <Button variant="secondary" onClick={prev}>Previous</Button>}
              {current < questions.length - 1 ? (
                <Button onClick={next}>Next</Button>
              ) : (
                <Button onClick={() => setConfirmOpen(true)} disabled={Object.keys(answers).length !== questions.length}>
                  Submit quiz
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Submit confirmation */}
      <Dialog.Root open={confirmOpen} onOpenChange={setConfirmOpen}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 z-50 bg-black/50 data-[state=open]:animate-in data-[state=closed]:animate-out" />
          <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-[90vw] max-w-md -translate-x-1/2 -translate-y-1/2 rounded-lg border bg-background p-6 shadow-lg data-[state=open]:animate-in data-[state=closed]:animate-out">
            <div className="mb-2 flex items-center justify-between">
              <Dialog.Title className="text-lg font-semibold">Submit quiz?</Dialog.Title>
              <Dialog.Close asChild>
                <Button size="icon" variant="outline" aria-label="Close"><X className="h-4 w-4" /></Button>
              </Dialog.Close>
            </div>
            <p className="text-sm text-muted-foreground">You won’t be able to change answers after submitting.</p>
            <div className="mt-5 flex justify-end gap-2">
              <Dialog.Close asChild><Button variant="outline">Cancel</Button></Dialog.Close>
              <Button onClick={() => { setConfirmOpen(false); submit() }}>Submit</Button>
            </div>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </div>
  )
}