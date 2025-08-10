import * as React from "react"
import { Eye, EyeOff } from "lucide-react"
import { cn } from "@/lib/utils"

type Strength = { score: number; label: string; color: string }
function calcStrength(v: string): Strength {
  let s = 0
  if (v.length >= 8) s++
  if (/[A-Z]/.test(v)) s++
  if (/[a-z]/.test(v)) s++
  if (/[0-9]/.test(v)) s++
  if (/[^A-Za-z0-9]/.test(v)) s++
  const score = Math.min(4, s)
  const map = [
    { score: 0, label: "Too short", color: "bg-rose-500" },
    { score: 1, label: "Weak",      color: "bg-rose-500" },
    { score: 2, label: "Fair",      color: "bg-amber-500" },
    { score: 3, label: "Good",      color: "bg-cyan-500" },
    { score: 4, label: "Strong",    color: "bg-green-500" },
  ]
  return map[score]
}

export interface PasswordInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  showStrength?: boolean
}

export const PasswordInput = React.forwardRef<HTMLInputElement, PasswordInputProps>(
  ({ className, showStrength, value, onChange, ...props }, ref) => {
    const [visible, setVisible] = React.useState(false)
    const str = calcStrength(String(value ?? ""))

    return (
      <div>
        <div className="relative">
          <input
            ref={ref}
            type={visible ? "text" : "password"}
            className={cn(
              "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 pr-10 text-sm ring-offset-background",
              "placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
              "disabled:cursor-not-allowed disabled:opacity-50",
              className
            )}
            value={value as string}
            onChange={onChange}
            {...props}
          />
          <button
            type="button"
            onClick={() => setVisible((v) => !v)}
            className="absolute inset-y-0 right-2 grid w-8 place-items-center text-muted-foreground hover:text-foreground"
            aria-label={visible ? "Hide password" : "Show password"}
            tabIndex={-1}
          >
            {visible ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>

        {showStrength && String(value ?? "").length > 0 && (
          <div className="mt-2">
            <div className="mb-1 flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Password strength</span>
              <span className="font-medium">{str.label}</span>
            </div>
            <div className="flex gap-1">
              {Array.from({ length: 4 }).map((_, i) => (
                <div
                  key={i}
                  className={cn(
                    "h-1 flex-1 rounded",
                    i < str.score ? str.color : "bg-muted"
                  )}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }
)
PasswordInput.displayName = "PasswordInput"