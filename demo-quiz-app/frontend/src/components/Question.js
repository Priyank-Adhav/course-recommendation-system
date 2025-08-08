import React from "react";

export default function Question({ question, selectedAnswer, onAnswerChange }) {
  const optionKeys = ["option_a", "option_b", "option_c", "option_d"];

  return (
    <div className="question-card">
      <h3>{question.question_text}</h3>
      {optionKeys.map((optKey, idx) => {
        const optionValue = question[optKey];
        if (!optionValue) return null;

        const inputId = `q-${question.id}-opt-${idx + 1}`;
        return (
          <div key={optKey}>
            <input
              id={inputId}
              type="radio"
              name={`question-${question.id}`}
              value={idx + 1}
              checked={selectedAnswer === idx + 1}
              onChange={(e) => onAnswerChange(question.id, Number(e.target.value))}
            />
            <label htmlFor={inputId}>{optionValue}</label>
          </div>
        );
      })}
    </div>
  );
}
