// src/pages/ResultsPage.js
import React from "react";
import { useLocation, Link } from "react-router-dom";

export default function ResultsPage() {
    const { state } = useLocation();
    const { score, total } = state?.scoreData || {};

    return (
        <div>
            <h1>Results</h1>
            <p>Your Score: {score} / {total}</p>
            <Link to="/">Go Home</Link>
        </div>
    );
}
