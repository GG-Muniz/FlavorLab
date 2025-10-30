/**
 * Journal API service for daily notes functionality.
 */

const API_BASE_URL = '/api/v1';

/**
 * Get journal entry for a specific date.
 * @param {string} date - Date in YYYY-MM-DD format
 * @returns {Promise<Object|null>} Journal entry or null if not found
 */
export async function getJournalNote(date) {
  try {
    const response = await fetch(`${API_BASE_URL}/journal/${date}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    if (response.status === 404) {
      return null; // No journal entry for this date
    }

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching journal note:', error);
    throw error;
  }
}

/**
 * Create or update a journal entry for a specific date.
 * @param {string} date - Date in YYYY-MM-DD format
 * @param {string} noteText - Journal note content
 * @returns {Promise<Object>} Created/updated journal entry
 */
export async function saveJournalNote(date, noteText) {
  try {
    const response = await fetch(`${API_BASE_URL}/journal/${date}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        note_text: noteText
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error saving journal note:', error);
    throw error;
  }
}

/**
 * Delete a journal entry for a specific date.
 * @param {string} date - Date in YYYY-MM-DD format
 * @returns {Promise<void>}
 */
export async function deleteJournalNote(date) {
  try {
    const response = await fetch(`${API_BASE_URL}/journal/${date}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    if (response.status === 404) {
      return; // Entry doesn't exist, consider it deleted
    }

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
  } catch (error) {
    console.error('Error deleting journal note:', error);
    throw error;
  }
}
