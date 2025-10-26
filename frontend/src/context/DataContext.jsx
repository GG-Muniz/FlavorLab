import React, { createContext, useState, useEffect, useCallback, useContext } from 'react';
import { getMeals, deleteLoggedMeal, updateLoggedMeal, logManualCalories, fetchMealsForDate, fetchNutritionSummaryForDate, setCalorieGoal } from '../services/mealsApi';
import { getJournalNote, saveJournalNote, deleteJournalNote } from '../services/journalApi';

const DataContext = createContext();

export const useData = () => {
  return useContext(DataContext);
};

export const DataProvider = ({ children }) => {
  const [loggedMeals, setLoggedMeals] = useState([]);
  const [mealPlans, setMealPlans] = useState([]);
  const [summary, setSummary] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchData = useCallback(async () => {
    // We don't set loading to true here to avoid UI flashes on re-fetch
    try {
      const [summaryResponse, plansResponse] = await Promise.all([
        fetch('/api/v1/users/me/daily-summary', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        }).then(res => {
          if (!res.ok) {
            throw new Error(`HTTP ${res.status}: ${res.statusText}`);
          }
          return res.json();
        }),
        getMeals('generated') // Get meal plans
      ]);
      setLoggedMeals(summaryResponse.logged_meals_today || []);
      setMealPlans(plansResponse || []);
      setSummary(summaryResponse); // Store full summary
    } catch (error) {
      console.error("Failed to fetch data", error);
      // Set fallback data to prevent infinite loading
      setLoggedMeals([]);
      setMealPlans([]);
      setSummary({
        daily_goal: 2000,
        total_consumed: 0,
        remaining: 2000,
        logged_meals_today: [],
        macros: {
          protein: 0,
          carbs: 0,
          fat: 0,
          fiber: 0
        }
      });
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Get the last logged meal (most recent)
  const getLastLoggedMeal = useCallback(() => {
    if (!loggedMeals || loggedMeals.length === 0) return null;

    // Sort by created_at or logged_at timestamp (most recent first)
    const sorted = [...loggedMeals].sort((a, b) => {
      const dateA = new Date(a.created_at || a.logged_at || 0);
      const dateB = new Date(b.created_at || b.logged_at || 0);
      return dateB - dateA;
    });

    return sorted[0];
  }, [loggedMeals]);

  // --- COMPLETE CRUD FUNCTIONS ---

  const addLog = async (mealName, calories) => {
    try {
      // CRITICAL FIX: Round calories to integer to prevent Pydantic validation errors
      await logManualCalories(mealName, Math.round(calories));
      await fetchData(); // Re-sync
    } catch (error) {
      console.error("Error logging meal:", error);
    }
  };

  const updateLog = async (logId, mealType, calories, macroData = null) => {
    try {
      if (macroData) {
        // Update with macro scaling - extend the API call to include macro data
        // CRITICAL FIX: Round all decimal values to prevent Pydantic validation errors
        const response = await fetch(`/api/v1/meals/${logId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            ...(localStorage.getItem('token') ? { 'Authorization': `Bearer ${localStorage.getItem('token')}` } : {})
          },
          body: JSON.stringify({
            meal_type: mealType,
            calories: Math.round(calories), // Round calories to integer
            protein: parseFloat(macroData.protein.toFixed(1)), // Round to 1 decimal
            carbs: parseFloat(macroData.carbs.toFixed(1)), // Round to 1 decimal
            fat: parseFloat(macroData.fat.toFixed(1)), // Round to 1 decimal
            fiber: parseFloat(macroData.fiber.toFixed(1)) // Round to 1 decimal
          })
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData?.detail || 'Failed to update logged meal with macros');
        }
      } else {
        // Update calories only
        await updateLoggedMeal(logId, mealType, calories);
      }
      await fetchData(); // Re-sync
    } catch (error) {
      console.error("Error updating meal:", error);
    }
  };

  const deleteLog = async (logId) => {
    try {
      await deleteLoggedMeal(logId);
      await fetchData(); // Re-sync
    } catch (error) {
      console.error("Error deleting meal:", error);
    }
  };

  const logMeal = async (mealId) => {
    try {
      const response = await fetch(`/api/v1/meals/${mealId}/log`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(localStorage.getItem('token') ? { 'Authorization': `Bearer ${localStorage.getItem('token')}` } : {})
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData?.detail || 'Failed to log meal plan');
      }

      await fetchData(); // Re-sync
    } catch (error) {
      console.error("Error logging meal:", error);
    }
  };

  // Calendar-specific functions for fetching historical data
  const getMealsForDate = async (date) => {
    try {
      return await fetchMealsForDate(date);
    } catch (error) {
      console.error("Error fetching meals for date:", error);
      return [];
    }
  };

  const getNutritionSummaryForDate = async (date) => {
    try {
      return await fetchNutritionSummaryForDate(date);
    } catch (error) {
      console.error("Error fetching nutrition summary for date:", error);
      return { total_calories: 0, total_protein_g: 0, total_carbs_g: 0, total_fat_g: 0 };
    }
  };

  const setGoal = async (goalCalories) => {
    try {
      await setCalorieGoal(goalCalories);
      await fetchData(); // Re-sync to get updated goal
    } catch (error) {
      console.error("Error setting calorie goal:", error);
      throw error; // Re-throw so component can handle UI error state
    }
  };

  const refetchAll = useCallback(async () => {
    await fetchData();
  }, [fetchData]);

  const value = {
    loggedMeals,
    mealPlans,
    summary,
    isLoading,
    addLog,
    updateLog,
    deleteLog,
    logMeal,
    setGoal,
    getMealsForDate,
    getNutritionSummaryForDate,
    getLastLoggedMeal,
    refetchAll,
    // Journal functions
    getJournalNote,
    saveJournalNote,
    deleteJournalNote,
  };

  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  );
};
