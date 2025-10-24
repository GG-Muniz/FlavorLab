import React, { createContext, useState, useEffect, useCallback, useContext } from 'react';
import { getMeals, deleteLoggedMeal, updateLoggedMeal, logManualCalories, fetchMealsForDate, fetchNutritionSummaryForDate } from '../services/mealsApi';

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
        }).then(res => res.json()),
        getMeals('generated') // Get meal plans
      ]);
      setLoggedMeals(summaryResponse.logged_meals_today);
      setMealPlans(plansResponse);
      setSummary(summaryResponse); // Store full summary
    } catch (error) {
      console.error("Failed to fetch data", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // --- COMPLETE CRUD FUNCTIONS ---

  const addLog = async (mealName, calories) => {
    try {
      await logManualCalories(mealName, calories);
      await fetchData(); // Re-sync
    } catch (error) {
      console.error("Error logging meal:", error);
    }
  };

  const updateLog = async (logId, mealType, calories) => {
    try {
      await updateLoggedMeal(logId, mealType, calories);
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

  const value = {
    loggedMeals,
    mealPlans,
    summary,
    isLoading,
    addLog,
    updateLog,
    deleteLog,
    logMeal,
    getMealsForDate,
    getNutritionSummaryForDate,
  };

  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  );
};
