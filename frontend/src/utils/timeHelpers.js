/**
 * Time formatting utilities for displaying relative timestamps
 */

/**
 * Convert a timestamp to a human-readable "time ago" format
 * @param {string|Date} timestamp - The timestamp to convert
 * @returns {string} Formatted time ago string (e.g., "2h ago", "Just now")
 */
export const getTimeAgo = (timestamp) => {
  if (!timestamp) return '';

  const now = new Date();
  const past = new Date(timestamp);
  const diffMs = now - past;
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;

  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;

  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
};

