/**
 * MealCard Component
 *
 * A presentational component that displays a single meal in a card format.
 * Used within the MealPlanShowcase grid to show meal overview information.
 *
 * Features:
 * - Displays meal type, name, calories, and description
 * - Hover animations and visual feedback
 * - Click handler for viewing detailed recipe information
 * - Consistent with FlavorLab's glassmorphism design system
 *
 * @component
 * @example
 * <MealCard
 *   meal={{
 *     type: 'breakfast',
 *     name: 'Avocado Toast',
 *     calories: 350,
 *     description: 'Whole grain toast topped with mashed avocado'
 *   }}
 *   onClick={(meal) => console.log('Clicked:', meal)}
 * />
 */

import { motion } from 'framer-motion';
import { Flame } from 'lucide-react';
import PropTypes from 'prop-types';
import './MealCard.css';

const MealCard = ({ meal, onClick }) => {
  /**
   * Get color scheme based on meal type
   * Each meal type has a unique color palette for visual distinction
   */
  const getMealTypeColor = (type) => {
    const colorMap = {
      breakfast: {
        bg: '#fef3c7',
        text: '#d97706',
        border: '#fde68a'
      },
      morning_snack: {
        bg: '#fce7f3',
        text: '#db2777',
        border: '#fbcfe8'
      },
      lunch: {
        bg: '#dbeafe',
        text: '#0284c7',
        border: '#bfdbfe'
      },
      afternoon_snack: {
        bg: '#e0e7ff',
        text: '#6366f1',
        border: '#c7d2fe'
      },
      dinner: {
        bg: '#f3e8ff',
        text: '#9333ea',
        border: '#e9d5ff'
      },
      snack: {
        bg: '#fce7f3',
        text: '#db2777',
        border: '#fbcfe8'
      }
    };

    return colorMap[type] || colorMap.breakfast;
  };

  /**
   * Format meal type for display
   * Converts snake_case to Title Case with proper spacing
   */
  const formatMealType = (type) => {
    return type
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const colors = getMealTypeColor(meal.type);

  return (
    <motion.div
      className="meal-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{
        scale: 1.03,
        transition: { duration: 0.2 }
      }}
      onClick={() => onClick(meal)}
      style={{
        background: 'rgba(255, 255, 255, 0.9)',
        backdropFilter: 'blur(10px)',
        WebkitBackdropFilter: 'blur(10px)',
        borderRadius: '20px',
        padding: '24px',
        border: '2px solid #f3f4f6',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        cursor: 'pointer',
        transition: 'all 0.3s ease'
      }}
    >
      {/* Meal Type Badge */}
      <div
        className="meal-type-badge"
        style={{
          display: 'inline-block',
          padding: '6px 12px',
          background: colors.bg,
          borderRadius: '8px',
          marginBottom: '16px',
          border: `1px solid ${colors.border}`
        }}
      >
        <span style={{
          fontSize: '11px',
          fontWeight: '600',
          color: colors.text,
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          {formatMealType(meal.type)}
        </span>
      </div>

      {/* Meal Name */}
      <h3
        className="meal-name"
        style={{
          fontSize: '18px',
          fontWeight: '700',
          color: '#111827',
          marginBottom: '12px',
          lineHeight: '1.3',
          minHeight: '48px'
        }}
      >
        {meal.name}
      </h3>

      {/* Calories Section */}
      <div
        className="meal-calories"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          marginBottom: '16px',
          padding: '10px 12px',
          background: '#fef3c7',
          borderRadius: '10px',
          border: '1px solid #fde68a'
        }}
      >
        <div style={{
          width: 32,
          height: 32,
          background: '#ffffff',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <Flame width={18} height={18} color="#d97706" />
        </div>
        <div>
          <span style={{
            fontSize: '16px',
            fontWeight: '700',
            color: '#d97706'
          }}>
            {meal.calories}
          </span>
          <span style={{
            fontSize: '13px',
            fontWeight: '500',
            color: '#92400e',
            marginLeft: '4px'
          }}>
            kcal
          </span>
        </div>
      </div>

      {/* Meal Description */}
      <p
        className="meal-description"
        style={{
          fontSize: '14px',
          color: '#6b7280',
          lineHeight: '1.6',
          margin: 0,
          minHeight: '64px'
        }}
      >
        {meal.description}
      </p>

      {/* Recipe Indicators (if available) */}
      {meal.ingredients && (
        <div style={{
          marginTop: '16px',
          paddingTop: '16px',
          borderTop: '1px solid #f3f4f6',
          display: 'flex',
          gap: '12px',
          flexWrap: 'wrap'
        }}>
          {meal.servings && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '12px',
              color: '#6b7280'
            }}>
              <span>👥</span>
              <span>{meal.servings} servings</span>
            </div>
          )}
          {meal.prep_time_minutes && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '12px',
              color: '#6b7280'
            }}>
              <span>⏱️</span>
              <span>{meal.prep_time_minutes + (meal.cook_time_minutes || 0)} min</span>
            </div>
          )}
        </div>
      )}

      {/* Click Hint */}
      <div
        className="meal-click-hint"
        style={{
          marginTop: '16px',
          paddingTop: '16px',
          borderTop: '1px solid #f3f4f6',
          textAlign: 'center'
        }}
      >
        <span style={{
          fontSize: '12px',
          color: '#22c55e',
          fontWeight: '600',
          transition: 'color 0.2s'
        }}>
          Click to view {meal.ingredients ? 'full recipe' : 'details'}
        </span>
      </div>
    </motion.div>
  );
};

// ============================================================================
// PropTypes Definition
// ============================================================================

MealCard.propTypes = {
  /**
   * Meal data object containing all meal information
   */
  meal: PropTypes.shape({
    /** Type of meal (breakfast, lunch, dinner, snack, etc.) */
    type: PropTypes.string.isRequired,
    /** Name of the meal */
    name: PropTypes.string.isRequired,
    /** Calorie count */
    calories: PropTypes.number.isRequired,
    /** Meal description */
    description: PropTypes.string.isRequired,
    /** Optional: List of ingredients (for detailed view) */
    ingredients: PropTypes.arrayOf(PropTypes.string),
    /** Optional: Number of servings */
    servings: PropTypes.number,
    /** Optional: Preparation time in minutes */
    prep_time_minutes: PropTypes.number,
    /** Optional: Cooking time in minutes */
    cook_time_minutes: PropTypes.number,
    /** Optional: Cooking instructions */
    instructions: PropTypes.arrayOf(PropTypes.string),
    /** Optional: Nutrition information */
    nutrition: PropTypes.object
  }).isRequired,

  /**
   * Click handler function called when card is clicked
   * Receives the meal object as parameter
   */
  onClick: PropTypes.func.isRequired
};

export default MealCard;
