import { useCallback, useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { NotificationsPanel, NotificationBellButton } from './components/notifications/NotificationsPanel';
import Login from './components/auth/Login';
import CalorieDetailModal from './components/modals/CalorieDetailModal';
import DailyTrackerModal from './components/modals/DailyTrackerModal';
import LogMealModal from './components/modals/LogMealModal';
import WaterCounter from './components/modals/WaterCounter.jsx';
import Calendar from './components/calendar/Calendar';
import { useAuth } from './context/AuthContext';
// import { useDashboard } from './contexts/DashboardContext'; // DEPRECATED: Using DataContext
import { useData } from './context/DataContext.jsx';
import { getTimeAgo } from './utils/timeHelpers';
import { parseMealsPerDay } from './utils/mealsHelpers';
import UpNext from './components/dashboard/UpNext';
import { getDailyCalorieSummary } from './services/calorieApi';
import MealPlanShowcase from './components/mealplan/MealPlanShowcase';
import MealHistory from './components/mealhistory/MealHistory';
import SmartActionStack from './components/dashboard/SmartActionStack';
import MacronutrientsCard from './components/dashboard/MacronutrientsCard';
import { fetchNutritionGoals, fetchDailySummary } from './services/nutritionApi';
import { getDailySummary } from './services/mealsApi';
import { fetchWaterSummary } from './services/waterApi';

import {
  LayoutDashboard,
  ChefHat,
  History,
  Calendar as CalendarIcon,
  Apple,
  Target,
  // Scan,
  BookOpen,
  BarChart3,
  User,
  Droplets,
  Activity,
  Award,
  TrendingUp,
  Zap,
  FlaskConical,
  Clock,
  Lightbulb,
  Plus
} from 'lucide-react';

// Icon configuration
const iconConfig = {
  navigation: {
    dashboard: { icon: LayoutDashboard, label: 'Dashboard' },
    recipes: { icon: ChefHat, label: 'Recipe Generator' },
    mealplans: { icon: ChefHat, label: 'Meal Plans' },
    history: { icon: History, label: 'Meal History' },
    calendar: { icon: CalendarIcon, label: 'Journal' },
    apothecary: { icon: FlaskConical, label: 'Apothecary' }
  },
};

// Service classes
class ApiService {
  constructor() {
    // Use environment variable or default to backend port 8000 with API prefix
    this.baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
  }

  async fetchNutritionData(userId) {
    console.log(`Fetching nutrition data for user: ${userId}`);
    return null;
  }

  async logMeal(mealData) {
    console.log('Logging meal:', mealData);
    return { success: true };
  }
}

class LLMService {
  constructor() {
    this.endpoint = 'https://api.your-llm-provider.com/v1/chat';
  }

  async getChatResponse(message, nutritionContext) {
    console.log('LLM Chat:', message, nutritionContext);
    return { response: 'AI response would go here' };
  }

  async generateRecipe(preferences, ingredients) {
    console.log('Generating recipe for:', preferences, ingredients);
    return { recipe: 'Generated recipe would go here' };
  }
}

// Custom hook
const useNutritionData = (userId) => {
  const [data] = useState(null);
  const [loading] = useState(false);
  const [error] = useState(null);
  return { data, loading, error };
};

// Components
const IconWrapper = ({ iconKey, category = 'navigation', size = 'default', color }) => {
  const sizeMap = {
    small: { width: 16, height: 16 },
    default: { width: 20, height: 20 },
    medium: { width: 24, height: 24 },
    large: { width: 32, height: 32 }
  };

  const iconData = iconConfig[category]?.[iconKey];
  if (!iconData) return null;

  const IconComponent = iconData.icon;
  return <IconComponent {...sizeMap[size]} strokeWidth={2} color={color} />;
};

const Card = ({ children, gradient, style = {} }) => {
  const cardStyle = {
    background: gradient || 'rgba(255, 255, 255, 0.7)',
    backdropFilter: 'blur(10px)',
    WebkitBackdropFilter: 'blur(10px)',
    borderRadius: '24px',
    padding: '32px',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    border: '1px solid rgba(255, 255, 255, 0.3)',
    position: 'relative',
    overflow: 'hidden',
    ...style
  };

  return (
    <motion.div
      style={cardStyle}
      whileHover={{
        scale: 1.02,
        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.15)'
      }}
      transition={{ duration: 0.2 }}
    >
      {children}
    </motion.div>
  );
};

const QuickActionButton = ({ actionKey, action, onClick }) => {
  const [isHovered, setIsHovered] = useState(false);

  const colorMap = {
    green: { bg: '#f0fdf4', hover: '#dcfce7', text: '#16a34a' },
    orange: { bg: '#fff7ed', hover: '#ffedd5', text: '#ea580c' },
    yellow: { bg: '#fefce8', hover: '#fef3c7', text: '#d97706' },
    cyan: { bg: '#ecfeff', hover: '#cffafe', text: '#0891b2' },
    purple: { bg: '#faf5ff', hover: '#f3e8ff', text: '#9333ea' }
  };

  const colors = colorMap[action.color] || colorMap.green;

  const buttonStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '24px',
    borderRadius: '16px',
    background: isHovered ? colors.hover : 'transparent',
    border: `1px solid ${isHovered ? colors.bg : 'transparent'}`,
    cursor: 'pointer',
    transition: 'all 0.2s',
    textDecoration: 'none',
    width: '100%'
  };

  const iconContainerStyle = {
    width: '56px',
    height: '56px',
    background: colors.bg,
    borderRadius: '16px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: '16px',
    transition: 'all 0.2s'
  };

  const labelStyle = {
    fontSize: '14px',
    fontWeight: '600',
    color: '#374151',
    textAlign: 'center',
    lineHeight: '1.25'
  };

  return (
    <button
      style={buttonStyle}
      onClick={() => onClick(actionKey)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div style={iconContainerStyle}>
        <IconWrapper
          iconKey={actionKey}
          category="quickActions"
          size="medium"
        />
      </div>
      <span style={labelStyle}>
        {action.label}
      </span>
    </button>
  );
};

function App() {
  const { user: authUser, loading: authLoading } = useAuth();
  const { summary, isLoading, getLastLoggedMeal, loggedMeals, currentStreak } = useData(); // Migrated from DashboardContext to DataContext
  const location = useLocation();
  const navigate = useNavigate();
  const [isAnimating, setIsAnimating] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const user = authUser || { id: '123', name: 'User' };

  // Get last logged meal for display
  const lastMeal = getLastLoggedMeal();

  // Count today's logged meals (backend already filters to today in logged_meals_today)
  const mealsLoggedCount = loggedMeals?.length || 0;
  const mealsLoggedToday = {
    breakfast: loggedMeals?.some((meal) => (meal?.meal_type || '').toLowerCase() === 'breakfast') || false,
    lunch: loggedMeals?.some((meal) => (meal?.meal_type || '').toLowerCase() === 'lunch') || false,
    dinner: loggedMeals?.some((meal) => (meal?.meal_type || '').toLowerCase() === 'dinner') || false,
  };

  // Get user's meal goal from profile (defaults to 5 if not set)
  const userMealGoal = parseMealsPerDay(authUser?.dietary_preferences?.meals_per_day);
  // NutriTest is now accessible via /nutritest route from Profile page only

  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([]); //Despues va a venir del API
  const [showCalorieModal, setShowCalorieModal] = useState(false);

  // Calculate unread count from notifications array
  const unreadNotifications = notifications.filter(n => !n.isRead).length;
  const [showCalorieCounter, setShowCalorieCounter] = useState(false);
  const [showLogMealModal, setShowLogMealModal] = useState(false);
  const [showWaterCounter, setShowWaterCounter] = useState(false);
  const { data: nutritionData, loading } = useNutritionData(user.id);
  const [hoveredNavButton, setHoveredNavButton] = useState(null);

  // Trigger entrance animation once mounted (avoid state updates before mount)
  useEffect(() => {
    const id = setTimeout(() => setIsAnimating(true), 50);
    return () => clearTimeout(id);
  }, []);

  // Sync active tab from URL (e.g., /?tab=dashboard)
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const tab = params.get('tab');
    const validTabs = Object.keys(iconConfig.navigation);
    if (tab && validTabs.includes(tab)) {
      setActiveTab(tab);
    } else if (location.pathname === '/' && activeTab !== 'dashboard') {
      setActiveTab('dashboard');
    }
  }, [location.search, location.pathname]);

  // Nutrition data state
  const [nutritionDataState, setNutritionDataState] = useState({
    calories: { current: 0, target: 2000, percentage: 0 },
    protein: { current: 0, target: 150, unit: 'g' },
    carbs: { current: 0, target: 250, unit: 'g' },
    fat: { current: 0, target: 67, unit: 'g' },
    water: { current: 0, target: 2000, unit: 'ml' }
  });
  const [isLoadingNutrition, setIsLoadingNutrition] = useState(true);

  // Fetch nutrition data from API
  const fetchNutritionData = useCallback(async () => {
    try {
      setIsLoadingNutrition(true);
      const today = new Date();
      const dateStr = today.toISOString().slice(0, 10);
      const [goals, totals, waterSummary] = await Promise.all([
        fetchNutritionGoals().catch(() => ({ calories: 2000, proteinTarget: 150, carbsTarget: 250, fatTarget: 67 })),
        fetchDailySummary(dateStr).catch(() => ({ calories: 0, protein: 0, carbs: 0, fat: 0 })),
        fetchWaterSummary(dateStr).catch(() => ({ goal_ml: null, total_intake_ml: 0 }))
      ]);

      const percentage = goals.calories > 0 ? Math.min(100, Math.round((totals.calories / goals.calories) * 100)) : 0;
      const waterGoal = typeof waterSummary.goal_ml === 'number' ? waterSummary.goal_ml : 2000;
      const waterCurrent = typeof waterSummary.total_intake_ml === 'number' ? waterSummary.total_intake_ml : 0;
      const waterPercentage = waterGoal > 0 ? Math.min(100, Math.round((waterCurrent / waterGoal) * 100)) : 0;

      const nutritionState = {
        calories: { current: totals.calories, target: goals.calories, percentage },
        protein: { current: totals.protein, target: goals.proteinTarget, unit: 'g' },
        carbs: { current: totals.carbs, target: goals.carbsTarget, unit: 'g' },
        fat: { current: totals.fat, target: goals.fatTarget, unit: 'g' },
        water: {
          current: waterCurrent,
          target: waterGoal,
          unit: 'ml',
          percentage: waterPercentage,
          remaining: waterGoal > 0 ? Math.max(0, waterGoal - waterCurrent) : null,
        }
      };

      setNutritionDataState(nutritionState);

      // Note: DataContext automatically updates via fetchData() - no manual update needed
    } catch (error) {
      console.error('Error fetching nutrition data:', error);
    } finally {
      setIsLoadingNutrition(false);
    }
  }, []);

  // Hydrate dashboard state when user is authenticated
  useEffect(() => {
    if (!authLoading && authUser) {
      fetchNutritionData();
    }
  }, [authLoading, authUser, fetchNutritionData]);

  // NutriTest completion handled in dedicated route component

  const apiService = new ApiService();
  const llmService = new LLMService();
  // Enhanced Progress Ring with hover effects
const ProgressRing = ({ percentage, size = 120, strokeWidth = 10, color = '#22c55e', onClick }) => {
  const [isHovered, setIsHovered] = useState(false);
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;

  // Cap the visual progress at 100% for the ring, but display actual percentage
  const displayPercentage = Math.round(percentage);
  const ringPercentage = Math.min(percentage, 100);
  const offset = circumference - (ringPercentage / 100) * circumference;

  return (
    <motion.button
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      whileHover={{ scale: 1.08 }}
      whileTap={{ scale: 0.95 }}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        background: 'transparent',
        border: 'none',
        cursor: 'pointer',
        padding: 0
      }}
    >
      {/* Outer glow ring when hovered */}
      {isHovered && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          style={{
          position: 'absolute',
          width: size + 16,
          height: size + 16,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${color}15 0%, transparent 70%)`,
          animation: 'pulse 2s infinite'
          }}
        />
      )}

      <svg
        width={size}
        height={size}
        style={{
          transform: 'rotate(-90deg)',
          filter: isHovered ? 'drop-shadow(0 4px 12px rgba(34, 197, 94, 0.4))' : 'none',
          transition: 'filter 0.3s ease'
        }}
      >
        {/* Background circle with gradient */}
        <defs>
          <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#22c55e" />
            <stop offset="100%" stopColor="#16a34a" />
          </linearGradient>
        </defs>

        {/* Background track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#f3f4f6"
          strokeWidth={strokeWidth}
          fill="none"
        />

        {/* Progress circle with gradient - animated */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="url(#progressGradient)"
          strokeWidth={strokeWidth}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{
            duration: 1.5,
            delay: 0.2,
            ease: [0.4, 0, 0.2, 1]
          }}
        />
      </svg>

      {/* Center content */}
      <div style={{
        position: 'absolute',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        transition: 'transform 0.3s ease',
        transform: isHovered ? 'scale(1.1)' : 'scale(1)'
      }}>
        <span style={{
          fontSize: '32px',
          fontWeight: '800',
          background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text'
        }}>
          {displayPercentage}%
        </span>
        {isHovered && (
          <span style={{
            fontSize: '10px',
            color: '#22c55e',
            fontWeight: '600',
            marginTop: '2px',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            EDIT
          </span>
        )}
      </div>
    </motion.button>
  );
};

// Health Tip of the Day Component
const HealthTipOfTheDay = () => {
  const [tip, setTip] = useState(null);
  const [loadingTip, setLoadingTip] = useState(true);
  const [tipError, setTipError] = useState(null);

  useEffect(() => {
    let mounted = true;
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';
    (async () => {
      try {
        setLoadingTip(true);
        setTipError(null);
        const resp = await fetch(`${API_BASE_URL}/tips/today`);
        const data = await resp.json();
        if (!resp.ok) throw new Error(data?.detail || 'Failed to load tip');
        if (mounted) setTip(data);
      } catch (e) {
        if (mounted) setTipError(e?.message || 'Failed to load tip');
      } finally {
        if (mounted) setLoadingTip(false);
      }
    })();
    return () => { mounted = false; };
  }, []);

  const category = tip?.category || 'TIP';
  const text = tip?.text || 'Loading...';

  return (
    <Card>
      <div style={{ position: 'relative' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
          <div style={{
            width: 32,
            height: 32,
            background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Lightbulb width={20} height={20} color="#d97706" />
          </div>
          <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#374151', margin: 0 }}>
            Health Tip of the Day
          </h3>
        </div>

        <div style={{
          background: 'linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)',
          borderRadius: '12px',
          padding: '20px',
          border: '1px solid #fde68a'
        }}>
          <div style={{
            display: 'inline-block',
            padding: '4px 12px',
            background: '#ffffff',
            borderRadius: '6px',
            fontSize: '11px',
            fontWeight: '600',
            color: '#d97706',
            marginBottom: '12px',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            {category}
          </div>

          <p style={{
            fontSize: '14px',
            color: '#374151',
            lineHeight: '1.6',
            margin: 0
          }}>
            {loadingTip ? 'Loading tip...' : (tipError || text)}
          </p>
        </div>
      </div>
    </Card>
  );
};


  const currentNutritionData = nutritionData || nutritionDataState;

  // App is only rendered behind a ProtectedRoute; no local login gate needed

  // Loading guard for DataContext - prevents null summary crashes
  if (isLoading || !summary) {
    return (
      <div style={{
        minHeight: '100vh',
        background: '#f9fafb',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: 48,
            height: 48,
            background: '#f0fdf4',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px',
            animation: 'pulse 2s infinite'
          }}>
            <div style={{
              width: 24,
              height: 24,
              background: '#22c55e',
              borderRadius: '50%'
            }} />
          </div>
          <h3 style={{
            fontSize: '18px',
            fontWeight: '600',
            color: '#1f2937',
            margin: '0 0 8px 0'
          }}>
            Loading Dashboard...
          </h3>
          <p style={{
            fontSize: '14px',
            color: '#6b7280',
            margin: 0
          }}>
            Fetching your nutrition data
          </p>
        </div>
      </div>
    );
  }

  if (loading && !authLoading) {
    return (
      <div style={{
        minHeight: '100vh',
        background: '#f9fafb',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: 48,
            height: 48,
            background: '#f0fdf4',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px'
          }}>
            <Apple width={24} height={24} color="#22c55e" />
          </div>
          <p style={{ color: '#6b7280' }}>Loading your nutrition data...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{
        minHeight: '100vh',
        background: 'var(--color-gray-50)',
        opacity: isAnimating ? 1 : 0,
        transform: isAnimating ? 'translateY(0)' : 'translateY(20px)',
        transition: 'opacity 0.6s ease-out, transform 0.6s ease-out'
      }}>
      {/* Header moved to AppLayout */}
      {/* Main Content */}
      <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '32px 16px' }}>
        {/* Navigation Tabs */}
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '12px',
          marginBottom: '32px',
          background: 'var(--color-gray-100)',
          padding: '12px',
          borderRadius: '16px',
          boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
          border: '2px solid var(--color-gray-200)',
          alignItems: 'center'
        }}>

          {Object.entries(iconConfig.navigation).map(([key, navItem]) => (
            <button
              key={key}
              onClick={() => { setActiveTab(key); navigate(`/?tab=${key}`, { replace: true }); }}
              onMouseEnter={() => setHoveredNavButton(key)}
              onMouseLeave={() => setHoveredNavButton(null)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px 20px',
                borderRadius: '12px',
                fontWeight: '500',
                fontSize: '14px',
                transition: 'all 0.2s',
                border: activeTab === key ? 'none' : '2px solid var(--color-gray-200)',
                cursor: 'pointer',
                background: activeTab === key ? '#22c55e' :
                           hoveredNavButton === key ? 'rgba(34, 197, 94, 0.12)' : 'transparent',
                color: activeTab === key ? '#ffffff' : 'var(--text-secondary)',
                boxShadow: activeTab === key ? '0 10px 15px -3px rgb(34 197 94 / 0.3)' : 'none',
                transform: activeTab === key ?  'scale(1.05)' :
                           hoveredNavButton === key ? 'scale(1.02)' : 'scale(1)'
              }}
            >
              <IconWrapper
                iconKey={key}
                category="navigation"
                size="small"
                color={activeTab === key ? '#ffffff' : undefined}
              />
              <span>{navItem.label}</span>
            </button>
          ))}
        </div>

        {/* Dashboard Content */}
        {activeTab === 'dashboard' && (
          <motion.div
            initial="hidden"
            animate="visible"
            variants={{
              hidden: { opacity: 0 },
              visible: {
                opacity: 1,
                transition: {
                  staggerChildren: 0.1,
                  delayChildren: 0.1
                }
              }
            }}
            style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}
          >
            {/* Stats Grid */}
            <motion.div
              variants={{
                hidden: { opacity: 0, y: 20 },
                visible: { opacity: 1, y: 0 }
              }}
              style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: '24px'
              }}
            >
              {/* Calories Card Column - Stacked vertically */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                {/* Daily Calories Card */}
                <Card>
                  <div style={{ position: 'relative' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                      <div style={{
                        width: 32,
                        height: 32,
                        background: '#f0fdf4',
                        borderRadius: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <Zap width={20} height={20} color="#22c55e" />
                      </div>
                      <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#374151', margin: 0 }}>
                        Daily Calories
                      </h3>
                    </div>

                    {/* Progress Ring */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
                      <div>
                        <ProgressRing
                          percentage={summary.daily_goal > 0 ? (summary.total_consumed / summary.daily_goal) * 100 : 0}
                          size={120}
                          strokeWidth={10}
                          color={summary.total_consumed > summary.daily_goal ? "#ef4444" : "#22c55e"}
                          onClick={() => setShowCalorieCounter(true)}
                        />
                      </div>
                      <div>
                        <p style={{ color: '#6b7280', margin: 0 }}>
                          Goal: {summary.daily_goal} kcal — Consumed: {summary.total_consumed} kcal
                        </p>
                        <p style={{
                          color: summary.remaining < 0 ? '#ef4444' : '#22c55e',
                          margin: '4px 0 0 0',
                          fontWeight: '600'
                        }}>
                          Remaining: {summary.remaining} kcal
                        </p>
                        <div style={{ height: 8 }} />
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => setShowLogMealModal(true)}
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '8px',
                            padding: '12px 20px',
                            background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
                            border: 'none',
                            borderRadius: '12px',
                            fontSize: '14px',
                            fontWeight: '700',
                            color: '#ffffff',
                            cursor: 'pointer'
                          }}
                        >
                          <Plus width={18} height={18} />
                          <span>Log Meal</span>
                        </motion.button>
                      </div>
                    </div>
                  </div>
                </Card>

                {/* Calorie Deficit Card - Coming Soon */}
                <Card>
                  <div style={{ position: 'relative' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                      <div style={{
                        width: 32,
                        height: 32,
                        background: '#fef3c7',
                        borderRadius: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <TrendingUp width={20} height={20} color="#f59e0b" />
                      </div>
                      <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#374151', margin: 0 }}>
                        Calorie Deficit
                      </h3>
                    </div>

                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      padding: '20px 16px',
                      background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
                      borderRadius: '12px',
                      border: '2px dashed #f59e0b'
                    }}>
                      <div style={{ textAlign: 'center' }}>
                        <p style={{
                          fontSize: '14px',
                          fontWeight: '600',
                          color: '#92400e',
                          margin: '0 0 4px 0'
                        }}>
                          Coming Soon...
                        </p>
                        <p style={{
                          fontSize: '12px',
                          color: '#a16207',
                          margin: 0,
                          opacity: 0.8
                        }}>
                          Track your calorie deficit goals
                        </p>
                      </div>
                    </div>
                  </div>
                </Card>
              </div>

              {/* Macronutrients Card */}
              <MacronutrientsCard
                macros={summary?.macros}
                isLoading={isLoading}
              />

              {/* Today's Activity Card */}
              <Card>
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
                      <Activity width={20} height={20} color="#22c55e" />
                    </div>
                    <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#374151', margin: 0 }}>
                      Today's Activity
                    </h3>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                    {/* Meals Logged - Interactive */}
                    <div
                      onClick={() => setShowCalorieCounter(true)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '16px',
                        background: '#f9fafb',
                        borderRadius: '12px',
                        cursor: 'pointer',
                        transition: 'all 0.2s',
                        position: 'relative'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = '#f3f4f6';
                        e.currentTarget.style.transform = 'translateY(-2px)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = '#f9fafb';
                        e.currentTarget.style.transform = 'translateY(0)';
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1 }}>
                        <div style={{
                          width: 40,
                          height: 40,
                          background: '#fff7ed',
                          borderRadius: '10px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}>
                          <Apple width={20} height={20} color="#ea580c" />
                        </div>
                        <div style={{ flex: 1 }}>
                          <div style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
                            Meals Logged
                          </div>
                          <div style={{ fontSize: '12px', color: '#6b7280' }}>
                            {mealsLoggedCount} of {userMealGoal} meals
                          </div>
                          {lastMeal && (
                            <div style={{
                              fontSize: '11px',
                              color: '#9ca3af',
                              marginTop: '2px',
                              fontStyle: 'italic'
                            }}>
                              {lastMeal.name} • {getTimeAgo(lastMeal.created_at || lastMeal.logged_at)}
                            </div>
                          )}
                        </div>
                      </div>
                      <div style={{ fontSize: '24px', fontWeight: '700', color: '#111827' }}>
                        {mealsLoggedCount}
                      </div>

                      {/* Hover tooltip indicator */}
                      <div style={{
                        position: 'absolute',
                        top: '8px',
                        right: '8px',
                        fontSize: '10px',
                        color: '#9ca3af',
                        opacity: 0.6
                      }}>
                        Click to log
                      </div>
                    </div>

                    <div
                      onClick={() => setShowWaterCounter(true)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '16px',
                        background: '#ecfeff',
                        borderRadius: '12px',
                        cursor: 'pointer',
                        position: 'relative',
                        transition: 'all 0.2s'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = '#d9f8ff';
                        e.currentTarget.style.transform = 'translateY(-2px)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = '#ecfeff';
                        e.currentTarget.style.transform = 'translateY(0)';
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1 }}>
                        <div style={{
                          width: 40,
                          height: 40,
                          background: '#ffffff',
                          borderRadius: '10px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}>
                          <Droplets width={20} height={20} color="#0891b2" />
                        </div>
                        <div>
                          <div style={{ fontSize: '14px', fontWeight: '600', color: '#0f172a' }}>Water Intake</div>
                          <div style={{ fontSize: '12px', color: '#0f172a', opacity: 0.65 }}>
                            Goal: {currentNutritionData.water.target ?? 2000} ml
                          </div>
                          {typeof currentNutritionData.water.remaining === 'number' && (
                            <div style={{ fontSize: '11px', color: '#0891b2', marginTop: 2 }}>
                              Remaining: {currentNutritionData.water.remaining} ml
                            </div>
                          )}
                        </div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '20px', fontWeight: '700', color: '#0f172a' }}>
                          {currentNutritionData.water.current}
                          <span style={{ fontSize: '14px', color: '#0f172a', opacity: 0.6, fontWeight: '500' }}> ml</span>
                        </div>
                        <div style={{ fontSize: '11px', color: '#0891b2', fontWeight: 600 }}>
                          {currentNutritionData.water.percentage ?? 0}% of goal
                        </div>
                      </div>
                      <div style={{
                        position: 'absolute',
                        top: '8px',
                        right: '8px',
                        fontSize: '10px',
                        color: '#0f172a',
                        opacity: 0.6
                      }}>
                        Click to log
                      </div>
                    </div>

                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '16px',
                      background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
                      borderRadius: '12px'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{
                          width: 40,
                          height: 40,
                          background: '#ffffff',
                          borderRadius: '10px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}>
                          <Award width={20} height={20} color="#d97706" />
                        </div>
                        <div>
                          <div style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>Streak</div>
                          <div style={{ fontSize: '12px', color: '#78716c' }}>Keep it going!</div>
                        </div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '28px', fontWeight: '700', color: '#111827' }}>{currentStreak}</div>
                        <div style={{ fontSize: '12px', color: '#78716c', fontWeight: '500' }}>days</div>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            </motion.div>

            {/* Up Next and Health Tip Section */}
            <motion.div
              variants={{
                hidden: { opacity: 0, y: 20 },
                visible: { opacity: 1, y: 0 }
              }}
              style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
              gap: '24px'
              }}
            >
              <SmartActionStack
                mealsLoggedToday={mealsLoggedToday}
                onAction={(actionId) => {
                  if (actionId === 'breakfast' || actionId === 'lunch' || actionId === 'dinner') {
                    setShowLogMealModal(true);
                  }
                  if (actionId === 'water') {
                    setShowWaterCounter(true);
                  }
                }}
              />
              <HealthTipOfTheDay />
            </motion.div>
          </motion.div>
        )}

        {activeTab === 'apothecary' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}
          >
            <ApothecaryPage />
          </motion.div>
        )}

        {activeTab === 'calendar' && (
          <Calendar />
        )}

        {activeTab === 'mealplans' && (
          <MealPlanShowcase />
        )}

        {activeTab === 'history' && (
          <MealHistory />
        )}

        {activeTab !== 'dashboard' && activeTab !== 'nutritest' && activeTab !== 'calendar' && activeTab !== 'mealplans' && activeTab !== 'history' && (
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{
                width: 80,
                height: 80,
                background: '#f0fdf4',
                borderRadius: '50%',
                margin: '0 auto 24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <IconWrapper
                  iconKey={activeTab}
                  category="navigation"
                  size="large"
                />
              </div>
              <h2 style={{ fontSize: '24px', fontWeight: '700', color: '#374151', marginBottom: '16px', margin: '0 0 16px 0' }}>
                {iconConfig.navigation[activeTab]?.label || 'Feature Coming Soon'}
              </h2>
              <p style={{ color: '#6b7280', margin: 0 }}>This feature will be implemented with proper API integration.</p>
            </div>
          </Card>
        )}
      </div>

      <NotificationsPanel
        isOpen={showNotifications}
        onClose={() => setShowNotifications(false)}
        user={user}
      />

      <CalorieDetailModal
        isOpen={showCalorieModal}
        onClose={() => setShowCalorieModal(false)}
        calorieData={currentNutritionData.calories}
      />

      <DailyTrackerModal
        isOpen={showCalorieCounter}
        onClose={() => setShowCalorieCounter(false)}
      />
      <LogMealModal
        isOpen={showLogMealModal}
        onClose={() => setShowLogMealModal(false)}
        onSaved={fetchNutritionData}
      />
      <WaterCounter
        isOpen={showWaterCounter}
        onClose={() => setShowWaterCounter(false)}
        onDataUpdate={fetchNutritionData}
      />
      </div>
  );
}

export default App;