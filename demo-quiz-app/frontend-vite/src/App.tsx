import { BrowserRouter, Routes, Route } from "react-router-dom"
import Navigation from "@/components/ui/Navigation"
import Footer from "@/components/ui/Footer"
import HomePage from "@/pages/HomePage"
import QuizList from "@/pages/QuizList"
import Quiz from "@/pages/Quiz"
import ResultsPage from "@/pages/ResultsPage"
import UserResults from "@/pages/UserResults"
import Login from "@/pages/Login"
import Register from "@/pages/Register"

function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen flex-col">
        <Navigation />
        <main className="flex-1 py-6">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/quizzes" element={<QuizList />} />
            <Route path="/quiz/:quizId" element={<Quiz />} />
            <Route path="/results/:resultId" element={<ResultsPage />} />
            <Route path="/my-results" element={<UserResults />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  )
}
export default App