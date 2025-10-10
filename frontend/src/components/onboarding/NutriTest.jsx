import { useState } from 'react';
import {
  Zap,
  Apple,
  Shield,
  Moon,
  Brain,
  Heart,
  Dumbbell,
  Flame,
  ArrowRight,
  CheckCircle2
} from 'lucide-react';

const NutriTest = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedGoals, setSelectedGoals] = useState([]);

  const healthGoals = [
    {
      id: 1,
      title: 'Increased Energy',
      icon: Zap,
      color: '#fbbf24',
      bg: '#fef3c7',
      description: 'Boost your daily energy levels'
    },
    {
      id: 2,
      title: 'Improved Digestion',
      icon: Apple,
      color: '#ea580c',
      bg: '#fed7aa',
      description: 'Support your digestive health'
    },
    {
      id: 3,
      title: 'Enhanced Immunity',
      icon: Shield,
      color: '#06b6d4',
      bg: '#cffafe',
      description: 'Strengthen your immune system'
    },
    {
      id: 4,
      title: 'Better Sleep',
      icon: Moon,
      color: '#8b5cf6',
      bg: '#ede9fe',
      description: 'Improve sleep quality naturally'
    },
    {
      id: 5,
      title: 'Mental Clarity',
      icon: Brain,
      color: '#ec4899',
      bg: '#fce7f3',
      description: 'Enhance focus and cognition'
    },
    {
      id: 6,
      title: 'Heart Health',
      icon: Heart,
      color: '#ef4444',
      bg: '#fee2e2',
      description: 'Support cardiovascular wellness'
    },
    {
      id: 7,
      title: 'Muscle Recovery',
      icon: Dumbbell,
      color: '#16a34a',
      bg: '#dcfce7',
      description: 'Accelerate post-workout recovery'
    },
    {
      id: 8,
      title: 'Inflammation Reduction',
      icon: Flame,
      color: '#f97316',
      bg: '#ffedd5',
      description: 'Reduce inflammation naturally'
    }
  ];

  const handleGoalSelect = (goalId) => {
    setSelectedGoals(prev => {
      if (prev.includes(goalId)) {
        // Deselect if already selected
        return prev.filter(id => id !== goalId);
      } else if (prev.length < 4) {
        // Add if less than 4 selected
        return [...prev, goalId];
      }
      // Don't add if already at max (4)
      return prev;
    });
  };

  const handleNext = () => {
    if (selectedGoals.length > 0) {
      // TODO: Move to next step in the walkthrough
      console.log('Selected goals:', selectedGoals);
      setCurrentStep(2);
    }
  };

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
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
              {currentStep}
            </span>
          </div>
          <h2 style={{
            fontSize: '28px',
            fontWeight: '700',
            color: '#111827',
            margin: 0
          }}>
            Health Goals
          </h2>
        </div>
        <p style={{
          fontSize: '16px',
          color: '#6b7280',
          margin: 0
        }}>
          Select up to 4 health goals to get personalized meal recommendations ({selectedGoals.length}/4)
        </p>
      </div>

      {/* Health Goals Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '20px',
        marginBottom: '32px'
      }}>
        {healthGoals.map((goal) => {
          const IconComponent = goal.icon;
          const isSelected = selectedGoals.includes(goal.id);

          return (
            <button
              key={goal.id}
              onClick={() => handleGoalSelect(goal.id)}
              style={{
                position: 'relative',
                background: '#ffffff',
                border: isSelected ? `3px solid ${goal.color}` : '2px solid #f3f4f6',
                borderRadius: '20px',
                padding: '28px',
                cursor: 'pointer',
                transition: 'all 0.3s',
                textAlign: 'left',
                boxShadow: isSelected
                  ? `0 10px 25px -5px ${goal.color}40`
                  : '0 1px 3px 0 rgb(0 0 0 / 0.1)',
                transform: isSelected ? 'translateY(-4px) scale(1.02)' : 'translateY(0)',
              }}
              onMouseEnter={(e) => {
                if (!isSelected) {
                  e.currentTarget.style.boxShadow = '0 4px 6px -1px rgb(0 0 0 / 0.1)';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.borderColor = '#e5e7eb';
                }
              }}
              onMouseLeave={(e) => {
                if (!isSelected) {
                  e.currentTarget.style.boxShadow = '0 1px 3px 0 rgb(0 0 0 / 0.1)';
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.borderColor = '#f3f4f6';
                }
              }}
            >
              {/* Selection Indicator */}
              {isSelected && (
                <div style={{
                  position: 'absolute',
                  top: '16px',
                  right: '16px',
                }}>
                  <CheckCircle2 width={24} height={24} color={goal.color} fill={goal.bg} />
                </div>
              )}

              {/* Icon */}
              <div style={{
                width: '64px',
                height: '64px',
                background: goal.bg,
                borderRadius: '16px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '20px',
                transition: 'all 0.3s'
              }}>
                <IconComponent width={32} height={32} color={goal.color} strokeWidth={2} />
              </div>

              {/* Content */}
              <h3 style={{
                fontSize: '18px',
                fontWeight: '700',
                color: '#111827',
                marginBottom: '8px',
                margin: '0 0 8px 0'
              }}>
                {goal.title}
              </h3>
              <p style={{
                fontSize: '14px',
                color: '#6b7280',
                lineHeight: '1.5',
                margin: 0
              }}>
                {goal.description}
              </p>
            </button>
          );
        })}
      </div>

      {/* Next Button */}
      <div style={{
        display: 'flex',
        justifyContent: 'flex-end',
        paddingTop: '16px',
        borderTop: '1px solid #f3f4f6'
      }}>
        <button
          onClick={handleNext}
          disabled={selectedGoals.length === 0}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '14px 28px',
            background: selectedGoals.length > 0
              ? 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)'
              : '#e5e7eb',
            color: selectedGoals.length > 0 ? '#ffffff' : '#9ca3af',
            border: 'none',
            borderRadius: '12px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: selectedGoals.length > 0 ? 'pointer' : 'not-allowed',
            transition: 'all 0.2s',
            boxShadow: selectedGoals.length > 0
              ? '0 4px 6px -1px rgb(34 197 94 / 0.3)'
              : 'none'
          }}
          onMouseEnter={(e) => {
            if (selectedGoals.length > 0) {
              e.currentTarget.style.boxShadow = '0 10px 15px -3px rgb(34 197 94 / 0.4)';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }
          }}
          onMouseLeave={(e) => {
            if (selectedGoals.length > 0) {
              e.currentTarget.style.boxShadow = '0 4px 6px -1px rgb(34 197 94 / 0.3)';
              e.currentTarget.style.transform = 'translateY(0)';
            }
          }}
        >
          <span>Continue</span>
          <ArrowRight width={20} height={20} />
        </button>
      </div>

      {/* Step 2 Placeholder - TODO: Build out next steps */}
      {currentStep === 2 && (
        <div style={{
          marginTop: '32px',
          padding: '24px',
          background: '#f0fdf4',
          borderRadius: '16px',
          border: '1px solid #bbf7d0',
          textAlign: 'center'
        }}>
          <p style={{
            fontSize: '16px',
            color: '#16a34a',
            fontWeight: '600',
            margin: '0 0 16px 0'
          }}>
            Step 2 coming soon! This will continue the walkthrough to generate your personalized meal.
          </p>
          <button
            onClick={() => {
              console.log('NutriTest completed with goals:', selectedGoals);
              if (onComplete) {
                onComplete({ selectedGoals });
              }
            }}
            style={{
              padding: '12px 24px',
              background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
              color: '#ffffff',
              border: 'none',
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              boxShadow: '0 4px 6px -1px rgb(34 197 94 / 0.3)'
            }}
          >
            Complete Setup
          </button>
        </div>
      )}
    </div>
  );
};

export default NutriTest;
