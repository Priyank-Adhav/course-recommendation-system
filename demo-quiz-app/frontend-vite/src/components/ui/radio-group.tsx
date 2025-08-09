import * as React from "react"
import * as RadioGroupPrimitive from "@radix-ui/react-radio-group"
import { cn } from "@/lib/utils"

export const RadioGroup = ({ className, ...props }: React.ComponentPropsWithoutRef<typeof RadioGroupPrimitive.Root>) => {
  return <RadioGroupPrimitive.Root className={cn("grid gap-2", className)} {...props} />
}

export const RadioCard = React.forwardRef<
  React.ElementRef<typeof RadioGroupPrimitive.Item>,
  React.ComponentPropsWithoutRef<typeof RadioGroupPrimitive.Item>
>(({ className, children, ...props }, ref) => {
  return (
    <RadioGroupPrimitive.Item
      ref={ref}
      className={cn(
        "flex items-center gap-3 rounded-md border p-3 text-left transition-colors",
        "hover:bg-accent hover:text-accent-foreground",
        "data-[state=checked]:border-transparent data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        className
      )}
      {...props}
    >
      {children}
    </RadioGroupPrimitive.Item>
  )
})
RadioCard.displayName = "RadioCard"