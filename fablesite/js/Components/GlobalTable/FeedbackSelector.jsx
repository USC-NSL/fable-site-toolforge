import React from 'react';

export default function FeedbackSelector({row, setState}) {
    return (
        <select
            className="form-select block pl-3 pr-3 py-2 text-base leading-6 border-gray-300 focus:outline-none focus:shadow-outline-blue focus:border-blue-300 sm:text-sm sm:leading-5"
            value={row.original.feedbackSelection}
            onChange={(e) => {
                e.preventDefault();
                setState(row.index, e.target.value)
            }}
        >
            <option>Correct</option>
            <option>Incorrect</option>
            <option>Unsure</option>
        </select>
    )
}