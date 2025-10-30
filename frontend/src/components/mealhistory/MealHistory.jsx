/**
 * MealHistory Component
 *
 * Displays logged meals (source=LOGGED) from the database.
 * Shows meals that the user has consumed, grouped by date.
 *
 * Features:
 * - Fetches logged meals (source=LOGGED) from the API
 * - Groups meals by date
 * - Displays meal cards with nutrition information
 * - Handles loading and error states
 * - Empty state when no meals have been logged
 */

import { useState, useEffect } from 'react';
import { getMeals } from '../../services/mealsApi';
import { motion } from 'framer-motion';
import { History, RefreshCw, AlertCircle, Calendar, Flame } from 'lucide-react';

const MealHistory = () => {
  // ============================================================================
  // State Management
  // ============================================================================

  const [loggedMeals, setLoggedMeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ============================================================================
  // Data Fetching Logic
  // ============================================================================

  const loadLoggedMeals = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch meals with source=logged filter
      const meals = await getMeals('logged');

      setLoggedMeals(meals);
    } catch (err) {
      setError(err.message);
      console.error('Error loading logged meals:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLoggedMeals();
  }, []);

  // ============================================================================
  // Helper Functions
  // ============================================================================

  /**
   * Group meals by date
   */
  const groupMealsByDate = (meals) => {
    const grouped = {};

    meals.forEach((meal) => {
      // Ensure we have a valid date
      if (!meal.date_logged) return;

      // Normalize the date to YYYY-MM-DD format
      const date = meal.date_logged.split('T')[0]; // Remove time part if present

      if (!grouped[date]) {
        grouped[date] = [];
      }
      grouped[date].push(meal);
    });

    // Sort dates in descending order (most recent first)
    return Object.keys(grouped)
      .sort((a, b) => new Date(b) - new Date(a))
      .map((date) => ({
        date,
        meals: grouped[date],
      }));
  };

  /**
   * Format date for display
   */
  const formatDate = (dateString) => {
    // Parse date as local date (not UTC) to avoid timezone issues
    const [year, month, day] = dateString.split('-').map(Number);
    const date = new Date(year, month - 1, day); // month is 0-indexed

    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    // Reset hours to compare only dates
    today.setHours(0, 0, 0, 0);
    yesterday.setHours(0, 0, 0, 0);
    date.setHours(0, 0, 0, 0);

    // Check if it's today
    if (date.getTime() === today.getTime()) {
      return 'Today';
    }

    // Check if it's yesterday
    if (date.getTime() === yesterday.getTime()) {
      return 'Yesterday';
    }

    // Otherwise format as "Mon, Jan 15, 2024"
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  /**
   * Get color scheme based on meal type
   */
  const getMealTypeColor = (type) => {
    const colorMap = {
      breakfast: { bg: '#fef3c7', text: '#d97706', border: '#fde68a' },
      morning_snack: { bg: '#fce7f3', text: '#db2777', border: '#fbcfe8' },
      lunch: { bg: '#dbeafe', text: '#0284c7', border: '#bfdbfe' },
      afternoon_snack: { bg: '#e0e7ff', text: '#6366f1', border: '#c7d2fe' },
      dinner: { bg: '#f3e8ff', text: '#9333ea', border: '#e9d5ff' },
      snack: { bg: '#fce7f3', text: '#db2777', border: '#fbcfe8' },
    };
    return colorMap[type] || colorMap.breakfast;
  };

  /**
   * Format meal type for display
   */
  const formatMealType = (type) => {
    if (!type) return 'Meal';
    return type
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  // ============================================================================
  // Conditional Rendering - Loading State
  // ============================================================================

  if (loading) {
    return (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '400px',
          gap: '20px',
        }}
      >
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
          style={{
            width: 64,
            height: 64,
            background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <History width={32} height={32} color="#ffffff" />
        </motion.div>

        <div style={{ textAlign: 'center' }}>
          <h3
            style={{
              fontSize: '20px',
              fontWeight: '600',
              color: '#374151',
              marginBottom: '8px',
            }}
          >
            Loading Meal History
          </h3>
          <p
            style={{
              fontSize: '14px',
              color: '#6b7280',
            }}
          >
            Fetching your logged meals...
          </p>
        </div>
      </div>
    );
  }

  // ============================================================================
  // Conditional Rendering - Error State
  // ============================================================================

  if (error && loggedMeals.length === 0) {
    return (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '400px',
          gap: '24px',
          padding: '32px',
        }}
      >
        <div
          style={{
            width: 64,
            height: 64,
            background: '#fef2f2',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <AlertCircle width={32} height={32} color="#ef4444" />
        </div>

        <div style={{ textAlign: 'center', maxWidth: '500px' }}>
          <h3
            style={{
              fontSize: '20px',
              fontWeight: '600',
              color: '#374151',
              marginBottom: '12px',
            }}
          >
            Unable to Load Meal History
          </h3>
          <p
            style={{
              fontSize: '14px',
              color: '#6b7280',
              lineHeight: '1.6',
              marginBottom: '24px',
            }}
          >
            {error}
          </p>

          <button
            onClick={loadLoggedMeals}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 24px',
              background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
              color: '#ffffff',
              border: 'none',
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              boxShadow: '0 4px 6px -1px rgba(34, 197, 94, 0.3)',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 10px 15px -3px rgba(34, 197, 94, 0.4)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(34, 197, 94, 0.3)';
            }}
          >
            <RefreshCw width={16} height={16} />
            <span>Try Again</span>
          </button>
        </div>
      </div>
    );
  }

  // ============================================================================
  // Conditional Rendering - Empty State
  // ============================================================================

  if (loggedMeals.length === 0) {
    return (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '400px',
          gap: '24px',
          padding: '32px',
        }}
      >
        <div
          style={{
            width: 80,
            height: 80,
            background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <History width={40} height={40} color="#16a34a" />
        </div>

        <div style={{ textAlign: 'center', maxWidth: '500px' }}>
          <h3
            style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#111827',
              marginBottom: '12px',
            }}
          >
            No Meals Logged Yet
          </h3>
          <p
            style={{
              fontSize: '16px',
              color: '#6b7280',
              lineHeight: '1.6',
            }}
          >
            Start logging meals from your Meal Plans to track your nutrition history. Go to the Meal Plans tab and click "Log Meal for Today" on any meal template.
          </p>
        </div>
      </div>
    );
  }

  // ============================================================================
  // Main Content - Meal History Display
  // ============================================================================

  const groupedMeals = groupMealsByDate(loggedMeals);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      style={{
        maxWidth: '1200px',
        margin: '0 auto',
      }}
    >
      {/* Header Section */}
      <div
        style={{
          marginBottom: '32px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '16px',
        }}
      >
        <div>
          <h2
            style={{
              fontSize: '32px',
              fontWeight: '700',
              color: '#111827',
              marginBottom: '8px',
            }}
          >
            Meal History
          </h2>
          <p
            style={{
              fontSize: '16px',
              color: '#6b7280',
            }}
          >
            {loggedMeals.length} logged meal{loggedMeals.length !== 1 ? 's' : ''}
          </p>
        </div>

        {/* Refresh Button */}
        <button
          onClick={loadLoggedMeals}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 20px',
            background: '#ffffff',
            color: '#374151',
            border: '2px solid #e5e7eb',
            borderRadius: '12px',
            fontSize: '14px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'all 0.2s',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = '#22c55e';
            e.currentTarget.style.color = '#22c55e';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = '#e5e7eb';
            e.currentTarget.style.color = '#374151';
          }}
        >
          <RefreshCw width={16} height={16} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Meal History Timeline */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
        {groupedMeals.map(({ date, meals }, groupIdx) => (
          <motion.div
            key={date}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: groupIdx * 0.1 }}
          >
            {/* Date Header */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                marginBottom: '16px',
                paddingBottom: '12px',
                borderBottom: '2px solid #e5e7eb',
              }}
            >
              <Calendar width={20} height={20} color="#6b7280" />
              <h3
                style={{
                  fontSize: '18px',
                  fontWeight: '600',
                  color: '#374151',
                  margin: 0,
                }}
              >
                {formatDate(date)}
              </h3>
              <span
                style={{
                  fontSize: '14px',
                  color: '#9ca3af',
                  marginLeft: 'auto',
                }}
              >
                {meals.length} meal{meals.length !== 1 ? 's' : ''}
              </span>
            </div>

            {/* Meals Grid */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                gap: '16px',
              }}
            >
              {meals.map((meal, mealIdx) => {
                const colors = getMealTypeColor(meal.meal_type);

                return (
                  <motion.div
                    key={meal.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3, delay: mealIdx * 0.05 }}
                    style={{
                      background: colors.bg,
                      border: `1px solid ${colors.border}`,
                      borderRadius: '12px',
                      padding: '16px',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '12px',
                    }}
                  >
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: '8px',
                      }}
                    >
                      <h4
                        style={{
                          fontSize: '18px',
                          fontWeight: '600',
                          color: colors.text,
                          margin: 0,
                        }}
                      >
                        {formatMealType(meal.meal_type)}
                      </h4>
                      <Flame width={20} height={20} color={colors.text} />
                    </div>

                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: '8px',
                      }}
                    >
                      <p
                        style={{
                          fontSize: '14px',
                          color: '#4b5563',
                          margin: 0,
                        }}
                      >
                        {meal.meal_name}
                      </p>
                      <span
                        style={{
                          fontSize: '14px',
                          fontWeight: '600',
                          color: colors.text,
                        }}
                      >
                        {meal.calories} kcal
                      </span>
                    </div>

                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: '8px',
                      }}
                    >
                      <p
                        style={{
                          fontSize: '14px',
                          color: '#4b5563',
                          margin: 0,
                        }}
                      >
                        Protein: {meal.protein}g
                      </p>
                      <p
                        style={{
                          fontSize: '14px',
                          color: '#4b5563',
                          margin: 0,
                        }}
                      >
                        Carbs: {meal.carbs}g
                      </p>
                      <p
                        style={{
                          fontSize: '14px',
                          color: '#4b5563',
                          margin: 0,
                        }}
                      >
                        Fat: {meal.fat}g
                      </p>
                    </div>

                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginTop: 'auto',
                      }}
                    >
                      <p
                        style={{
                          fontSize: '14px',
                          color: '#6b7280',
                          margin: 0,
                        }}
                      >
                        {meal.date_logged}
                      </p>
                      <button
                        onClick={() => loadLoggedMeals()}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px',
                          padding: '6px 12px',
                          background: '#ffffff',
                          color: '#374151',
                          border: '1px solid #e5e7eb',
                          borderRadius: '8px',
                          fontSize: '12px',
                          fontWeight: '600',
                          cursor: 'pointer',
                          transition: 'all 0.2s',
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.borderColor = '#22c55e';
                          e.currentTarget.style.color = '#22c55e';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.borderColor = '#e5e7eb';
                          e.currentTarget.style.color = '#374151';
                        }}
                      >
                        <RefreshCw width={12} height={12} />
                        <span>Log Again</span>
                      </button>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

export default MealHistory;
