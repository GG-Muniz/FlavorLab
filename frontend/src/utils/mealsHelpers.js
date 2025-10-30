/**
 * Meal-related utility functions
 */

/**
 * Parse the meals_per_day profile value to a numeric daily meal goal
 * @param {string} mealsPerDayValue - The value from user.dietary_preferences.meals_per_day
 * @returns {number} The numeric daily meal goal (defaults to 5)
 */
export const parseMealsPerDay = (mealsPerDayValue) => {
  if (!mealsPerDayValue) return 5; // Default to 5 meals

  const map = {
    '3-meals': 3,
    '3-meals-2-snacks': 5, // 3 meals + 2 snacks = 5 total
    '5-6-smaller': 5, // Use 5 as the target for 5-6 smaller meals
  };

  return map[mealsPerDayValue] || 5; // Default to 5 if unknown value
};

