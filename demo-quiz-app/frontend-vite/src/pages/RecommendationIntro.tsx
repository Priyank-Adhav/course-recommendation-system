import { Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Sparkles, Search } from "lucide-react"

export default function RecommendationIntro() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-20 text-center">
      <Sparkles className="h-12 w-12 text-cyan-500 mx-auto mb-4" />
      <h1 className="text-4xl font-bold mb-3">Smart Course Recommendations</h1>
      <p className="text-muted-foreground max-w-2xl mx-auto mb-8">
        Our AI engine curates course suggestions that align with your interests, skill level,
        and learning goals. Get personalized learning paths instantly.
      </p>
      <Link to="/recommendations">
        <Button size="lg" className="bg-cyan-600 hover:bg-cyan-700">
          <Search className="mr-2 h-5 w-5" /> Explore Recommendations
        </Button>
      </Link>
    </div>
  )
}
