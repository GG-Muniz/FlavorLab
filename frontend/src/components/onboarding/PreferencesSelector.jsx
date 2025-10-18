import { useState } from 'react';
import { motion } from 'framer-motion';
import { BackgroundCard, SectionHeader, SelectableCard } from '../ui/CardGrid.jsx';
import {
  AlertCircle,
  Leaf,
  ArrowRight,
  ArrowLeft,
  CheckCircle2
} from 'lucide-react';
import './PreferencesSelector.css';

// Canonical options for allergies and dietary preferences (uniform across app)
const mockPreferenceOptions = {
  allergies: [
    { id: 'Dairy', name: 'Dairy', icon: '🥛' },
    { id: 'Gluten', name: 'Gluten', icon: '🌾' },
    { id: 'Peanuts', name: 'Peanuts', icon: '🥜' },
    { id: 'Tree Nuts', name: 'Tree Nuts', icon: '🌰' },
    { id: 'Soy', name: 'Soy', icon: '🌱' },
    { id: 'Eggs', name: 'Eggs', icon: '🥚' },
    { id: 'Shellfish', name: 'Shellfish', icon: '🦞' },
    { id: 'Fish', name: 'Fish', icon: '🐟' },
    { id: 'Sesame', name: 'Sesame', icon: '🌿' }
  ],
  diets: [
    { id: 'vegetarian', name: 'Vegetarian', description: 'No meat', icon: '🥗' },
    { id: 'vegan', name: 'Vegan', description: 'No animal products', icon: '🌱' },
    { id: 'pescatarian', name: 'Pescatarian', description: 'No meat, but fish', icon: '🐟' },
    { id: 'keto', name: 'Keto', description: 'Low-carb, high-fat', icon: '🥑' },
    { id: 'paleo', name: 'Paleo', description: 'Primal eating', icon: '🥩' },
    // Use commonly supported fruit icon for Mediterranean
    { id: 'mediterranean', name: 'Mediterranean', description: 'Plant-based foods', icon: '🍇' }
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
      // Enforce single-selection for diet
      const currentlySelected = selectedDiets[0];
      const newSelection = currentlySelected === id ? [] : [id];
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
      <BackgroundCard tone="blue">
        <SectionHeader icon={(props) => <AlertCircle {...props} />} title="Any Food Allergies?" subtitle="Select all that apply (optional)" iconBg="#fff7ed" iconColor="#ea580c" />
        <div className="card-grid allergies-grid">
          {mockPreferenceOptions.allergies.map((allergy) => {
            const isSelected = selectedAllergies.includes(allergy.id);
            return (
              <SelectableCard key={allergy.id} palette="orange" selected={isSelected} onClick={() => handleSelection(allergy.id, 'allergy')} emoji={allergy.icon} title={allergy.name} />
            );
          })}
        </div>
      </BackgroundCard>

      {/* Dietary Preferences Section */}
      <BackgroundCard tone="green">
        <SectionHeader icon={(props) => <Leaf {...props} />} title="Dietary Preference" subtitle="Select one (optional)" iconBg="#f0fdf4" iconColor="#16a34a" />
        <div className="card-grid diets-grid">
          {mockPreferenceOptions.diets.map((diet) => {
            const isSelected = selectedDiets.includes(diet.id);
            return (
              <SelectableCard key={diet.id} palette="green" selected={isSelected} onClick={() => handleSelection(diet.id.toLowerCase(), 'diet')} emoji={diet.icon} title={diet.name} subtitle={diet.description} />
            );
          })}
        </div>
      </BackgroundCard>

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
            color: '#000000',
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
          <ArrowLeft width={20} height={20} color="#000000" />
          <span style={{ color: '#000000', opacity: 1, fontWeight: 700 }}>Back</span>
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
