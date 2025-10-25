import React from 'react';
import { Target } from 'lucide-react';
import { motion } from 'framer-motion';
import ProgressBar from '../ui/ProgressBar';

/**
 * MacronutrientsCard Component
 *
 * A presentational component that displays daily macronutrient totals.
 * This is a "dumb" component that receives all data from DataContext.
 *
 * Features:
 * - Displays Protein, Carbs, Fat, and Fiber with progress bars
 * - Real-time updates when meals are logged from any source
 * - Consistent with FlavorLab's glassmorphism design system
 *
 * @component
 */
const MacronutrientsCard = ({ macros, isLoading = false }) => {
  // Guard clause to prevent rendering errors if macro data is missing
  if (!macros) {
    return (
      <motion.div
        style={{
          background: 'rgba(255, 255, 255, 0.7)',
          backdropFilter: 'blur(10px)',
          WebkitBackdropFilter: 'blur(10px)',
          borderRadius: '24px',
          padding: '32px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
          border: '1px solid rgba(255, 255, 255, 0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '200px'
        }}
        whileHover={{
          scale: 1.02,
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.15)'
        }}
        transition={{ duration: 0.2 }}
      >
        <div style={{ color: '#6b7280', fontSize: '14px' }}>Calculating Macronutrients...</div>
      </motion.div>
    );
  }

  // Macro configuration with colors
  const macroConfig = [
    {
      key: 'protein',
      label: 'Protein',
      color: '#34D399' // Green
    },
    {
      key: 'carbs',
      label: 'Carbs',
      color: '#FBBF24' // Yellow
    },
    {
      key: 'fat',
      label: 'Fat',
      color: '#F87171' // Red
    },
    {
      key: 'fiber',
      label: 'Fiber',
      color: '#60A5FA' // Blue
    }
  ];

  if (isLoading) {
    return (
      <motion.div
        style={{
          background: 'rgba(255, 255, 255, 0.7)',
          backdropFilter: 'blur(10px)',
          WebkitBackdropFilter: 'blur(10px)',
          borderRadius: '24px',
          padding: '32px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
          border: '1px solid rgba(255, 255, 255, 0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '200px'
        }}
        whileHover={{
          scale: 1.02,
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.15)'
        }}
        transition={{ duration: 0.2 }}
      >
        <div style={{ color: '#6b7280', fontSize: '14px' }}>Loading macronutrients...</div>
      </motion.div>
    );
  }

  return (
    <motion.div
      style={{
        background: 'rgba(255, 255, 255, 0.7)',
        backdropFilter: 'blur(10px)',
        WebkitBackdropFilter: 'blur(10px)',
        borderRadius: '24px',
        padding: '32px',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        border: '1px solid rgba(255, 255, 255, 0.3)',
        position: 'relative',
        overflow: 'hidden'
      }}
      whileHover={{
        scale: 1.02,
        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.15)'
      }}
      transition={{ duration: 0.2 }}
    >
      <div style={{ position: 'relative' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <div style={{
            width: 32,
            height: 32,
            background: '#f0fdf4',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Target width={20} height={20} color="#22c55e" />
          </div>
          <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#374151', margin: 0 }}>
            Macronutrients
          </h3>
        </div>

        <div className="macronutrients-card">
          {macroConfig.map((macro) => {
            const macroData = macros?.[macro.key];
            const consumed = macroData?.consumed || 0;
            const goal = macroData?.goal || 0;

            return (
              <div key={macro.key} className="macro-row">
                <div className="macro-info">
                  <span className="macro-label">{macro.label}</span>
                  <span className="macro-values">
                    {consumed.toFixed(1)}g / {goal.toFixed(1)}g
                  </span>
                </div>
                <ProgressBar
                  consumed={consumed}
                  goal={goal}
                  color={macro.color}
                />
              </div>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
};

export default MacronutrientsCard;
