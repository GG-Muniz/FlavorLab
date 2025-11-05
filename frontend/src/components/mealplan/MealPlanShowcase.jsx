/**
 * MealPlanShowcase Component
 *
 * Main parent component for displaying AI-generated personalized meal plans.
 * Handles fetching data from the backend, managing loading/error states,
 * and displaying the meal plan overview with individual meal cards.
 *
 * Features:
 * - Fetches meal plan data using Claude Haiku LLM
 * - Displays health goal summary
 * - Shows meal cards in a responsive grid layout
 * - Handles loading and error states gracefully
 * - Modal view for detailed recipe information
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { generateMealPlan } from '../../services/mealPlanApi';
import { getHealthPillars } from '../../services/healthPillarsApi';
import { motion } from 'framer-motion';
import { ChefHat, RefreshCw, AlertCircle, Sparkles, Flame, Dumbbell, HeartPulse, Edit } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useData } from '../../context/DataContext';
import MealCard from './MealCard';
import MealDetailModal from './MealDetailModal';

const MealPlanShowcase = () => {
  // ============================================================================
  // State Management
  // ============================================================================

  /**
   * Meal plan data from the backend
   * Structure: { plan: [{ day: string, meals: [...] }], health_goal_summary: string }
   */
  const [mealPlan, setMealPlan] = useState(null);

  /**
   * Loading state for API request
   */
  const [loading, setLoading] = useState(false);

  /**
   * Error message if meal plan generation fails
   */
  const [error, setError] = useState(null);

  /**
   * Initial state - true until user clicks "Generate Plan"
   */
  const [isInitialState, setIsInitialState] = useState(true);

  /**
   * Currently selected meal for detailed view modal (future enhancement)
   */
  const [selectedMeal, setSelectedMeal] = useState(null);

  /**
   * Get user data from auth context and logged meals from data context
   */
  const { user } = useAuth();
  const { loggedMeals, refetchAll } = useData();

  /**
   * Navigation for editing preferences
   */
  const navigate = useNavigate();

  /**
   * Health pillars definitions from backend
   */
  const [pillars, setPillars] = useState([]);

  // ============================================================================
  // Data Fetching Logic
  // ============================================================================

  /**
   * Fetch meal plan from the backend
   *
   * Requests a meal plan with full recipe details (ingredients, instructions, nutrition).
   * Can be called again to retry after an error.
   */
  const loadMealPlan = async () => {
    try {
      // Exit initial state
      setIsInitialState(false);

      // Reset states before fetching
      setLoading(true);
      setError(null);

      // Fetch meal plan WITH recipes for modal display
      const data = await generateMealPlan(true);

      // Debug: Log the meal plan data to inspect IDs
      console.log('📋 [MealPlanShowcase] Generated meal plan:', JSON.stringify(data, null, 2));

      // Store the meal plan data
      setMealPlan(data);
    } catch (err) {
      // Capture error message for display
      setError(err.message);
      console.error('Error loading meal plan:', err);
    } finally {
      // Always set loading to false when done
      setLoading(false);
    }
  };

  /**
   * Fetch health pillars on mount
   */
  useEffect(() => {
    const fetchPillars = async () => {
      try {
        const data = await getHealthPillars();
        setPillars(data);
      } catch (err) {
        console.error('Error loading health pillars:', err);
        // Fail silently - not critical for meal plan display
      }
    };

    fetchPillars();
  }, []);

  /**
   * Load existing generated meals on mount if available
   * Only shows the most recent meal plan generation
   */
  useEffect(() => {
    const loadExistingMealPlan = async () => {
      try {
        const { getMeals } = await import('../../services/mealsApi');
        const existingMeals = await getMeals('generated');

        if (existingMeals && existingMeals.length > 0) {
          console.log('📋 [MealPlanShowcase] Found existing generated meals:', existingMeals);

          // Sort meals by created_at descending to get the most recent ones
          const sortedMeals = [...existingMeals].sort((a, b) =>
            new Date(b.created_at) - new Date(a.created_at)
          );

          // Get the most recent creation date
          const mostRecentDate = sortedMeals[0].created_at;

          // Filter to only show meals from the most recent generation
          // (all meals created within 5 seconds are considered one generation)
          const mostRecentMeals = sortedMeals.filter(meal => {
            const mealDate = new Date(meal.created_at);
            const recentDate = new Date(mostRecentDate);
            // Consider meals created within 5 seconds as part of the same generation
            const timeDiff = Math.abs(recentDate - mealDate);
            return timeDiff < 5000; // 5 seconds
          });

          console.log('📋 [MealPlanShowcase] Showing only most recent meal plan generation:', mostRecentMeals);

          // Convert MealResponse[] format to LLMMealPlanResponse format
          const convertedPlan = {
            plan: [{
              day: 'Today',
              meals: mostRecentMeals.map(meal => ({
                id: meal.id,
                type: meal.meal_type || meal.type,
                name: meal.name,
                calories: meal.calories,
                description: meal.description,
                tags: meal.nutrition_info?.tags || [],
                ingredients: meal.ingredients || [],
                servings: meal.servings,
                prep_time_minutes: meal.prep_time_minutes,
                cook_time_minutes: meal.cook_time_minutes,
                instructions: meal.instructions || [],
                nutrition: meal.nutrition_info || {}
              }))
            }],
            health_goal_summary: null
          };

          console.log('📋 [MealPlanShowcase] Converted plan:', convertedPlan);
          setMealPlan(convertedPlan);
          setIsInitialState(false);
        }
      } catch (err) {
        console.error('Error loading existing meal plan:', err);
        // Fail silently - user can still generate new plans
      }
    };

    loadExistingMealPlan();
  }, []);

  // ============================================================================
  // Helper - Goal Icons Mapping
  // ============================================================================

  const goalIcons = {
    'weight-loss': { icon: Flame, emoji: '🔥', color: '#f97316' },
    'muscle-gain': { icon: Dumbbell, emoji: '💪', color: '#8b5cf6' },
    'wellness': { icon: HeartPulse, emoji: '🧘', color: '#ec4899' },
    'improved-health': { icon: HeartPulse, emoji: '❤️', color: '#ef4444' },
    'better-nutrition': { icon: ChefHat, emoji: '🥗', color: '#22c55e' }
  };

  const userGoal = user?.preferences?.survey_data?.primaryGoal;
  const goalData = userGoal ? goalIcons[userGoal] : null;

  // ============================================================================
  // Helper - Extract User Preferences Data
  // ============================================================================

  // Get user's selected health pillar IDs
  // First try preferences.health_goals (array of IDs),
  // then fallback to survey_data.healthPillars (array of pillar names)
  const userPillarIds = user?.preferences?.health_goals || [];
  const surveyHealthPillarNames = user?.preferences?.survey_data?.healthPillars || [];

  console.log('MealPlanShowcase - user.preferences:', user?.preferences);
  console.log('MealPlanShowcase - userPillarIds:', userPillarIds);
  console.log('MealPlanShowcase - surveyHealthPillarNames:', surveyHealthPillarNames);
  console.log('MealPlanShowcase - all pillars:', pillars);

  // Map IDs to human-readable pillar names
  let userPillarNames = [];
  if (userPillarIds.length > 0) {
    // Use the ID-based approach
    userPillarNames = pillars
      .filter(p => userPillarIds.includes(p.id))
      .map(p => p.name);
    console.log('MealPlanShowcase - using ID-based approach, userPillarNames:', userPillarNames);
  } else if (surveyHealthPillarNames.length > 0) {
    // Fallback: use names directly from survey_data
    userPillarNames = surveyHealthPillarNames;
    console.log('MealPlanShowcase - using survey_data.healthPillars, userPillarNames:', userPillarNames);
  } else if (mealPlan?.plan?.[0]?.meals) {
    // Last fallback: extract health goals from meal tags
    const allPillarNamesSet = new Set(pillars.map(p => p.name));
    const healthGoalsFromMeals = new Set();
    mealPlan.plan[0].meals.forEach(meal => {
      meal.tags?.forEach(tag => {
        if (allPillarNamesSet.has(tag)) {
          healthGoalsFromMeals.add(tag);
        }
      });
    });
    userPillarNames = Array.from(healthGoalsFromMeals);
    console.log('MealPlanShowcase - using meal tags fallback, userPillarNames:', userPillarNames);
  }

  console.log('MealPlanShowcase - FINAL userPillarNames:', userPillarNames);

  // Get all pillar names for tag filtering in MealCard
  const allPillarNames = pillars.map(p => p.name);

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

  // Get dietary restrictions
  const dietaryRestrictions = user?.preferences?.survey_data?.dietaryRestrictions || [];

  // Get allergies
  const allergies = user?.preferences?.survey_data?.allergies || [];

  // Get disliked ingredients from dietary_preferences
  const dislikedIngredients = user?.dietary_preferences?.disliked || [];

  // Get user's first name or fallback to full name or "User"
  const userName = user?.first_name || user?.name || null;

  // ============================================================================
  // Conditional Rendering - Initial State
  // ============================================================================

  if (isInitialState) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '500px',
          gap: '32px',
          padding: '48px 24px',
          textAlign: 'center'
        }}
      >
        {/* Animated Icon */}
        <motion.div
          animate={{
            scale: [1, 1.1, 1],
            rotate: [0, 5, -5, 0]
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: 'easeInOut'
          }}
          style={{
            width: 96,
            height: 96,
            background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
            borderRadius: '24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 20px 25px -5px rgba(34, 197, 94, 0.3)'
          }}
        >
          <Sparkles width={48} height={48} color="#ffffff" strokeWidth={2.5} />
        </motion.div>

        {/* Welcome Text */}
        <div style={{ maxWidth: '600px' }}>
          <h2 style={{
            fontSize: '36px',
            fontWeight: '700',
            color: '#111827',
            marginBottom: '16px',
            lineHeight: '1.2'
          }}>
            Welcome to Your AI Meal Planner
          </h2>
          <p style={{
            fontSize: '18px',
            color: '#6b7280',
            lineHeight: '1.6',
            marginBottom: '8px'
          }}>
            Let our AI nutritionist create a personalized meal plan tailored to your unique health goals and preferences.
          </p>
          <p style={{
            fontSize: '14px',
            color: '#9ca3af',
            lineHeight: '1.6'
          }}>
            Powered by Claude Haiku • Database-aware recommendations
          </p>
        </div>

        {/* Generate Button */}
        <motion.button
          onClick={loadMealPlan}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '12px',
            padding: '18px 36px',
            background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
            color: '#ffffff',
            border: 'none',
            borderRadius: '16px',
            fontSize: '18px',
            fontWeight: '700',
            cursor: 'pointer',
            boxShadow: '0 10px 25px -5px rgba(34, 197, 94, 0.4)',
            transition: 'all 0.3s'
          }}
        >
          <Sparkles width={24} height={24} />
          <span>Generate My Meal Plan</span>
        </motion.button>

        {/* Features List */}
        <div style={{
          display: 'flex',
          gap: '24px',
          flexWrap: 'wrap',
          justifyContent: 'center',
          marginTop: '16px'
        }}>
          {[
            '✨ Personalized Recipes',
            '🎯 Goal-Aligned Nutrition',
            '🥗 Dietary Restrictions Respected'
          ].map((feature, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 + idx * 0.1 }}
              style={{
                padding: '8px 16px',
                background: '#f9fafb',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: '500',
                color: '#374151'
              }}
            >
              {feature}
            </motion.div>
          ))}
        </div>
      </motion.div>
    );
  }

  // ============================================================================
  // Conditional Rendering - Loading State
  // ============================================================================

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '400px',
        gap: '20px'
      }}>
        {/* Loading Spinner Icon */}
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
            justifyContent: 'center'
          }}
        >
          <ChefHat width={32} height={32} color="#ffffff" />
        </motion.div>

        {/* Loading Text */}
        <div style={{ textAlign: 'center' }}>
          <h3 style={{
            fontSize: '20px',
            fontWeight: '600',
            color: '#374151',
            marginBottom: '8px'
          }}>
            Generating Your Meal Plan
          </h3>
          <p style={{
            fontSize: '14px',
            color: '#6b7280'
          }}>
            Our AI is crafting personalized meals just for you...
          </p>
        </div>
      </div>
    );
  }

  // ============================================================================
  // Conditional Rendering - Error State
  // ============================================================================

  if (error) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '400px',
        gap: '24px',
        padding: '32px'
      }}>
        {/* Error Icon */}
        <div style={{
          width: 64,
          height: 64,
          background: '#fef2f2',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <AlertCircle width={32} height={32} color="#ef4444" />
        </div>

        {/* Error Message */}
        <div style={{ textAlign: 'center', maxWidth: '500px' }}>
          <h3 style={{
            fontSize: '20px',
            fontWeight: '600',
            color: '#374151',
            marginBottom: '12px'
          }}>
            Unable to Generate Meal Plan
          </h3>
          <p style={{
            fontSize: '14px',
            color: '#6b7280',
            lineHeight: '1.6',
            marginBottom: '24px'
          }}>
            {error}
          </p>

          {/* Retry Button */}
          <button
            onClick={loadMealPlan}
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
              transition: 'all 0.2s'
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
  // Main Content - Meal Plan Display
  // ============================================================================

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      style={{
        maxWidth: '1200px',
        margin: '0 auto'
      }}
    >
      {/* NEW PERSONALIZED HEADER */}
      <div style={{
        marginBottom: '32px',
        display: 'flex',
        flexDirection: 'column',
        gap: '24px'
      }}>
        {/* Title Row with Goal Icon and Regenerate Button */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '16px',
          flexWrap: 'wrap'
        }}>
          {/* Title with Goal Icon */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '16px'
          }}>
            <h2 style={{
              fontSize: '32px',
              fontWeight: '700',
              color: '#111827',
              margin: 0
            }}>
              {userName ? `${userName}'s Meal Plan` : 'Your Meal Plan'}
            </h2>
            {goalData && (
              <motion.div
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ type: 'spring', stiffness: 200, damping: 15 }}
                style={{
                  fontSize: '32px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: '48px',
                  height: '48px',
                  background: `${goalData.color}20`,
                  borderRadius: '12px',
                  border: `2px solid ${goalData.color}40`
                }}
              >
                {goalData.emoji}
              </motion.div>
            )}
          </div>

          {/* Regenerate Button */}
          <motion.button
            onClick={loadMealPlan}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 20px',
              background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
              color: '#ffffff',
              border: 'none',
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              boxShadow: '0 4px 6px -1px rgba(59, 130, 246, 0.3)',
              transition: 'all 0.2s'
            }}
          >
            <RefreshCw width={16} height={16} color="#ffffff" />
            <span style={{ color: '#ffffff' }}>Generate New Meal Plan</span>
          </motion.button>
        </div>

        {/* User Preferences Summary - Vertical Layout */}
        {(userPillarNames.length > 0 || dietaryRestrictions.length > 0 || allergies.length > 0 || dislikedIngredients.length > 0) && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            style={{
              padding: '24px',
              background: 'rgba(255, 255, 255, 0.9)',
              backdropFilter: 'blur(10px)',
              WebkitBackdropFilter: 'blur(10px)',
              borderRadius: '12px',
              border: '2px solid #f3f4f6',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              display: 'flex',
              flexDirection: 'column',
              gap: '20px'
            }}
          >
            {/* Health Goals Row */}
            {userPillarNames.length > 0 && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <strong style={{ fontSize: '14px', color: '#374151', fontWeight: '600', minWidth: '90px' }}>
                  Health Goals:
                </strong>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', flex: 1 }}>
                  {userPillarNames.map((name, idx) => (
                    <span
                      key={`goal-${idx}`}
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        padding: '6px 12px',
                        background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                        border: 'none',
                        borderRadius: '6px',
                        fontSize: '13px',
                        fontWeight: '500',
                        color: '#ffffff',
                        whiteSpace: 'nowrap',
                        boxShadow: '0 1px 2px rgba(59, 130, 246, 0.3)'
                      }}
                    >
                      <span style={{ fontSize: '13px' }}>{getPillarEmoji(name)}</span>
                      {name}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Dietary Style & Allergies Container */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {/* Dietary Style Row */}
              {dietaryRestrictions.length > 0 && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <strong style={{ fontSize: '14px', color: '#374151', fontWeight: '600', minWidth: '90px' }}>
                    Dietary Style:
                  </strong>
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', flex: 1 }}>
                    {dietaryRestrictions.map((restriction, idx) => (
                      <span
                        key={`diet-${idx}`}
                        style={{
                          padding: '6px 12px',
                          background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                          border: 'none',
                          borderRadius: '6px',
                          fontSize: '13px',
                          fontWeight: '500',
                          color: '#ffffff',
                          textTransform: 'capitalize',
                          whiteSpace: 'nowrap',
                          boxShadow: '0 1px 2px rgba(16, 185, 129, 0.3)'
                        }}
                      >
                        {restriction}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Allergies Row */}
              {allergies.length > 0 && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <strong style={{ fontSize: '14px', color: '#374151', fontWeight: '600', minWidth: '90px' }}>
                    Allergies:
                  </strong>
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', flex: 1 }}>
                    {allergies.map((allergy, idx) => (
                      <span
                        key={`allergy-${idx}`}
                        style={{
                          padding: '6px 12px',
                          background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                          border: 'none',
                          borderRadius: '6px',
                          fontSize: '13px',
                          fontWeight: '500',
                          color: '#ffffff',
                          textTransform: 'capitalize',
                          whiteSpace: 'nowrap',
                          boxShadow: '0 1px 2px rgba(245, 158, 11, 0.3)'
                        }}
                      >
                        {allergy}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Avoiding Row */}
              {dislikedIngredients.length > 0 && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <strong style={{ fontSize: '14px', color: '#374151', fontWeight: '600', minWidth: '90px' }}>
                    Avoiding:
                  </strong>
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', flex: 1 }}>
                    {dislikedIngredients.map((item, idx) => {
                      const displayName = item?.name || item;
                      return (
                        <span
                          key={`disliked-${idx}`}
                          style={{
                            padding: '6px 12px',
                            background: 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)',
                            border: 'none',
                            borderRadius: '6px',
                            fontSize: '13px',
                            fontWeight: '500',
                            color: '#ffffff',
                            textTransform: 'capitalize',
                            whiteSpace: 'nowrap',
                            boxShadow: '0 1px 2px rgba(236, 72, 153, 0.3)'
                          }}
                        >
                          {displayName}
                        </span>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>

            {/* Horizontal Divider before Edit Button */}
            <div style={{ width: '100%', height: '1px', background: '#e5e7eb' }} />

            {/* Edit Preferences Button */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '4px' }}>
              <motion.button
                onClick={() => navigate('/app/nutritest')}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '8px 16px',
                  background: '#ffffff',
                  color: '#374151',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '13px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  whiteSpace: 'nowrap',
                  boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)'
                }}
              >
                <Edit width={14} height={14} />
                <span>Edit Preferences</span>
              </motion.button>
            </div>
          </motion.div>
        )}
      </div>


      {/* Meal Cards Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '24px'
      }}>
        {mealPlan?.plan[0]?.meals.map((meal, idx) => {
          // Check if this meal is already logged today
          const mealType = meal.type || meal.meal_type;
          const isLogged = loggedMeals?.some(
            loggedMeal => loggedMeal.name === meal.name &&
                         loggedMeal.meal_type?.toLowerCase() === mealType?.toLowerCase()
          ) || false;

          return (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * idx, duration: 0.4 }}
              style={{ height: '100%' }}
            >
              <MealCard
                meal={meal}
                pillarNames={allPillarNames}
                isLogged={isLogged}
                onClick={() => setSelectedMeal(meal)}
                onLogMeal={async (mealToLog) => {
                  try {
                    const { logMealForToday } = await import('../../services/mealsApi');
                    await logMealForToday(mealToLog.id);
                    // Refresh data to update logged status
                    await refetchAll();
                  } catch (error) {
                    console.error('Error logging meal:', error);
                    alert(`Failed to log meal: ${error.message || 'Unknown error'}`);
                  }
                }}
              />
            </motion.div>
          );
        })}
      </div>

      {/* Meal Detail Modal */}
      <MealDetailModal meal={selectedMeal} isOpen={!!selectedMeal} onClose={() => setSelectedMeal(null)} />
    </motion.div>
  );
};

export default MealPlanShowcase;
