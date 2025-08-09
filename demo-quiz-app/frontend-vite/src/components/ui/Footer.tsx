import { Github, Mail, Twitter, Linkedin } from "lucide-react"

export default function Footer() {
  return (
    <footer className="mt-14 border-t bg-background">
      <div className="h-1 w-full bg-gradient-to-r from-cyan-500 via-blue-600 to-cyan-500" />
      <div className="mx-auto max-w-6xl px-4 py-8">
        <div className="grid gap-8 md:grid-cols-4">
          <div>
            <h3 className="bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-lg font-bold text-transparent">
              QuizMaster
            </h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Challenge yourself with interactive quizzes and track your progress.
            </p>
          </div>

          <div>
            <h4 className="text-sm font-semibold">Explore</h4>
            <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
              <li><a className="hover:text-foreground" href="/quizzes">Browse Quizzes</a></li>
              <li><a className="hover:text-foreground" href="/my-results">My Results</a></li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold">Resources</h4>
            <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
              <li><a className="hover:text-foreground" href="#">Privacy</a></li>
              <li><a className="hover:text-foreground" href="#">Terms</a></li>
              <li><a className="hover:text-foreground" href="#">Contact</a></li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold">Connect</h4>
            <div className="mt-3 flex gap-3">
              <a className="rounded-full border p-2 text-muted-foreground transition-colors hover:border-cyan-500 hover:text-cyan-600" href="#"><Mail className="h-4 w-4" /></a>
              <a className="rounded-full border p-2 text-muted-foreground transition-colors hover:border-cyan-500 hover:text-cyan-600" href="#"><Twitter className="h-4 w-4" /></a>
              <a className="rounded-full border p-2 text-muted-foreground transition-colors hover:border-cyan-500 hover:text-cyan-600" href="#"><Github className="h-4 w-4" /></a>
              <a className="rounded-full border p-2 text-muted-foreground transition-colors hover:border-cyan-500 hover:text-cyan-600" href="#"><Linkedin className="h-4 w-4" /></a>
            </div>
          </div>
        </div>

        <div className="mt-8 flex flex-wrap items-center justify-between gap-2 border-t pt-6 text-xs text-muted-foreground">
          <p>© {new Date().getFullYear()} QuizMaster</p>
          <p>Built with React & Flask</p>
        </div>
      </div>
    </footer>
  )
}