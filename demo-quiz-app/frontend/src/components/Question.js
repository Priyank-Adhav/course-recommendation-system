import React from "react";

export default function Question({ question, selectedAnswer, onAnswerChange }) {
  const optionKeys = ["option_a", "option_b", "option_c", "option_d"];

  return (
    <div className="question-card">
      <h3>{question.question_text}</h3>
      <div className="options-container">
        {optionKeys.map((optKey, idx) => {
          const optionValue = question[optKey];
          if (!optionValue) return null;

          const inputId = `q-${question.id}-opt-${idx}`;
          return (
            <div key={optKey} className="option-item">
              <input
                id={inputId}
                type="radio"
                name={`question-${question.id}`}
                value={idx} // Changed to use 0-based index to match backend
                checked={selectedAnswer === idx}
                onChange={(e) => onAnswerChange(question.id, Number(e.target.value))}
              />
              <label htmlFor={inputId} className="option-label">
                <span className="option-letter">{String.fromCharCode(65 + idx)}.</span>
                <span className="option-text">{optionValue}</span>
              </label>
            </div>
          );
        })}
      </div>
    </div>
  );
}