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
import { getHealthPillars } from '../../services/healthPillarsApi';
import { useData } from '../../context/DataContext';
import { motion } from 'framer-motion';
import { History, Trash2, AlertCircle, Calendar, Flame, RefreshCw, Leaf, Droplets } from 'lucide-react';

const MealHistory = () => {
  console.log('🔍 [MealHistory] Component rendering...');

  // ============================================================================
  // State Management
  // ============================================================================

  const [loggedMeals, setLoggedMeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pillars, setPillars] = useState([]);

  // Get deleteLog function from DataContext for synchronized deletion
  const dataContext = useData();
  console.log('🔍 [MealHistory] DataContext:', dataContext);
  const { deleteLog, refetchAll } = dataContext || {};

  // ============================================================================
  // Data Fetching Logic
  // ============================================================================

  const loadLoggedMeals = async () => {
    try {
      console.log('🔍 [MealHistory] Loading logged meals...');
      setLoading(true);
      setError(null);

      // Fetch meals with source=logged filter
      const meals = await getMeals('logged');
      console.log('🔍 [MealHistory] Fetched meals:', meals);

      setLoggedMeals(meals);
    } catch (err) {
      console.error('❌ [MealHistory] Error loading logged meals:', err);
      setError(err.message);
    } finally {
      setLoading(false);
      console.log('🔍 [MealHistory] Loading complete. Meals count:', loggedMeals.length);
    }
  };

  useEffect(() => {
    loadLoggedMeals();
  }, []);

  // Fetch health pillars on mount
  useEffect(() => {
    const fetchPillars = async () => {
      try {
        const data = await getHealthPillars();
        setPillars(data);
      } catch (err) {
        console.error('Error loading health pillars:', err);
        // Fail silently - not critical for display
      }
    };

    fetchPillars();
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
    * Get color scheme based on meal type - Updated to light orange theme
    */
   const getMealTypeColor = (type) => {
     // Light orange theme
     const colorMap = {
       breakfast: { bg: 'linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%)', text: '#9a3412', border: '#fed7aa', accent: '#fdba74' },
       morning_snack: { bg: 'linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%)', text: '#c2410c', border: '#fed7aa', accent: '#fdba74' },
       lunch: { bg: 'linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%)', text: '#ea580c', border: '#fed7aa', accent: '#fdba74' },
       afternoon_snack: { bg: 'linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%)', text: '#c2410c', border: '#fed7aa', accent: '#fdba74' },
       dinner: { bg: 'linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%)', text: '#9a3412', border: '#fed7aa', accent: '#fdba74' },
       snack: { bg: 'linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%)', text: '#c2410c', border: '#fed7aa', accent: '#fdba74' },
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

  /**
   * Get emoji for health pillar based on pillar name
   */
  const getPillarEmoji = (pillarName) => {
    const emojiMap = {
      'Increased Energy': '⚡',
      'Improved Digestion': '🌿',
      'Enhanced Immunity': '🛡️',
      'Better Sleep': '😴',
      'Mental Clarity': '🧠',
      'Heart Health': '❤️',
      'Muscle Recovery': '💪',
      'Inflammation Reduction': '🔥'
    };
    return emojiMap[pillarName] || '🎯';
  };

  /**
   * Get color for dietary/constraint tags
   */
  const getTagColor = (tagName) => {
    const lowerTag = tagName.toLowerCase();

    // Dietary restrictions - green theme
    if (lowerTag.includes('gluten-free') || lowerTag.includes('dairy-free') ||
        lowerTag.includes('vegan') || lowerTag.includes('vegetarian')) {
      return { bg: '#d1fae5', text: '#065f46', border: '#a7f3d0' };
    }

    // Keto - purple theme
    if (lowerTag.includes('keto')) {
      return { bg: '#e9d5ff', text: '#7e22ce', border: '#d8b4fe' };
    }

    // Allergy-free tags - red theme
    if (lowerTag.includes('-free')) {
      return { bg: '#fee2e2', text: '#991b1b', border: '#fca5a5' };
    }

    // Default - gray theme
    return { bg: '#f3f4f6', text: '#374151', border: '#e5e7eb' };
  };

  // Get all pillar names for tag filtering
  const allPillarNames = pillars.map(p => p.name);

  /**
   * Handle deleting a logged meal
   * Uses DataContext's deleteLog function to ensure all tabs stay synchronized
   */
  const handleDeleteMeal = async (mealId, mealName) => {
    // Confirm deletion with user
    const confirmDelete = window.confirm(
      `Are you sure you want to delete "${mealName}"? This action cannot be undone.`
    );

    if (!confirmDelete) return;

    try {
      // Delete via DataContext (automatically syncs Dashboard, Journal, etc.)
      if (deleteLog) {
        await deleteLog(mealId);
      } else {
        // Fallback to direct API call if DataContext not available
        const { deleteLoggedMeal } = await import('../../services/mealsApi');
        await deleteLoggedMeal(mealId);
      }

      // Refresh local meal history view
      await loadLoggedMeals();

      console.log(`✅ Successfully deleted meal: ${mealName}`);
    } catch (error) {
      console.error('❌ Failed to delete meal:', error);
      alert(`Failed to delete meal: ${error.message || 'Unknown error'}`);
    }
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
             background: 'linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%)',
             borderRadius: '50%',
             display: 'flex',
             alignItems: 'center',
             justifyContent: 'center',
           }}
         >
           <History width={40} height={40} color="#ea580c" />
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
                color: '#000000',
                marginBottom: '8px',
              }}
            >
              Meal History
            </h2>
                       <p
              style={{
                fontSize: '16px',
                color: '#000000',
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
             color: '#c2410c',
             border: '2px solid #fed7aa',
             borderRadius: '12px',
             fontSize: '14px',
             fontWeight: '600',
             cursor: 'pointer',
             transition: 'all 0.2s',
             boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
           }}
           onMouseEnter={(e) => {
             e.currentTarget.style.borderColor = '#fdba74';
             e.currentTarget.style.background = 'linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%)';
             e.currentTarget.style.transform = 'translateY(-2px)';
             e.currentTarget.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
           }}
           onMouseLeave={(e) => {
             e.currentTarget.style.borderColor = '#fed7aa';
             e.currentTarget.style.background = '#ffffff';
             e.currentTarget.style.transform = 'translateY(0)';
             e.currentTarget.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.05)';
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
                  marginBottom: '20px',
                  padding: '8px 0',
                }}
              >
                <Calendar width={18} height={18} color="#6b7280" />
                <h3
                  style={{
                    fontSize: '16px',
                    fontWeight: '600',
                    color: '#374151',
                    margin: 0,
                  }}
                >
                  {formatDate(date)}
                </h3>
             </div>

            {/* Meals Grid */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                gap: '20px',
              }}
            >
              {meals.map((meal, mealIdx) => {
                const colors = getMealTypeColor(meal.meal_type);

                // Extract tags from nutrition_info
                const tags = meal.nutrition_info?.tags || [];
                const dietaryTags = tags.filter(tag => !allPillarNames.includes(tag));
                const healthGoalTags = tags.filter(tag => allPillarNames.includes(tag));

                return (
                                                                                                                                                       <motion.div
                       key={meal.id}
                       initial={{ opacity: 0, scale: 0.95 }}
                       animate={{ opacity: 1, scale: 1 }}
                       transition={{ duration: 0.3, delay: mealIdx * 0.05 }}
                       style={{
                         background: '#ffffff',
                         border: '1px solid #e5e7eb',
                         borderRadius: '12px',
                         overflow: 'hidden',
                         display: 'flex',
                         flexDirection: 'column',
                         boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
                         transition: 'all 0.3s',
                         minWidth: 0,
                         width: '100%',
                       }}
                     onMouseEnter={(e) => {
                       e.currentTarget.style.transform = 'translateY(-4px)';
                       e.currentTarget.style.boxShadow = '0 8px 16px rgba(0, 0, 0, 0.12)';
                     }}
                     onMouseLeave={(e) => {
                       e.currentTarget.style.transform = 'translateY(0)';
                       e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.08)';
                     }}
                   >
                     {/* Orange Header */}
                     <div
                       style={{
                         background: 'linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%)',
                         borderBottom: '2px solid #fed7aa',
                         padding: '12px 16px',
                         display: 'flex',
                         justifyContent: 'space-between',
                         alignItems: 'center',
                       }}
                     >
                       <span
                         style={{
                           fontSize: '11px',
                           fontWeight: '700',
                           color: '#9a3412',
                           textTransform: 'uppercase',
                           letterSpacing: '0.5px',
                         }}
                       >
                         {formatMealType(meal.meal_type)}
                       </span>
                       <button
                         onClick={() => handleDeleteMeal(meal.id, meal.name)}
                         style={{
                           display: 'inline-flex',
                           alignItems: 'center',
                           gap: '4px',
                           padding: '4px 8px',
                           background: 'transparent',
                           color: '#ef4444',
                           border: 'none',
                           borderRadius: '6px',
                           fontSize: '11px',
                           fontWeight: '600',
                           cursor: 'pointer',
                           transition: 'all 0.2s',
                         }}
                         onMouseEnter={(e) => {
                           e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)';
                         }}
                         onMouseLeave={(e) => {
                           e.currentTarget.style.background = 'transparent';
                         }}
                       >
                         <Trash2 width={12} height={12} />
                       </button>
                     </div>

                                           {/* White Body */}
                      <div
                        style={{
                          padding: '16px',
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '12px',
                          minWidth: 0, // Prevent overflow
                        }}
                      >
                        {/* Meal Name */}
                        <h4
                          style={{
                            fontSize: '18px',
                            fontWeight: '700',
                            color: '#111827',
                            margin: 0,
                            lineHeight: '1.3',
                          }}
                        >
                          {meal.name}
                        </h4>

                        {/* Calories */}
                        <div style={{
                          fontSize: '24px',
                          fontWeight: '700',
                          color: '#ea580c',
                        }}>
                          {meal.calories || 0} <span style={{
                            fontSize: '14px',
                            fontWeight: '600',
                            color: '#9ca3af',
                          }}>kcal</span>
                        </div>

                        {/* Macros - Simple horizontal layout */}
                        <div
                          style={{
                            display: 'flex',
                            flexWrap: 'wrap',
                            gap: '12px',
                            paddingTop: '8px',
                            borderTop: '1px solid #e5e7eb',
                          }}
                        >
                          <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                            minWidth: 0,
                            flexShrink: 0,
                          }}>
                            <Leaf width={14} height={14} color="#ea580c" />
                            <span style={{
                              fontSize: '12px',
                              color: '#6b7280',
                              whiteSpace: 'nowrap',
                            }}>Protein:</span>
                            <span style={{
                              fontSize: '13px',
                              fontWeight: '700',
                              color: '#374151',
                              whiteSpace: 'nowrap',
                            }}>{meal.protein_g || 0}g</span>
                          </div>
                          <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                            minWidth: 0,
                            flexShrink: 0,
                          }}>
                            <Droplets width={14} height={14} color="#ea580c" />
                            <span style={{
                              fontSize: '12px',
                              color: '#6b7280',
                              whiteSpace: 'nowrap',
                            }}>Carbs:</span>
                            <span style={{
                              fontSize: '13px',
                              fontWeight: '700',
                              color: '#374151',
                              whiteSpace: 'nowrap',
                            }}>{meal.carbs_g || 0}g</span>
                          </div>
                          <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                            minWidth: 0,
                            flexShrink: 0,
                          }}>
                            <Flame width={14} height={14} color="#ea580c" />
                            <span style={{
                              fontSize: '12px',
                              color: '#6b7280',
                              whiteSpace: 'nowrap',
                            }}>Fat:</span>
                            <span style={{
                              fontSize: '13px',
                              fontWeight: '700',
                              color: '#374151',
                              whiteSpace: 'nowrap',
                            }}>{meal.fat_g || 0}g</span>
                          </div>
                        </div>
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
