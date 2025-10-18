import { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import HealthPillarsSelector from './HealthPillarsSelector';
import PreferencesSelector from './PreferencesSelector';
import FinalPreferences from './FinalPreferences';
import LoadingOverlay from './LoadingOverlay';
import { submitSurvey } from '../../services/mealPlanApi';
import './NutriTest.css';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const NutriTest = ({ onComplete }) => {
  const { user, updateProfile } = useAuth();
  const navigate = useNavigate();
  // Master state object - holds all data from the entire flow
  const [formData, setFormData] = useState({
    healthPillars: [],
    allergies: [],
    diets: [],
    // Step 3 fields
    mealsPerDay: '3', // '3', '3-meals-2-snacks', or '6'
    dislikedIngredients: []
  });

  // Track which step the user is on
  const [currentStep, setCurrentStep] = useState(1); // 1 for pillars, 2 for preferences, etc.

  // Loading state for API call
  const [isLoading, setIsLoading] = useState(false);

  // Pre-populate from AuthContext on mount
  useEffect(() => {
    if (!user) return;
    const goals = user.health_goals || {};
    const prefs = user.dietary_preferences || {};
    const normalizeDiet = (d) => (typeof d === 'string' ? d.trim().toLowerCase().replace('pescetarian', 'pescatarian') : d);
    setFormData(prev => ({
      ...prev,
      // For pillars: if your backend stores IDs, map appropriately; otherwise derive from keys
      healthPillars: Array.isArray(goals?.selectedGoals)
        ? goals.selectedGoals
        : (Array.isArray(goals) ? goals : []),
      allergies: Array.isArray(prefs?.allergies) ? prefs.allergies : [],
      diets: Array.isArray(prefs?.diet)
        ? prefs.diet.map(normalizeDiet)
        : (prefs?.diet ? [normalizeDiet(prefs.diet)] : []),
      mealsPerDay: prefs?.meals_per_day || prev.mealsPerDay,
      dislikedIngredients: Array.isArray(prefs?.disliked) ? prefs.disliked : []
    }));
  }, [user]);

  // Single function for any child to update the master formData
  const handleDataChange = (stepData) => {
    setFormData(prevData => ({ ...prevData, ...stepData }));
  };

  // Functions to control navigation
  const handleNext = () => {
    setCurrentStep(prevStep => prevStep + 1);
  };

  const handleBack = () => {
    setCurrentStep(prevStep => prevStep - 1);
  };

  // Handle final completion
  const handleComplete = async () => {
    const payload = {
      // Map NutriTest data into backend schema
      health_goals: (formData.healthPillars && formData.healthPillars.length)
        ? { selectedGoals: formData.healthPillars }
        : undefined,
      dietary_preferences: {
        diet: (formData.diets?.[0] || '').trim().toLowerCase(),
        allergies: formData.allergies || [],
        disliked: formData.dislikedIngredients || [],
        meals_per_day: formData.mealsPerDay || undefined
      }
    };
    try {
      setIsLoading(true);
      await updateProfile(payload);
      if (onComplete) onComplete(payload);
      navigate('/profile', { state: { defaultTab: 'goals' } });
    } finally {
      setIsLoading(false);
    }
  };

  // Handle generate plan with loading state
  const handleGeneratePlan = async () => {
    setIsLoading(true);
    console.log('SENDING THIS TO THE LLM:', formData);

    try {
      // Submit survey data to backend
      await submitSurvey(formData);
      console.log('Survey submitted successfully!');

      // Complete the NutriTest flow
      await handleComplete();
    } catch (error) {
      console.error('Error submitting survey:', error);
      setIsLoading(false);
      // TODO: Show error message to user
      alert(`Failed to submit survey: ${error.message}`);
    }
  };

  // Page transition variants
  const pageVariants = {
    initial: { opacity: 0, x: 50 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -50 }
  };

  const pageTransition = {
    duration: 0.4,
    ease: 'easeInOut'
  };

  return (
    <div className="nutri-test-container" style={{ position: 'relative', minHeight: '100vh' }}>
      <AnimatePresence mode="wait">
        {/* Step 1: Health Pillars */}
        {currentStep === 1 && (
          <motion.div
            key="step-1"
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={pageTransition}
          >
            <HealthPillarsSelector
              initialSelections={formData.healthPillars}
              onDataChange={handleDataChange}
              onNextStep={handleNext}
            />
          </motion.div>
        )}

        {/* Step 2: Allergies & Preferences */}
        {currentStep === 2 && (
          <motion.div
            key="step-2"
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={pageTransition}
          >
            <PreferencesSelector
              initialAllergies={formData.allergies}
              initialDiets={formData.diets}
              onDataChange={handleDataChange}
              onNextStep={handleNext}
              onBackStep={handleBack}
            />
          </motion.div>
        )}

        {/* Step 3: Final Touches */}
        {currentStep === 3 && (
          <motion.div
            key="step-3"
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={pageTransition}
          >
            <FinalPreferences
              initialData={formData}
              onDataChange={handleDataChange}
              onBackStep={handleBack}
              onGeneratePlan={handleGeneratePlan}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading Overlay */}
      <AnimatePresence>
        {isLoading && <LoadingOverlay />}
      </AnimatePresence>
    </div>
  );
};

export default NutriTest;
