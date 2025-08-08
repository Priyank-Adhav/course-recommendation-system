// src/pages/HomePage.js
import React, { useEffect, useState } from "react";
import { fetchQuizzes } from "../services/api";
import { Link } from "react-router-dom";

export default function HomePage() {
    const [quizzes, setQuizzes] = useState([]);

    useEffect(() => {
        fetchQuizzes().then(setQuizzes);
    }, []);

    return (
        <div className="home-page">
            <h1>Available Quizzes</h1>
            {quizzes.length === 0 && <p>Loading quizzes...</p>}
            <ul>
                {quizzes.map((quiz) => (
                    <li key={quiz.id}>
                        <Link to={`/quiz/${quiz.id}`}>{quiz.title}</Link>
                    </li>
                ))}
            </ul>
        </div>
    );
}
