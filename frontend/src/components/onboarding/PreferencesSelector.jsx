import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  AlertCircle,
  Leaf,
  ArrowRight,
  ArrowLeft,
  CheckCircle2
} from 'lucide-react';
import './PreferencesSelector.css';

// Mock data for allergies and dietary preferences
const mockPreferenceOptions = {
  allergies: [
    { id: 'milk', name: 'Milk', icon: '🥛' },
    { id: 'eggs', name: 'Eggs', icon: '🥚' },
    { id: 'fish', name: 'Fish', icon: '🐟' },
    { id: 'shellfish', name: 'Crustacean Shellfish', icon: '🦞' },
    { id: 'treenuts', name: 'Tree Nuts', icon: '🌰' },
    { id: 'peanuts', name: 'Peanuts', icon: '🥜' },
    { id: 'wheat', name: 'Wheat', icon: '🌾' },
    { id: 'soybeans', name: 'Soybeans', icon: '🫘' },
    { id: 'sesame', name: 'Sesame', icon: '🫚' }
  ],
  diets: [
    { id: 'vegetarian', name: 'Vegetarian', description: 'No meat', icon: '🥗' },
    { id: 'vegan', name: 'Vegan', description: 'No animal products', icon: '🌱' },
    { id: 'pescatarian', name: 'Pescatarian', description: 'No meat, but fish', icon: '🐟' },
    { id: 'keto', name: 'Keto', description: 'Low-carb, high-fat', icon: '🥑' },
    { id: 'paleo', name: 'Paleo', description: 'Primal eating', icon: '🥩' },
    { id: 'mediterranean', name: 'Mediterranean', description: 'Plant-based foods', icon: '🫒' }
  ]
};

const PreferencesSelector = ({
  initialAllergies,
  initialDiets,
  onDataChange,
  onNextStep,
  onBackStep
}) => {
  // Initialize local state from props
  const [selectedAllergies, setSelectedAllergies] = useState(initialAllergies || []);
  const [selectedDiets, setSelectedDiets] = useState(initialDiets || []);

  // Unified selection handler
  const handleSelection = (id, type) => {
    if (type === 'allergy') {
      const newSelection = selectedAllergies.includes(id)
        ? selectedAllergies.filter(item => item !== id)
        : [...selectedAllergies, id];
      setSelectedAllergies(newSelection);
      onDataChange({ allergies: newSelection });
    } else if (type === 'diet') {
      // Allow multiple diet selections
      const newSelection = selectedDiets.includes(id)
        ? selectedDiets.filter(item => item !== id)
        : [...selectedDiets, id];
      setSelectedDiets(newSelection);
      onDataChange({ diets: newSelection });
    }
  };

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: '48px' }}>
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
              2
            </span>
          </div>
          <h2 style={{
            fontSize: '28px',
            fontWeight: '700',
            color: '#111827',
            margin: 0
          }}>
            Preferences & Allergies
          </h2>
        </div>
        <p style={{
          fontSize: '16px',
          color: '#6b7280',
          margin: 0
        }}>
          Help us personalize your meal recommendations
        </p>
      </div>

      {/* Allergies Section */}
      <div className="background-card allergies-card">
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
              background: '#fff7ed',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <AlertCircle width={20} height={20} color="#ea580c" />
            </div>
            <h3 style={{
              fontSize: '20px',
              fontWeight: '600',
              color: '#111827',
              margin: 0
            }}>
              Any Food Allergies?
            </h3>
          </div>
          <p style={{
            fontSize: '14px',
            color: '#6b7280',
            margin: 0
          }}>
            Select all that apply (optional)
          </p>
        </div>

        {/* Allergies Grid */}
        <div className="card-grid allergies-grid">
          {mockPreferenceOptions.allergies.map((allergy) => {
            const isSelected = selectedAllergies.includes(allergy.id);

            return (
              <motion.div
                key={allergy.id}
                className={`selectable-card allergy-card ${isSelected ? 'selected' : ''}`}
                onClick={() => handleSelection(allergy.id, 'allergy')}
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.98 }}
              >
                {isSelected && (
                  <div className="check-icon">
                    <CheckCircle2 width={16} height={16} color="#ea580c" fill="#fff7ed" />
                  </div>
                )}
                <span style={{
                  fontSize: '40px',
                  marginBottom: '8px'
                }}>
                  {allergy.icon}
                </span>
                <span style={{
                  fontSize: '14px',
                  fontWeight: '600',
                  color: isSelected ? '#ea580c' : '#374151',
                  textAlign: 'center'
                }}>
                  {allergy.name}
                </span>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Dietary Preferences Section */}
      <div className="background-card diets-card">
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
              background: '#f0fdf4',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Leaf width={20} height={20} color="#16a34a" />
            </div>
            <h3 style={{
              fontSize: '20px',
              fontWeight: '600',
              color: '#111827',
              margin: 0
            }}>
              Dietary Preference
            </h3>
          </div>
          <p style={{
            fontSize: '14px',
            color: '#6b7280',
            margin: 0
          }}>
            Select all that apply (optional)
          </p>
        </div>

        {/* Diets Grid */}
        <div className="card-grid diets-grid">
          {mockPreferenceOptions.diets.map((diet) => {
            const isSelected = selectedDiets.includes(diet.id);

            return (
              <motion.div
                key={diet.id}
                className={`selectable-card diet-card ${isSelected ? 'selected' : ''}`}
                onClick={() => handleSelection(diet.id, 'diet')}
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.98 }}
              >
                {isSelected && (
                  <div className="check-icon">
                    <CheckCircle2 width={20} height={20} color="#16a34a" fill="#f0fdf4" />
                  </div>
                )}
                <span style={{
                  fontSize: '48px',
                  marginBottom: '12px'
                }}>
                  {diet.icon}
                </span>
                <span style={{
                  fontSize: '16px',
                  fontWeight: '700',
                  color: isSelected ? '#16a34a' : '#111827',
                  marginBottom: '4px'
                }}>
                  {diet.name}
                </span>
                <span style={{
                  fontSize: '12px',
                  color: isSelected ? '#15803d' : '#6b7280'
                }}>
                  {diet.description}
                </span>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Navigation Buttons */}
      <div style={{
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
          onClick={onNextStep}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '14px 28px',
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
          <span>Complete Setup</span>
          <ArrowRight width={20} height={20} />
        </button>
      </div>
    </div>
  );
};

export default PreferencesSelector;
