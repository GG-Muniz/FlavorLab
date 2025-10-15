import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Utensils,
  Sparkles,
  X,
  ArrowRight,
  ArrowLeft
} from 'lucide-react';
import './FinalPreferences.css';

const FinalPreferences = ({ initialData, onDataChange, onBackStep, onGeneratePlan }) => {
  const [dislikeInput, setDislikeInput] = useState('');

  const handleAddDislike = (e) => {
    if (e.key === 'Enter' && dislikeInput.trim() !== '') {
      e.preventDefault();
      const updatedDislikes = [...initialData.dislikedIngredients, dislikeInput.trim()];
      onDataChange({ dislikedIngredients: updatedDislikes });
      setDislikeInput('');
    }
  };

  const handleRemoveDislike = (ingredientToRemove) => {
    const updatedDislikes = initialData.dislikedIngredients.filter(
      ing => ing !== ingredientToRemove
    );
    onDataChange({ dislikedIngredients: updatedDislikes });
  };

  const handleMealsPerDayChange = (mealOption) => {
    onDataChange({ mealsPerDay: mealOption });
  };

  // Stagger animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
        delayChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
        ease: 'easeOut'
      }
    }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Header */}
      <motion.div variants={itemVariants} style={{ marginBottom: '48px' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          marginBottom: '12px'
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 6px -1px rgb(34 197 94 / 0.3)'
          }}>
            <span style={{ fontSize: '20px', fontWeight: '700', color: '#ffffff' }}>
              3
            </span>
          </div>
          <h2 style={{
            fontSize: '28px',
            fontWeight: '700',
            color: '#111827',
            margin: 0
          }}>
            Final Touches
          </h2>
        </div>
        <p style={{
          fontSize: '16px',
          color: '#6b7280',
          margin: 0
        }}>
          Just a few more details to personalize your experience
        </p>
      </motion.div>

      {/* Meals Per Day Section */}
      <motion.div variants={itemVariants} className="background-card meals-card">
        <div className="section-header">
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            marginBottom: '12px'
          }}>
            <div style={{
              width: '32px',
              height: '32px',
              background: '#e0f2fe',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Utensils width={20} height={20} color="#0284c7" />
            </div>
            <h3 style={{
              fontSize: '20px',
              fontWeight: '600',
              color: '#111827',
              margin: 0
            }}>
              How many meals do you eat per day?
            </h3>
          </div>
          <p style={{
            fontSize: '14px',
            color: '#6b7280',
            margin: 0
          }}>
            Choose one option
          </p>
        </div>

        <div className="meals-grid">
          <motion.div
            className={`selectable-card meal-option-card ${initialData.mealsPerDay === '3-meals' ? 'selected' : ''}`}
            onClick={() => handleMealsPerDayChange('3-meals')}
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.98 }}
          >
            <div style={{
              fontSize: '48px',
              marginBottom: '12px'
            }}>
              🍽️
            </div>
            <h4 style={{
              fontSize: '16px',
              fontWeight: '700',
              color: initialData.mealsPerDay === '3-meals' ? '#16a34a' : '#111827',
              margin: 0
            }}>
              3 Meals
            </h4>
          </motion.div>

          <motion.div
            className={`selectable-card meal-option-card ${initialData.mealsPerDay === '3-meals-2-snacks' ? 'selected' : ''}`}
            onClick={() => handleMealsPerDayChange('3-meals-2-snacks')}
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.98 }}
          >
            <div style={{
              fontSize: '48px',
              marginBottom: '12px'
            }}>
              🍽️🍎
            </div>
            <h4 style={{
              fontSize: '16px',
              fontWeight: '700',
              color: initialData.mealsPerDay === '3-meals-2-snacks' ? '#16a34a' : '#111827',
              margin: 0
            }}>
              3 Meals + 2 Snacks
            </h4>
          </motion.div>

          <motion.div
            className={`selectable-card meal-option-card ${initialData.mealsPerDay === '5-6-smaller' ? 'selected' : ''}`}
            onClick={() => handleMealsPerDayChange('5-6-smaller')}
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.98 }}
          >
            <div style={{
              fontSize: '48px',
              marginBottom: '12px'
            }}>
              🍱
            </div>
            <h4 style={{
              fontSize: '16px',
              fontWeight: '700',
              color: initialData.mealsPerDay === '5-6-smaller' ? '#16a34a' : '#111827',
              margin: 0
            }}>
              5-6 Smaller Meals
            </h4>
          </motion.div>
        </div>
      </motion.div>

      {/* Disliked Ingredients Section */}
      <motion.div variants={itemVariants} className="background-card dislikes-card">
        <div className="section-header">
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            marginBottom: '12px'
          }}>
            <div style={{
              width: '32px',
              height: '32px',
              background: '#e0f2fe',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Sparkles width={20} height={20} color="#0284c7" />
            </div>
            <h3 style={{
              fontSize: '20px',
              fontWeight: '600',
              color: '#111827',
              margin: 0
            }}>
              Any ingredients you dislike?
            </h3>
          </div>
          <p style={{
            fontSize: '14px',
            color: '#6b7280',
            margin: 0
          }}>
            We'll exclude these from your recommendations (optional)
          </p>
        </div>

        <input
          type="text"
          value={dislikeInput}
          onChange={(e) => setDislikeInput(e.target.value)}
          onKeyDown={handleAddDislike}
          placeholder="e.g., cilantro, mushrooms, olives..."
          className="ingredient-input"
        />
        <p style={{
          fontSize: '12px',
          color: '#9ca3af',
          margin: '8px 0 16px 0'
        }}>
          Press Enter to add
        </p>

        {initialData.dislikedIngredients.length > 0 && (
          <div className="tags-container">
            {initialData.dislikedIngredients.map((ing, index) => (
              <span key={`${ing}-${index}`} className="tag">
                {ing}
                <button
                  onClick={() => handleRemoveDislike(ing)}
                  className="tag-remove-button"
                  aria-label={`Remove ${ing}`}
                >
                  <X width={14} height={14} />
                </button>
              </span>
            ))}
          </div>
        )}
      </motion.div>

      {/* Navigation Buttons */}
      <motion.div variants={itemVariants} style={{
        display: 'flex',
        justifyContent: 'space-between',
        paddingTop: '16px',
        borderTop: '1px solid #f3f4f6'
      }}>
        <button
          onClick={onBackStep}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '14px 28px',
            background: '#ffffff',
            color: '#374151',
            border: '2px solid #e5e7eb',
            borderRadius: '12px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = '#d1d5db';
            e.currentTarget.style.background = '#f9fafb';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = '#e5e7eb';
            e.currentTarget.style.background = '#ffffff';
          }}
        >
          <ArrowLeft width={20} height={20} />
          <span>Back</span>
        </button>

        <button
          onClick={onGeneratePlan}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '14px 32px',
            background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
            color: '#ffffff',
            border: 'none',
            borderRadius: '12px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'all 0.2s',
            boxShadow: '0 4px 6px -1px rgb(34 197 94 / 0.3)'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.boxShadow = '0 10px 15px -3px rgb(34 197 94 / 0.4)';
            e.currentTarget.style.transform = 'translateY(-2px)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.boxShadow = '0 4px 6px -1px rgb(34 197 94 / 0.3)';
            e.currentTarget.style.transform = 'translateY(0)';
          }}
        >
          <Sparkles width={20} height={20} />
          <span>Generate My Plan</span>
          <ArrowRight width={20} height={20} />
        </button>
      </motion.div>
    </motion.div>
  );
};

export default FinalPreferences;
