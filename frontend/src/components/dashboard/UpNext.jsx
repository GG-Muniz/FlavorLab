import { motion } from 'framer-motion';
import { Coffee, Sun, Moon, Droplets, ChefHat, ArrowRight } from 'lucide-react';

const UpNext = ({ onAction }) => {
  // Get current time
  const currentHour = new Date().getHours();

  // Determine the next action based on time of day
  const getNextAction = () => {
    if (currentHour < 11) {
      return {
        id: 'breakfast',
        title: 'Log Breakfast',
        subtitle: 'Start your day right',
        icon: Coffee,
        gradient: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
        iconBg: '#fff7ed',
        iconColor: '#ea580c',
        actionColor: '#ea580c'
      };
    } else if (currentHour < 16) {
      return {
        id: 'lunch',
        title: 'Log Lunch',
        subtitle: 'Fuel your afternoon',
        icon: Sun,
        gradient: 'linear-gradient(135deg, #fed7aa 0%, #fb923c 100%)',
        iconBg: '#fff7ed',
        iconColor: '#ea580c',
        actionColor: '#ea580c'
      };
    } else if (currentHour < 21) {
      return {
        id: 'dinner',
        title: 'Log Dinner',
        subtitle: 'End your day well',
        icon: Moon,
        gradient: 'linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%)',
        iconBg: '#ede9fe',
        iconColor: '#7c3aed',
        actionColor: '#7c3aed'
      };
    } else {
      // Late night - suggest water or plan tomorrow
      return {
        id: 'water',
        title: 'Log Water Intake',
        subtitle: 'Stay hydrated',
        icon: Droplets,
        gradient: 'linear-gradient(135deg, #cffafe 0%, #a5f3fc 100%)',
        iconBg: '#ecfeff',
        iconColor: '#0891b2',
        actionColor: '#0891b2'
      };
    }
  };

  const nextAction = getNextAction();
  const IconComponent = nextAction.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      whileHover={{ scale: 1.02 }}
      style={{
        background: nextAction.gradient,
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
              background: nextAction.iconBg,
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
            }}
          >
            <IconComponent width={24} height={24} color={nextAction.iconColor} strokeWidth={2.5} />
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
              Up Next
            </div>
            <h3 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#111827',
              margin: 0
            }}>
              {nextAction.title}
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
          {nextAction.subtitle}
        </p>

        {/* Action Button */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => onAction && onAction(nextAction.id)}
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
            color: nextAction.actionColor,
            cursor: 'pointer',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            transition: 'all 0.2s'
          }}
        >
          <ChefHat width={20} height={20} />
          <span>Log Now</span>
          <ArrowRight width={20} height={20} />
        </motion.button>

        {/* Quick alternative action */}
        <div style={{ textAlign: 'center', marginTop: '16px' }}>
          <button
            onClick={(e) => {
              e.stopPropagation();
              // Handle planning tomorrow's meals
              if (onAction) onAction('plan-tomorrow');
            }}
            style={{
              padding: '8px 16px',
              background: 'rgba(255, 255, 255, 0.7)',
              border: 'none',
              borderRadius: '8px',
              fontSize: '13px',
              fontWeight: '600',
              color: '#6b7280',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 1)';
              e.currentTarget.style.color = '#374151';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.7)';
              e.currentTarget.style.color = '#6b7280';
            }}
          >
            or Plan Tomorrow's Meals
          </button>
        </div>
      </div>
    </motion.div>
  );
};

export default UpNext;
