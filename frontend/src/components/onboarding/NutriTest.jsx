import { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import HealthPillarsSelector from './HealthPillarsSelector';
import PreferencesSelector from './PreferencesSelector';
import FinalPreferences from './FinalPreferences';
import LoadingOverlay from './LoadingOverlay';
import './NutriTest.css';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { submitSurvey } from '../../services/mealPlanApi';

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
  const handleComplete = async (skipNavigation = false) => {
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
      if (onComplete) onComplete(payload, { skipNavigation });
      // Only navigate to profile if not skipping navigation (for meal plan generation flow)
      if (!skipNavigation) {
        navigate('/profile', { state: { defaultTab: 'goals' } });
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Handle generate plan with loading state
  const handleGeneratePlan = async () => {
    setIsLoading(true);
    try {
      await submitSurvey(formData);
      // Skip the profile navigation by passing true
      await handleComplete(true);
      // Navigate directly to meal plans tab and trigger auto-generation
      navigate('/app?tab=mealplans', {
        replace: true,
        state: { autoGenerateMealPlan: true }
      });
    } catch (error) {
      console.error('Error submitting survey:', error);
      alert(`Failed to submit survey: ${error?.message || 'Unknown error'}`);
    } finally {
      setIsLoading(false);
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
