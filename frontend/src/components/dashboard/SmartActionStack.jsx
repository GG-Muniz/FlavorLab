import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Coffee,
  Sun,
  Moon,
  Droplets,
  ChefHat,
  ArrowRight,
  Calendar,
  ChevronUp,
  ChevronDown
} from 'lucide-react';

const SmartActionStack = ({ onAction, mealsLoggedToday = { breakfast: false, lunch: false, dinner: false } }) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  /**
   * Smart Prioritization Logic
   * Builds and prioritizes actions based on:
   * - Time of day
   * - User completion status
   * - Contextual relevance
   */
  const getPrioritizedActions = () => {
    const currentHour = new Date().getHours();
    const allMealsLogged = mealsLoggedToday.breakfast && mealsLoggedToday.lunch && mealsLoggedToday.dinner;

    // Define all possible actions
    const allActions = [
      // Meal logging actions
      {
        id: 'breakfast',
        title: 'Log Breakfast',
        subtitle: 'Start your day right',
        icon: Coffee,
        gradient: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
        iconBg: '#fff7ed',
        iconColor: '#ea580c',
        actionColor: '#ea580c',
        cta: 'Log Now',
        priority: currentHour < 11 && !mealsLoggedToday.breakfast ? 100 : 20
      },
      {
        id: 'lunch',
        title: 'Log Lunch',
        subtitle: 'Fuel your afternoon',
        icon: Sun,
        gradient: 'linear-gradient(135deg, #fed7aa 0%, #fb923c 100%)',
        iconBg: '#fff7ed',
        iconColor: '#ea580c',
        actionColor: '#ea580c',
        cta: 'Log Now',
        priority: (currentHour >= 11 && currentHour < 16) && !mealsLoggedToday.lunch ? 100 : 30
      },
      {
        id: 'dinner',
        title: 'Log Dinner',
        subtitle: 'End your day well',
        icon: Moon,
        gradient: 'linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%)',
        iconBg: '#ede9fe',
        iconColor: '#7c3aed',
        actionColor: '#7c3aed',
        cta: 'Log Now',
        priority: (currentHour >= 16 && currentHour < 21) && !mealsLoggedToday.dinner ? 100 : 40
      },
      // Water logging - promoted when all meals logged
      {
        id: 'water',
        title: 'Log Water Intake',
        subtitle: 'Stay hydrated throughout the day',
        icon: Droplets,
        gradient: 'linear-gradient(135deg, #cffafe 0%, #a5f3fc 100%)',
        iconBg: '#ecfeff',
        iconColor: '#0891b2',
        actionColor: '#0891b2',
        cta: 'Add Water',
        priority: allMealsLogged ? 95 : (currentHour >= 21 ? 90 : 50)
      }
    ];

    // Sort by priority (highest first)
    return allActions.sort((a, b) => b.priority - a.priority);
  };

  const actions = getPrioritizedActions();

  // Reset to top when actions change (time passes, meals logged)
  useEffect(() => {
    setCurrentIndex(0);
  }, [mealsLoggedToday.breakfast, mealsLoggedToday.lunch, mealsLoggedToday.dinner]);

  // Navigation handlers
  const goToNext = () => {
    setCurrentIndex((prev) => (prev + 1) % actions.length);
  };

  const goToPrevious = () => {
    setCurrentIndex((prev) => (prev - 1 + actions.length) % actions.length);
  };

  // Animation variants for flipper effect
  const cardVariants = {
    initial: {
      opacity: 0,
      y: 30,
      scale: 0.95
    },
    animate: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        duration: 0.4,
        ease: [0.4, 0, 0.2, 1]
      }
    },
    exit: {
      opacity: 0,
      y: -30,
      scale: 0.95,
      transition: {
        duration: 0.3,
        ease: [0.4, 0, 0.2, 1]
      }
    }
  };

  const currentAction = actions[currentIndex];
  const IconComponent = currentAction.icon;

  return (
    <div style={{ position: 'relative' }}>
      <AnimatePresence mode="wait">
        <motion.div
          key={currentIndex}
          variants={cardVariants}
          initial="initial"
          animate="animate"
          exit="exit"
          whileHover={{ scale: 1.02 }}
          style={{
            background: currentAction.gradient,
            borderRadius: '24px',
            padding: '32px',
            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
            border: '1px solid rgba(255, 255, 255, 0.5)',
            position: 'relative',
            overflow: 'hidden',
            cursor: 'pointer'
          }}
        >
          {/* Decorative background circles */}
          <div style={{
            position: 'absolute',
            top: '-40px',
            right: '-40px',
            width: '160px',
            height: '160px',
            background: 'rgba(255, 255, 255, 0.2)',
            borderRadius: '50%'
          }} />
          <div style={{
            position: 'absolute',
            bottom: '-60px',
            left: '-60px',
            width: '200px',
            height: '200px',
            background: 'rgba(255, 255, 255, 0.15)',
            borderRadius: '50%'
          }} />

          {/* Content */}
          <div style={{ position: 'relative', zIndex: 1 }}>
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
              <motion.div
                animate={{
                  scale: [1, 1.1, 1],
                  rotate: [0, 5, -5, 0]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  repeatType: 'reverse'
                }}
                style={{
                  width: '48px',
                  height: '48px',
                  background: currentAction.iconBg,
                  borderRadius: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              >
                <IconComponent width={24} height={24} color={currentAction.iconColor} strokeWidth={2.5} />
              </motion.div>
              <div>
                <div style={{
                  fontSize: '12px',
                  fontWeight: '600',
                  color: 'rgba(0, 0, 0, 0.5)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                  marginBottom: '4px'
                }}>
                  Smart Action
                </div>
                <h3 style={{
                  fontSize: '24px',
                  fontWeight: '700',
                  color: '#111827',
                  margin: 0
                }}>
                  {currentAction.title}
                </h3>
              </div>
            </div>

            {/* Subtitle */}
            <p style={{
              fontSize: '16px',
              color: '#374151',
              marginBottom: '24px',
              margin: '0 0 24px 0'
            }}>
              {currentAction.subtitle}
            </p>

            {/* Action Button */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onAction && onAction(currentAction.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '12px',
                width: '100%',
                padding: '16px 24px',
                background: '#ffffff',
                border: 'none',
                borderRadius: '12px',
                fontSize: '16px',
                fontWeight: '700',
                color: currentAction.actionColor,
                cursor: 'pointer',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                transition: 'all 0.2s'
              }}
            >
              <ChefHat width={20} height={20} />
              <span>{currentAction.cta}</span>
              <ArrowRight width={20} height={20} />
            </motion.button>

            {/* Stack Indicator */}
            <div style={{
              textAlign: 'center',
              marginTop: '16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px'
            }}>
              <div style={{
                fontSize: '12px',
                fontWeight: '600',
                color: 'rgba(0, 0, 0, 0.4)',
                letterSpacing: '0.5px'
              }}>
                {currentIndex + 1} of {actions.length}
              </div>
              <div style={{ display: 'flex', gap: '4px' }}>
                {actions.map((_, idx) => (
                  <div
                    key={idx}
                    style={{
                      width: idx === currentIndex ? '16px' : '6px',
                      height: '6px',
                      borderRadius: '3px',
                      background: idx === currentIndex
                        ? 'rgba(0, 0, 0, 0.6)'
                        : 'rgba(0, 0, 0, 0.2)',
                      transition: 'all 0.3s ease'
                    }}
                  />
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      </AnimatePresence>

      {/* Navigation Controls - Vertical Flipper Buttons */}
      <div style={{
        position: 'absolute',
        right: '16px',
        top: '50%',
        transform: 'translateY(-50%)',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        zIndex: 10
      }}>
        {/* Previous Action Button */}
        <motion.button
          whileHover={{ scale: 1.1, y: -2 }}
          whileTap={{ scale: 0.9 }}
          onClick={(e) => {
            e.stopPropagation();
            goToPrevious();
          }}
          style={{
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            background: 'rgba(255, 255, 255, 0.9)',
            border: '1px solid rgba(0, 0, 0, 0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            transition: 'all 0.2s'
          }}
        >
          <ChevronUp width={20} height={20} color="#374151" strokeWidth={2.5} />
        </motion.button>

        {/* Next Action Button */}
        <motion.button
          whileHover={{ scale: 1.1, y: 2 }}
          whileTap={{ scale: 0.9 }}
          onClick={(e) => {
            e.stopPropagation();
            goToNext();
          }}
          style={{
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            background: 'rgba(255, 255, 255, 0.9)',
            border: '1px solid rgba(0, 0, 0, 0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            transition: 'all 0.2s'
          }}
        >
          <ChevronDown width={20} height={20} color="#374151" strokeWidth={2.5} />
        </motion.button>
      </div>
    </div>
  );
};

export default SmartActionStack;
