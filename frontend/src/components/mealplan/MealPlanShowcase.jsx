/**
 * MealPlanShowcase Component
 *
 * Main parent component for displaying saved meal templates.
 * Handles fetching meal templates from the database, managing loading/error states,
 * and displaying meal template cards with "Log Meal" functionality.
 *
 * Features:
 * - Fetches saved meal templates (source=GENERATED)
 * - Displays meal cards in a responsive grid layout
 * - "Generate New Meals" button to create fresh meal plans
 * - "Log Meal" button on each card to log templates as consumed
 * - Handles loading and error states gracefully
 * - Modal view for detailed recipe information
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { generateMealPlan } from '../../services/mealPlanApi';
import { getMeals, logMealForToday } from '../../services/mealsApi';
import { motion } from 'framer-motion';
import { ChefHat, RefreshCw, AlertCircle, Sparkles } from 'lucide-react';
import MealCard from './MealCard';
import MealDetailModal from './MealDetailModal';
import { useDashboard } from '../../contexts/DashboardContext';

const MealPlanShowcase = () => {
  const navigate = useNavigate();
  const { updateSummary } = useDashboard();

  // ============================================================================
  // State Management
  // ============================================================================

  /**
   * Meal templates from the database (source=GENERATED)
   */
  const [mealTemplates, setMealTemplates] = useState([]);

  /**
   * Loading state for API request
   */
  const [loading, setLoading] = useState(true);

  /**
   * Error message if fetching fails
   */
  const [error, setError] = useState(null);

  /**
   * Currently selected meal for detailed view modal
   */
  const [selectedMeal, setSelectedMeal] = useState(null);

  /**
   * Loading state for generating new meals
   */
  const [generating, setGenerating] = useState(false);

  // ============================================================================
  // Data Fetching Logic
  // ============================================================================

  /**
   * Fetch meal templates from the database
   *
   * Fetches all saved meal templates (source=GENERATED) for the current user.
   */
  const loadMealTemplates = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch meal templates with source=generated filter
      const templates = await getMeals('generated');

      setMealTemplates(templates);
    } catch (err) {
      setError(err.message);
      console.error('Error loading meal templates:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Generate new meal plan using LLM
   *
   * Calls the LLM API to generate fresh meal suggestions and saves them as templates.
   */
  const handleGenerateNewMeals = async () => {
    try {
      setGenerating(true);
      setError(null);

      // Generate meal plan WITH recipes (true)
      await generateMealPlan(true);

      // Reload templates to show newly generated meals
      await loadMealTemplates();
    } catch (err) {
      setError(err.message);
      console.error('Error generating meals:', err);
    } finally {
      setGenerating(false);
    }
  };

  /**
   * Log a meal for today and navigate to dashboard with updated summary
   *
   * Calls the new /meals/{meal_id}/log endpoint which returns the complete
   * dashboard summary including today's total calories and remaining calories.
   */
  const handleLogMeal = async (mealTemplate) => {
    try {
      // Call the new endpoint that logs the meal AND returns dashboard summary
      const dashboardSummary = await logMealForToday(mealTemplate.id);

      // Update the dashboard context with the new summary
      updateSummary(dashboardSummary);

      // Navigate to dashboard tab
      navigate('/?tab=dashboard');

      // Optionally reload meal templates to remove the logged one from GENERATED list
      await loadMealTemplates();
    } catch (err) {
      console.error('Error logging meal:', err);
      alert(`Failed to log meal: ${err.message}`);
    }
  };

  /**
   * Load meal templates when component mounts
   */
  useEffect(() => {
    loadMealTemplates();
  }, []);

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
            Loading Your Meal Plans
          </h3>
          <p style={{
            fontSize: '14px',
            color: '#6b7280'
          }}>
            Fetching your saved meal templates...
          </p>
        </div>
      </div>
    );
  }

  // ============================================================================
  // Conditional Rendering - Error State
  // ============================================================================

  if (error && mealTemplates.length === 0) {
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
            Unable to Load Meal Plans
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
            onClick={loadMealTemplates}
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
  // Conditional Rendering - Empty State
  // ============================================================================

  if (mealTemplates.length === 0) {
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
        {/* Empty State Icon */}
        <div style={{
          width: 80,
          height: 80,
          background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <ChefHat width={40} height={40} color="#16a34a" />
        </div>

        {/* Empty State Message */}
        <div style={{ textAlign: 'center', maxWidth: '500px' }}>
          <h3 style={{
            fontSize: '24px',
            fontWeight: '700',
            color: '#111827',
            marginBottom: '12px'
          }}>
            No Meal Plans Yet
          </h3>
          <p style={{
            fontSize: '16px',
            color: '#6b7280',
            lineHeight: '1.6',
            marginBottom: '32px'
          }}>
            Generate your first personalized meal plan using AI. Our intelligent system will create meals tailored to your health goals and preferences.
          </p>

          {/* Generate Button */}
          <button
            onClick={handleGenerateNewMeals}
            disabled={generating}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '10px',
              padding: '14px 32px',
              background: generating ? '#9ca3af' : 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
              color: '#ffffff',
              border: 'none',
              borderRadius: '12px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: generating ? 'not-allowed' : 'pointer',
              boxShadow: '0 4px 6px -1px rgba(34, 197, 94, 0.3)',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              if (!generating) {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 10px 15px -3px rgba(34, 197, 94, 0.4)';
              }
            }}
            onMouseLeave={(e) => {
              if (!generating) {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(34, 197, 94, 0.3)';
              }
            }}
          >
            {generating ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                >
                  <RefreshCw width={20} height={20} />
                </motion.div>
                <span>Generating...</span>
              </>
            ) : (
              <>
                <Sparkles width={20} height={20} />
                <span>Generate Meal Plan</span>
              </>
            )}
          </button>
        </div>
      </div>
    );
  }

  // ============================================================================
  // Main Content - Meal Templates Display
  // ============================================================================

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '32px',
        background: 'linear-gradient(135deg, #dbeafe 0%, #e0f2fe 100%)',
        borderRadius: '24px',
        minHeight: '600px'
      }}
    >
      {/* Header Section */}
      <div style={{
        marginBottom: '32px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <div>
          <h2 style={{
            fontSize: '32px',
            fontWeight: '700',
            color: '#0f172a',
            marginBottom: '8px'
          }}>
            Your Meal Plans
          </h2>
          <p style={{
            fontSize: '16px',
            color: '#334155',
            fontWeight: '500'
          }}>
            {mealTemplates.length} saved meal template{mealTemplates.length !== 1 ? 's' : ''}
          </p>
        </div>

        {/* Generate New Meals Button */}
        <button
          onClick={handleGenerateNewMeals}
          disabled={generating}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '12px 24px',
            background: generating ? '#9ca3af' : '#0ea5e9',
            color: '#ffffff',
            border: 'none',
            borderRadius: '12px',
            fontSize: '14px',
            fontWeight: '600',
            cursor: generating ? 'not-allowed' : 'pointer',
            boxShadow: '0 4px 6px -1px rgba(14, 165, 233, 0.4)',
            transition: 'all 0.3s ease'
          }}
          onMouseEnter={(e) => {
            if (!generating) {
              e.currentTarget.style.background = '#7dd3fc';
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 8px 12px -2px rgba(125, 211, 252, 0.5)';
            }
          }}
          onMouseLeave={(e) => {
            if (!generating) {
              e.currentTarget.style.background = '#0ea5e9';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(14, 165, 233, 0.4)';
            }
          }}
        >
          {generating ? (
            <>
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              >
                <RefreshCw width={16} height={16} color="#ffffff" />
              </motion.div>
              <span style={{ color: '#ffffff' }}>Generating...</span>
            </>
          ) : (
            <>
              <Sparkles width={16} height={16} color="#ffffff" />
              <span style={{ color: '#ffffff' }}>Generate New Meals</span>
            </>
          )}
        </button>
      </div>

      {/* Meal Cards Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '24px'
      }}>
        {mealTemplates.map((meal, idx) => (
          <motion.div
            key={meal.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 * idx, duration: 0.4 }}
          >
            <MealCard
              meal={{
                id: meal.id,
                type: meal.meal_type || 'meal',
                name: meal.name,
                calories: meal.calories,
                description: meal.description || 'No description available',
                ingredients: meal.ingredients,
                servings: meal.servings,
                prep_time_minutes: meal.prep_time_minutes,
                cook_time_minutes: meal.cook_time_minutes,
                instructions: meal.instructions,
                nutrition: meal.nutrition_info
              }}
              onClick={() => setSelectedMeal(meal)}
              onLogMeal={handleLogMeal}
            />
          </motion.div>
        ))}
      </div>

      {/* Meal Detail Modal */}
      {selectedMeal && (
        <MealDetailModal
          meal={{
            id: selectedMeal.id,
            type: selectedMeal.meal_type || 'meal',
            name: selectedMeal.name,
            calories: selectedMeal.calories,
            description: selectedMeal.description || 'No description available',
            ingredients: selectedMeal.ingredients,
            servings: selectedMeal.servings,
            prep_time_minutes: selectedMeal.prep_time_minutes,
            cook_time_minutes: selectedMeal.cook_time_minutes,
            instructions: selectedMeal.instructions,
            nutrition: selectedMeal.nutrition_info
          }}
          isOpen={!!selectedMeal}
          onClose={() => setSelectedMeal(null)}
        />
      )}
    </motion.div>
  );
};

export default MealPlanShowcase;
