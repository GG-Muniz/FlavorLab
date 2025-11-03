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
import { Flame, CheckCircle2 } from 'lucide-react';
import PropTypes from 'prop-types';
import './MealCard.css';

const MealCard = ({ meal, pillarNames = [], isLogged = false, onClick, onLogMeal }) => {
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

  /**
   * Filter tags into dietary/constraint tags and health goal tags
   */
  const dietaryTags = meal.tags?.filter(tag => !pillarNames.includes(tag)) || [];
  const healthGoalTags = meal.tags?.filter(tag => pillarNames.includes(tag)) || [];

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

      {/* Dietary/Constraint Tags */}
      {dietaryTags.length > 0 && (
        <div
          className="dietary-tags"
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '6px',
            marginBottom: '8px'
          }}
        >
          {dietaryTags.map((tag, index) => {
            // Color mapping for dietary constraint tags
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

            const tagColors = getTagColor(tag);

            return (
              <span
                key={index}
                style={{
                  display: 'inline-block',
                  padding: '4px 10px',
                  fontSize: '11px',
                  fontWeight: '600',
                  color: tagColors.text,
                  background: tagColors.bg,
                  border: `1px solid ${tagColors.border}`,
                  borderRadius: '6px',
                  textTransform: 'capitalize',
                  letterSpacing: '0.3px'
                }}
              >
                {tag}
              </span>
            );
          })}
        </div>
      )}

      {/* Health Goal Tags */}
      {healthGoalTags.length > 0 && (
        <div
          className="health-goal-tags"
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '6px',
            marginBottom: '16px'
          }}
        >
          {healthGoalTags.map((tag, index) => (
            <span
              key={index}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                padding: '5px 12px',
                fontSize: '11px',
                fontWeight: '700',
                color: '#ffffff',
                background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                border: 'none',
                borderRadius: '8px',
                textTransform: 'capitalize',
                letterSpacing: '0.3px',
                boxShadow: '0 1px 2px rgba(59, 130, 246, 0.3)'
              }}
            >
              <span style={{ fontSize: '12px' }}>{getPillarEmoji(tag)}</span>
              {tag}
            </span>
          ))}
        </div>
      )}

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

      {/* Recipe Indicators - Always show if we have the data */}
      {(meal.servings || meal.prep_time_minutes || meal.cook_time_minutes) && (
        <div style={{
          marginTop: '16px',
          paddingTop: '16px',
          borderTop: '1px solid #e5e7eb',
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
              color: '#6b7280',
              fontWeight: '500'
            }}>
              <span>👥</span>
              <span>{meal.servings} servings</span>
            </div>
          )}
          {(meal.prep_time_minutes || meal.cook_time_minutes) && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '12px',
              color: '#6b7280',
              fontWeight: '500'
            }}>
              <span>⏱️</span>
              <span>{(meal.prep_time_minutes || 0) + (meal.cook_time_minutes || 0)} min</span>
            </div>
          )}
        </div>
      )}

      {/* Log Meal Button Section */}
      <div style={{ marginTop: '16px' }}>
        {meal.id && onLogMeal && (
          <button
            onClick={(e) => {
              e.stopPropagation(); // Prevent card click
              onLogMeal(meal);
            }}
            style={{
              width: '100%',
              padding: '10px 16px',
              background: isLogged ? '#f3f4f6' : 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
              color: isLogged ? '#6b7280' : '#ffffff',
              border: isLogged ? '1px solid #e5e7eb' : 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'all 0.2s',
              boxShadow: isLogged ? 'none' : '0 2px 4px rgba(34, 197, 94, 0.3)'
            }}
            onMouseEnter={(e) => {
              if (!isLogged) {
                e.currentTarget.style.transform = 'translateY(-1px)';
                e.currentTarget.style.boxShadow = '0 4px 6px rgba(34, 197, 94, 0.4)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isLogged) {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 2px 4px rgba(34, 197, 94, 0.3)';
              }
            }}
          >
            {isLogged ? <CheckCircle2 width={16} height={16} /> : <Flame width={16} height={16} />}
            {isLogged ? 'Logged ✔️' : 'Log Meal'}
          </button>
        )}
      </div>

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
    /** Optional: Tags for meal attributes (e.g., 'Gluten-Free', 'High-Protein') */
    tags: PropTypes.arrayOf(PropTypes.string),
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
   * Array of health pillar names for tag filtering
   */
  pillarNames: PropTypes.arrayOf(PropTypes.string),

  /**
   * Click handler function called when card is clicked
   * Receives the meal object as parameter
   */
  onClick: PropTypes.func.isRequired
};

export default MealCard;
