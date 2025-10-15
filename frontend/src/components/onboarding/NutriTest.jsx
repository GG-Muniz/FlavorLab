import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import HealthPillarsSelector from './HealthPillarsSelector';
import PreferencesSelector from './PreferencesSelector';
import FinalPreferences from './FinalPreferences';
import LoadingOverlay from './LoadingOverlay';
import { submitSurvey } from '../../services/mealPlanApi';

const NutriTest = ({ onComplete }) => {
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
  const handleComplete = () => {
    console.log('NutriTest completed with data:', formData);
    if (onComplete) {
      onComplete(formData);
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
      setIsLoading(false);
      handleComplete();
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
    <div style={{ position: 'relative', minHeight: '100vh' }}>
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
