import React from 'react';

/**
 * ProgressBar Component
 *
 * A reusable progress bar component for displaying macro progress.
 *
 * @param {Object} props
 * @param {number} props.consumed - Amount consumed
 * @param {number} props.goal - Goal amount
 * @param {string} props.color - Color for the progress bar
 */
const ProgressBar = ({ consumed, goal, color }) => {
  const percentage = goal > 0 ? Math.min((consumed / goal) * 100, 100) : 0;

  return (
    <div className="progress-bar-container">
      <div
        className="progress-bar-fill"
        style={{
          width: `${percentage}%`,
          backgroundColor: color,
        }}
      />
    </div>
  );
};

export default ProgressBar;
