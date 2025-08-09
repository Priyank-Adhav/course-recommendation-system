import * as React from "react"
import * as ToggleGroupPrimitive from "@radix-ui/react-toggle-group"
import { cn } from "@/lib/utils"

export function ToggleGroup({
  className,
  ...props
}: React.ComponentPropsWithoutRef<typeof ToggleGroupPrimitive.Root>) {
  return <ToggleGroupPrimitive.Root className={cn("inline-flex gap-2", className)} {...props} />
}

export function ToggleGroupItem({
  className,
  ...props
}: React.ComponentPropsWithoutRef<typeof ToggleGroupPrimitive.Item>) {
  return (
    <ToggleGroupPrimitive.Item
      className={cn(
        "inline-flex items-center justify-center rounded-md border px-3 py-1.5 text-sm font-medium",
        "bg-background hover:bg-accent hover:text-accent-foreground",
        "data-[state=on]:bg-primary data-[state=on]:text-primary-foreground data-[state=on]:border-transparent",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        className
      )}
      {...props}
    />
  )
}