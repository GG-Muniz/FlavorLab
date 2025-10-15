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
import { generateMealPlan } from '../../services/mealPlanApi';
import { motion } from 'framer-motion';
import { ChefHat, RefreshCw, AlertCircle } from 'lucide-react';
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
  const [loading, setLoading] = useState(true);

  /**
   * Error message if meal plan generation fails
   */
  const [error, setError] = useState(null);

  /**
   * Currently selected meal for detailed view modal (future enhancement)
   */
  const [selectedMeal, setSelectedMeal] = useState(null);

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
      // Reset states before fetching
      setLoading(true);
      setError(null);

      // Fetch meal plan WITH recipes for modal display
      const data = await generateMealPlan(true);

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
   * Load meal plan when component mounts
   */
  useEffect(() => {
    loadMealPlan();
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
      {/* Header Section */}
      <div style={{
        marginBottom: '32px',
        textAlign: 'center'
      }}>
        <h2 style={{
          fontSize: '32px',
          fontWeight: '700',
          color: '#111827',
          marginBottom: '12px'
        }}>
          Your Personalized Meal Plan
        </h2>
        <p style={{
          fontSize: '16px',
          color: '#6b7280'
        }}>
          AI-powered nutrition tailored to your health goals
        </p>
      </div>

      {/* Health Goal Summary Section */}
      {mealPlan?.health_goal_summary && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          style={{
            marginBottom: '32px',
            padding: '20px 24px',
            background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
            borderRadius: '16px',
            border: '2px solid #bbf7d0',
            boxShadow: '0 4px 6px -1px rgba(34, 197, 94, 0.1)'
          }}
        >
          <div style={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: '12px'
          }}>
            <div style={{
              width: 40,
              height: 40,
              background: '#ffffff',
              borderRadius: '10px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}>
              <ChefHat width={20} height={20} color="#16a34a" />
            </div>
            <div>
              <h3 style={{
                fontSize: '16px',
                fontWeight: '600',
                color: '#166534',
                marginBottom: '8px'
              }}>
                Meal Plan Overview
              </h3>
              <p style={{
                fontSize: '14px',
                color: '#15803d',
                lineHeight: '1.6',
                margin: 0
              }}>
                {mealPlan.health_goal_summary}
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Meal Cards Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '24px'
      }}>
        {mealPlan?.plan[0]?.meals.map((meal, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 * idx, duration: 0.4 }}
          >
            <MealCard meal={meal} onClick={() => setSelectedMeal(meal)} />
          </motion.div>
        ))}
      </div>

      {/* Meal Detail Modal */}
      <MealDetailModal meal={selectedMeal} isOpen={!!selectedMeal} onClose={() => setSelectedMeal(null)} />
    </motion.div>
  );
};

export default MealPlanShowcase;
