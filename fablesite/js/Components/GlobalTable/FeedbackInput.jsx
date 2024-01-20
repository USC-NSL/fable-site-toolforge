import React from 'react';

export default function FeedbackInput({row, setState}) {
    return (
        <textarea 
            rows="3"
            className="py-3 mt-5 mb-5 px-3 border"
            value={row.original.feedbackInput}
            onChange={(e) => {
                e.preventDefault();
                setState(row.index, e.target.value)
            }}
        />
    )
}