import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
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
import { getHealthPillars } from '../../services/healthPillarsApi';
import './HealthPillarsSelector.css';

const HealthPillarsSelector = ({ initialSelections, onDataChange, onNextStep }) => {
  // Local state for selected pillars - initialized from parent's data
  const [selectedPillars, setSelectedPillars] = useState(initialSelections || []);

  // State for API data
  const [pillars, setPillars] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Map pillar IDs to UI configuration (icons and colors)
  const pillarUIConfig = {
    1: { icon: Zap, color: '#fbbf24', bg: '#fef3c7' }, // Increased Energy
    2: { icon: Apple, color: '#ea580c', bg: '#fed7aa' }, // Improved Digestion
    3: { icon: Shield, color: '#06b6d4', bg: '#cffafe' }, // Enhanced Immunity
    4: { icon: Moon, color: '#8b5cf6', bg: '#ede9fe' }, // Better Sleep
    5: { icon: Brain, color: '#ec4899', bg: '#fce7f3' }, // Mental Clarity
    6: { icon: Heart, color: '#ef4444', bg: '#fee2e2' }, // Heart Health
    7: { icon: Dumbbell, color: '#16a34a', bg: '#dcfce7' }, // Muscle Recovery
    8: { icon: Flame, color: '#f97316', bg: '#ffedd5' } // Inflammation Reduction
  };

  // Fetch health pillars from API
  useEffect(() => {
    const fetchHealthPillars = async () => {
      try {
        setIsLoading(true);
        const data = await getHealthPillars();

        // Map API data to include UI configuration
        const enrichedPillars = data.map(pillar => ({
          id: pillar.id,
          title: pillar.name,
          description: pillar.description,
          icon: pillarUIConfig[pillar.id]?.icon || Zap,
          color: pillarUIConfig[pillar.id]?.color || '#22c55e',
          bg: pillarUIConfig[pillar.id]?.bg || '#f0fdf4'
        }));

        setPillars(enrichedPillars);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch health pillars:', err);
        setError('Failed to load health goals. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchHealthPillars();
  }, []);

  const handlePillarSelect = (pillarId) => {
    let newSelectionArray;

    if (selectedPillars.includes(pillarId)) {
      // Deselect if already selected
      newSelectionArray = selectedPillars.filter(id => id !== pillarId);
    } else if (selectedPillars.length < 4) {
      // Add if less than 4 selected
      newSelectionArray = [...selectedPillars, pillarId];
    } else {
      // Don't add if already at max (4)
      return;
    }

    // Update local state
    setSelectedPillars(newSelectionArray);

    // Report changes back to parent
    onDataChange({ healthPillars: newSelectionArray });
  };

  // Loading state
  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '64px 32px' }}>
        <div style={{
          width: '56px',
          height: '56px',
          margin: '0 auto 24px',
          background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          animation: 'pulse 2s infinite'
        }}>
          <Zap width={28} height={28} color="#ffffff" />
        </div>
        <style>
          {`
            @keyframes pulse {
              0%, 100% { opacity: 1; transform: scale(1); }
              50% { opacity: 0.7; transform: scale(1.05); }
            }
          `}
        </style>
        <p style={{
          fontSize: '16px',
          fontWeight: '600',
          color: '#374151',
          margin: 0
        }}>
          Loading health goals...
        </p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div style={{ textAlign: 'center', padding: '64px 32px' }}>
        <div style={{
          width: '56px',
          height: '56px',
          margin: '0 auto 24px',
          background: '#fee2e2',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <Flame width={28} height={28} color="#ef4444" />
        </div>
        <p style={{
          fontSize: '16px',
          fontWeight: '600',
          color: '#374151',
          marginBottom: '8px'
        }}>
          {error}
        </p>
        <button
          onClick={() => window.location.reload()}
          style={{
            marginTop: '16px',
            padding: '10px 20px',
            background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
            color: '#ffffff',
            border: 'none',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: '600',
            cursor: 'pointer',
            boxShadow: '0 4px 6px -1px rgb(34 197 94 / 0.3)'
          }}
        >
          Retry
        </button>
      </div>
    );
  }

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
              1
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
          Select up to 4 health goals to get personalized meal recommendations ({selectedPillars.length}/4)
        </p>
      </div>

      {/* Health Goals Grid */}
      <div className="background-card health-pillars-card">
        <div className="health-goals-grid">
          {pillars.map((pillar) => {
            const IconComponent = pillar.icon;
            const isSelected = selectedPillars.includes(pillar.id);

            return (
              <motion.div
                key={pillar.id}
                className={`health-pillar-card ${isSelected ? 'selected' : ''}`}
                onClick={() => handlePillarSelect(pillar.id)}
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.98 }}
                style={{
                  border: isSelected ? `3px solid ${pillar.color}` : '2px solid transparent',
                  boxShadow: isSelected
                    ? `0 10px 25px -5px ${pillar.color}40`
                    : '0px 4px 8px rgba(0, 0, 0, 0.05)'
                }}
              >
                {/* Selection Indicator */}
                {isSelected && (
                  <div className="pillar-check-icon">
                    <CheckCircle2 width={24} height={24} color={pillar.color} fill={pillar.bg} />
                  </div>
                )}

                {/* Icon */}
                <div
                  className="pillar-icon-container"
                  style={{ background: pillar.bg }}
                >
                  <IconComponent width={32} height={32} color={pillar.color} strokeWidth={2} />
                </div>

                {/* Content */}
                <h3 className="pillar-title">
                  {pillar.title}
                </h3>
                <p className="pillar-description">
                  {pillar.description}
                </p>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Next Button */}
      <div className="health-pillars-nav">
        <button
          onClick={onNextStep}
          disabled={selectedPillars.length === 0}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '14px 28px',
            background: selectedPillars.length > 0
              ? 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)'
              : '#e5e7eb',
            color: selectedPillars.length > 0 ? '#ffffff' : '#9ca3af',
            border: 'none',
            borderRadius: '12px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: selectedPillars.length > 0 ? 'pointer' : 'not-allowed',
            transition: 'all 0.2s',
            boxShadow: selectedPillars.length > 0
              ? '0 4px 6px -1px rgb(34 197 94 / 0.3)'
              : 'none'
          }}
          onMouseEnter={(e) => {
            if (selectedPillars.length > 0) {
              e.currentTarget.style.boxShadow = '0 10px 15px -3px rgb(34 197 94 / 0.4)';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }
          }}
          onMouseLeave={(e) => {
            if (selectedPillars.length > 0) {
              e.currentTarget.style.boxShadow = '0 4px 6px -1px rgb(34 197 94 / 0.3)';
              e.currentTarget.style.transform = 'translateY(0)';
            }
          }}
        >
          <span>Continue</span>
          <ArrowRight width={20} height={20} />
        </button>
      </div>
    </div>
  );
};

export default HealthPillarsSelector;
