/**
 * MealDetailModal Component
 *
 * A modal dialog that displays full recipe details for a selected meal.
 * Shows ingredients, instructions, nutrition information, and other meal metadata.
 *
 * Features:
 * - Full-screen modal overlay with glassmorphism design
 * - Displays ingredients list with measurements
 * - Step-by-step cooking instructions
 * - Nutrition information breakdown
 * - Prep/cook time and servings
 * - Close on overlay click or X button
 * - Smooth animations with Framer Motion
 *
 * @component
 * @example
 * <MealDetailModal
 *   meal={selectedMeal}
 *   isOpen={!!selectedMeal}
 *   onClose={() => setSelectedMeal(null)}
 * />
 */

import { motion, AnimatePresence } from 'framer-motion';
import { X, Clock, Users, Flame, ChefHat } from 'lucide-react';
import PropTypes from 'prop-types';
import './MealDetailModal.css';

const MealDetailModal = ({ meal, isOpen, onClose }) => {
  // Don't render anything if modal is closed or no meal selected
  if (!isOpen || !meal) return null;

  /**
   * Get color scheme based on meal type
   * Matches MealCard color system for visual consistency
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
   * Converts snake_case to Title Case
   */
  const formatMealType = (type) => {
    return type
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const colors = getMealTypeColor(meal.type);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Overlay Background */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0, 0, 0, 0.5)',
              backdropFilter: 'blur(4px)',
              WebkitBackdropFilter: 'blur(4px)',
              zIndex: 1000,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '20px',
              overflowY: 'auto'
            }}
          >
            {/* Modal Content */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              onClick={(e) => e.stopPropagation()} // Prevent closing when clicking inside modal
              style={{
                background: 'rgba(255, 255, 255, 0.95)',
                backdropFilter: 'blur(20px)',
                WebkitBackdropFilter: 'blur(20px)',
                borderRadius: '24px',
                maxWidth: '800px',
                width: '100%',
                maxHeight: '90vh',
                overflowY: 'auto',
                boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                border: '2px solid #f3f4f6',
                position: 'relative'
              }}
            >
              {/* Close Button */}
              <button
                onClick={onClose}
                style={{
                  position: 'absolute',
                  top: '20px',
                  right: '20px',
                  width: '40px',
                  height: '40px',
                  borderRadius: '12px',
                  background: '#ffffff',
                  border: '2px solid #e5e7eb',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  zIndex: 10
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = '#f9fafb';
                  e.currentTarget.style.borderColor = '#d1d5db';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = '#ffffff';
                  e.currentTarget.style.borderColor = '#e5e7eb';
                }}
              >
                <X width={20} height={20} color="#374151" />
              </button>

              {/* Modal Header */}
              <div style={{
                padding: '32px 32px 24px',
                borderBottom: '2px solid #f3f4f6'
              }}>
                {/* Meal Type Badge */}
                <div
                  style={{
                    display: 'inline-block',
                    padding: '6px 12px',
                    background: colors.bg,
                    borderRadius: '8px',
                    marginBottom: '12px',
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
                <h2 style={{
                  fontSize: '28px',
                  fontWeight: '700',
                  color: '#111827',
                  marginBottom: '16px',
                  lineHeight: '1.2'
                }}>
                  {meal.name}
                </h2>

                {/* Meal Description */}
                <p style={{
                  fontSize: '16px',
                  color: '#6b7280',
                  lineHeight: '1.6',
                  marginBottom: '20px'
                }}>
                  {meal.description}
                </p>

                {/* Meta Information Row */}
                <div style={{
                  display: 'flex',
                  gap: '16px',
                  flexWrap: 'wrap'
                }}>
                  {/* Calories */}
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '10px 14px',
                    background: '#fef3c7',
                    borderRadius: '10px',
                    border: '1px solid #fde68a'
                  }}>
                    <Flame width={18} height={18} color="#d97706" />
                    <span style={{
                      fontSize: '14px',
                      fontWeight: '600',
                      color: '#d97706'
                    }}>
                      {meal.calories} kcal
                    </span>
                  </div>

                  {/* Servings */}
                  {meal.servings && (
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      padding: '10px 14px',
                      background: '#dbeafe',
                      borderRadius: '10px',
                      border: '1px solid #bfdbfe'
                    }}>
                      <Users width={18} height={18} color="#0284c7" />
                      <span style={{
                        fontSize: '14px',
                        fontWeight: '600',
                        color: '#0284c7'
                      }}>
                        {meal.servings} servings
                      </span>
                    </div>
                  )}

                  {/* Prep + Cook Time */}
                  {meal.prep_time_minutes && (
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      padding: '10px 14px',
                      background: '#f3e8ff',
                      borderRadius: '10px',
                      border: '1px solid #e9d5ff'
                    }}>
                      <Clock width={18} height={18} color="#9333ea" />
                      <span style={{
                        fontSize: '14px',
                        fontWeight: '600',
                        color: '#9333ea'
                      }}>
                        {meal.prep_time_minutes + (meal.cook_time_minutes || 0)} min
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Modal Body */}
              <div style={{ padding: '32px' }}>
                {/* Ingredients Section */}
                {meal.ingredients && meal.ingredients.length > 0 && (
                  <div style={{ marginBottom: '32px' }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      marginBottom: '16px'
                    }}>
                      <div style={{
                        width: 32,
                        height: 32,
                        background: '#dcfce7',
                        borderRadius: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <ChefHat width={18} height={18} color="#16a34a" />
                      </div>
                      <h3 style={{
                        fontSize: '20px',
                        fontWeight: '600',
                        color: '#111827',
                        margin: 0
                      }}>
                        Ingredients
                      </h3>
                    </div>
                    <ul style={{
                      listStyle: 'none',
                      padding: 0,
                      margin: 0,
                      display: 'grid',
                      gap: '10px'
                    }}>
                      {meal.ingredients.map((ingredient, idx) => (
                        <li key={idx} style={{
                          padding: '12px 16px',
                          background: '#f9fafb',
                          borderRadius: '10px',
                          border: '1px solid #e5e7eb',
                          fontSize: '14px',
                          color: '#374151',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '12px'
                        }}>
                          <span style={{
                            width: '6px',
                            height: '6px',
                            background: '#22c55e',
                            borderRadius: '50%',
                            flexShrink: 0
                          }} />
                          {ingredient}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Instructions Section */}
                {meal.instructions && meal.instructions.length > 0 && (
                  <div style={{ marginBottom: '32px' }}>
                    <h3 style={{
                      fontSize: '20px',
                      fontWeight: '600',
                      color: '#111827',
                      marginBottom: '16px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px'
                    }}>
                      <div style={{
                        width: 32,
                        height: 32,
                        background: '#dbeafe',
                        borderRadius: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <span style={{ fontSize: '16px' }}>📝</span>
                      </div>
                      Instructions
                    </h3>
                    <ol style={{
                      listStyle: 'none',
                      padding: 0,
                      margin: 0,
                      counterReset: 'step-counter',
                      display: 'grid',
                      gap: '16px'
                    }}>
                      {meal.instructions.map((instruction, idx) => (
                        <li key={idx} style={{
                          padding: '16px',
                          background: '#f9fafb',
                          borderRadius: '12px',
                          border: '1px solid #e5e7eb',
                          fontSize: '14px',
                          color: '#374151',
                          lineHeight: '1.6',
                          display: 'flex',
                          gap: '16px',
                          counterIncrement: 'step-counter'
                        }}>
                          <span style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            width: '28px',
                            height: '28px',
                            background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
                            color: '#ffffff',
                            borderRadius: '50%',
                            fontSize: '13px',
                            fontWeight: '700',
                            flexShrink: 0
                          }}>
                            {idx + 1}
                          </span>
                          <span>{instruction}</span>
                        </li>
                      ))}
                    </ol>
                  </div>
                )}

                {/* Nutrition Section */}
                {meal.nutrition && (
                  <div>
                    <h3 style={{
                      fontSize: '20px',
                      fontWeight: '600',
                      color: '#111827',
                      marginBottom: '16px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px'
                    }}>
                      <div style={{
                        width: 32,
                        height: 32,
                        background: '#fef3c7',
                        borderRadius: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <span style={{ fontSize: '16px' }}>🥗</span>
                      </div>
                      Nutrition Information
                    </h3>
                    <div style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                      gap: '12px'
                    }}>
                      {Object.entries(meal.nutrition).map(([key, value]) => (
                        <div key={key} style={{
                          padding: '14px',
                          background: '#f9fafb',
                          borderRadius: '10px',
                          border: '1px solid #e5e7eb'
                        }}>
                          <div style={{
                            fontSize: '12px',
                            color: '#6b7280',
                            fontWeight: '500',
                            textTransform: 'capitalize',
                            marginBottom: '4px'
                          }}>
                            {key.replace(/_/g, ' ')}
                          </div>
                          <div style={{
                            fontSize: '16px',
                            color: '#111827',
                            fontWeight: '700'
                          }}>
                            {value}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* No Details Available Message */}
                {!meal.ingredients && !meal.instructions && !meal.nutrition && (
                  <div style={{
                    padding: '32px',
                    textAlign: 'center',
                    color: '#6b7280'
                  }}>
                    <p>Additional recipe details are not available for this meal.</p>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

// ============================================================================
// PropTypes Definition
// ============================================================================

MealDetailModal.propTypes = {
  /**
   * Meal data object with full recipe details
   */
  meal: PropTypes.shape({
    type: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    calories: PropTypes.number.isRequired,
    description: PropTypes.string.isRequired,
    ingredients: PropTypes.arrayOf(PropTypes.string),
    servings: PropTypes.number,
    prep_time_minutes: PropTypes.number,
    cook_time_minutes: PropTypes.number,
    instructions: PropTypes.arrayOf(PropTypes.string),
    nutrition: PropTypes.object
  }),

  /**
   * Whether the modal is currently open
   */
  isOpen: PropTypes.bool.isRequired,

  /**
   * Callback function to close the modal
   */
  onClose: PropTypes.func.isRequired
};

export default MealDetailModal;
