import type { ReactNode } from "react"
import { Link } from "react-router-dom"
import { CheckCircle2, Sparkles } from "lucide-react"

export default function AuthShell({
  title, subtitle, children,
}: { title: string; subtitle?: string; children: ReactNode }) {
  return (
    <div className="mx-auto grid min-h-[calc(100vh-56px-56px)] w-full max-w-6xl grid-cols-1 px-4 md:grid-cols-2 md:gap-8">
      <section className="mx-auto flex w-full max-w-md flex-col justify-center py-8">
        <div className="mb-6">
          <Link to="/" className="text-lg font-semibold">
            <span className="bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent">QuizMaster</span>
          </Link>
        </div>
        <h1 className="text-2xl font-bold">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-muted-foreground">{subtitle}</p>}
        <div className="mt-6">{children}</div>
      </section>

      <aside className="relative hidden items-center justify-center overflow-hidden rounded-xl border md:flex">
        <Aurora />
        <div className="relative z-10 max-w-sm p-8 text-white">
          <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-xs">
            <Sparkles className="h-3.5 w-3.5" /> Modern UI + Dark Mode
          </div>
          <h2 className="text-2xl font-semibold">Learn with beautiful, fast quizzes</h2>
          <p className="mt-2 text-white/80">
            Clean design, keyboard-friendly controls, and instant feedback.
          </p>
          <ul className="mt-4 space-y-2 text-sm">
            {["Search & filter quizzes", "Sticky progress & review", "Detailed results"].map((t) => (
              <li key={t} className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-white/90" /> {t}
              </li>
            ))}
          </ul>
        </div>
      </aside>
    </div>
  )
}

function Aurora() {
  return (
    <div aria-hidden className="absolute inset-0 -z-10">
      <div className="absolute inset-0 bg-gradient-to-br from-cyan-600 to-blue-700" />
      <div className="absolute -top-20 -left-20 h-72 w-72 rounded-full bg-cyan-400/40 blur-3xl" />
      <div className="absolute -bottom-24 -right-20 h-72 w-72 rounded-full bg-blue-500/40 blur-3xl" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(255,255,255,0.08),transparent_50%)]" />
    </div>
  )
}