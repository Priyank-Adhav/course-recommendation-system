import { useEffect, useState } from "react"
import { NavLink, Link, useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Menu, X, Sun, Moon, LogOut } from "lucide-react"
import { getUser, logout } from "@/services/auth"

const links = [
  { to: "/", label: "Home" },
  { to: "/quizzes", label: "Quizzes" },
  { to: "/my-results", label: "My Results" },
]

export default function Navigation() {
  const [open, setOpen] = useState(false)
  const [dark, setDark] = useState(false)
  const [user, setUser] = useState(getUser())
  const nav = useNavigate()

  useEffect(() => {
    setDark(document.documentElement.classList.contains("dark"))
    const i = setInterval(() => setUser(getUser()), 500) // simple sync; replace with store later
    return () => clearInterval(i)
  }, [])

  const toggleTheme = () => {
    const html = document.documentElement
    html.classList.toggle("dark")
    setDark(html.classList.contains("dark"))
  }

  const doLogout = () => {
    logout()
    setUser(null)
    nav("/")
  }

  return (
    <header className="sticky top-0 z-50 border-b bg-background/70 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <nav className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
        <NavLink to="/" className="group inline-flex items-center gap-2 text-lg font-semibold">
          <span className="bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent">QuizMaster</span>
          <span className="h-2 w-2 rounded-full bg-cyan-500 transition-transform group-hover:scale-125" />
        </NavLink>

        <div className="hidden items-center gap-5 md:flex">
          {links.map((l) => (
            <NavLink key={l.to} to={l.to}
              className={({ isActive }) => isActive ? "text-primary underline underline-offset-4" : "text-foreground/80 hover:text-foreground"}>
              {l.label}
            </NavLink>
          ))}
          <Button variant="outline" size="icon" aria-label="Toggle theme" onClick={toggleTheme}>
            {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>
          {user ? (
            <div className="flex items-center gap-3">
              <span className="text-sm text-muted-foreground">Hi, {user.name.split(" ")[0]}</span>
              <Button variant="outline" size="sm" onClick={doLogout}><LogOut className="mr-2 h-4 w-4" /> Logout</Button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link to="/login"><Button variant="outline" size="sm">Sign in</Button></Link>
              <Link to="/register"><Button size="sm">Register</Button></Link>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2 md:hidden">
          <Button variant="outline" size="icon" aria-label="Toggle theme" onClick={toggleTheme}>
            {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>
          <Button variant="outline" size="icon" aria-label="Menu" onClick={() => setOpen(o => !o)}>
            {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>
      </nav>

      {open && (
        <div className="md:hidden">
          <div className="border-b bg-background p-4">
            <div className="flex flex-col gap-2">
              {links.map((l) => (
                <NavLink key={l.to} to={l.to} onClick={() => setOpen(false)}
                  className={({ isActive }) => `rounded-md px-3 py-2 text-sm ${isActive ? "bg-primary text-primary-foreground" : "hover:bg-accent"}`}>
                  {l.label}
                </NavLink>
              ))}
              {user ? (
                <button onClick={() => { setOpen(false); doLogout() }} className="rounded-md px-3 py-2 text-left text-sm hover:bg-accent">
                  Logout
                </button>
              ) : (
                <>
                  <Link to="/login" onClick={() => setOpen(false)} className="rounded-md px-3 py-2 text-sm hover:bg-accent">Sign in</Link>
                  <Link to="/register" onClick={() => setOpen(false)} className="rounded-md px-3 py-2 text-sm hover:bg-accent">Register</Link>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  )
}