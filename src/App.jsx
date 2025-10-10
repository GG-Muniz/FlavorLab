import { useState } from 'react';
import { NotificationsPanel, NotificationBellButton } from './components/notifications/NotificationsPanel';
import Login from './components/auth/Login';
import NutriTest from './components/onboarding/NutriTest';
import CalorieDetailModal from './components/modals/CalorieDetailModal';
import CalorieCounter from './components/modals/CalorieCounter';
import Calendar from './components/calendar/Calendar';

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
  Lightbulb
} from 'lucide-react';

// Icon configuration
const iconConfig = {
  navigation: {
    dashboard: { icon: LayoutDashboard, label: 'Dashboard' },
    nutritest: { icon: FlaskConical, label: 'NutriTest' },
    recipes: { icon: ChefHat, label: 'Recipe Generator' },
    history: { icon: History, label: 'Meal History' },
    calendar: { icon: CalendarIcon, label: 'Calendar' }
  },
  quickActions: {
    mealData: { icon: Apple, label: 'Meal Data', color: 'orange' },
    dietGoals: { icon: Target, label: 'Diet Goals', color: 'yellow' },
    // barcodeScanner: { icon: Scan, label: 'Barcode Scanner', color: 'cyan' },
    ingredientDatabase: { icon: BookOpen, label: 'Ingredient Database', color: 'green' },
    foodLog: { icon: BarChart3, label: 'Food Log', color: 'purple' }
  }
};

// Service classes
class ApiService {
  constructor() {
    this.baseURL = 'http://localhost:3001';
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
const IconWrapper = ({ iconKey, category = 'navigation', size = 'default' }) => {
  const sizeMap = {
    small: { width: 16, height: 16 },
    default: { width: 20, height: 20 },
    medium: { width: 24, height: 24 },
    large: { width: 32, height: 32 }
  };

  const iconData = iconConfig[category]?.[iconKey];
  if (!iconData) return null;

  const IconComponent = iconData.icon;
  return <IconComponent {...sizeMap[size]} strokeWidth={2} />;
};

const Card = ({ children, gradient, style = {} }) => {
  const cardStyle = {
    background: gradient || '#ffffff',
    borderRadius: '24px',
    padding: '32px',
    boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
    border: '1px solid #f3f4f6',
    position: 'relative',
    overflow: 'hidden',
    transition: 'box-shadow 0.3s ease',
    ...style
  };

  return (
    <div
      style={cardStyle}
      onMouseOver={(e) => {
        e.currentTarget.style.boxShadow = '0 4px 6px -1px rgb(0 0 0 / 0.1)';
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.boxShadow = '0 1px 3px 0 rgb(0 0 0 / 0.1)';
      }}
    >
      {children}
    </div>
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
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [user] = useState({ id: '123', name: 'Sarah' });
  const [hasCompletedNutriTest, setHasCompletedNutriTest] = useState(false);

  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([]); //Despues va a venir del API
  const [showCalorieModal, setShowCalorieModal] = useState(false);
  const [showQuickActionsMenu, setShowQuickActionsMenu] = useState(false);

  // Calculate unread count from notifications array
  const unreadNotifications = notifications.filter(n => !n.isRead).length;
  const [showCalorieCounter, setShowCalorieCounter] = useState(false);
  const { data: nutritionData, loading } = useNutritionData(user.id);
  const [hoveredNavButton, setHoveredNavButton] = useState(null);

  // Handle login
  const handleLogin = () => {
    setIsLoggedIn(true);
    // Trigger entrance animation - small delay to ensure DOM is ready
    setTimeout(() => setIsAnimating(true), 50);
    // TODO: Store authentication token/session
    // TODO: Fetch user data from backend
    // TODO: Check from backend if user has completed NutriTest
  };

  // Handle NutriTest completion
  const handleNutriTestComplete = (testResults) => {
    console.log('NutriTest completed:', testResults);
    setHasCompletedNutriTest(true);
    // TODO: Send results to backend to create user profile and meal plan
    // Switch back to dashboard
    setActiveTab('dashboard');
  };
  const mockNutritionData = {
    calories: { current: 1247, target: 2000, percentage: 62 },
    protein: { current: 45, target: 150, unit: 'g' },
    carbs: { current: 156, target: 250, unit: 'g' },
    fat: { current: 42, target: 67, unit: 'g' },
    water: { current: 1200, target: 2000, unit: 'ml' }
  };

  const apiService = new ApiService();
  const llmService = new LLMService();
  // Enhanced Progress Ring with hover effects
const ProgressRing = ({ percentage, size = 120, strokeWidth = 10, color = '#22c55e', onClick }) => {
  const [isHovered, setIsHovered] = useState(false);
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        background: 'transparent',
        border: 'none',
        cursor: 'pointer',
        padding: 0,
        transition: 'transform 0.3s ease',
        transform: isHovered ? 'scale(1.08)' : 'scale(1)'
      }}
    >
      {/* Outer glow ring when hovered */}
      {isHovered && (
        <div style={{
          position: 'absolute',
          width: size + 16,
          height: size + 16,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${color}15 0%, transparent 70%)`,
          animation: 'pulse 2s infinite'
        }} />
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

        {/* Progress circle with gradient */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="url(#progressGradient)"
          strokeWidth={strokeWidth}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{
            transition: 'stroke-dashoffset 0.6s cubic-bezier(0.4, 0, 0.2, 1)'
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
          {percentage}%
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
    </button>
  );
};

// Upcoming Events Widget Component
const UpcomingEventsWidget = () => {
  // Mock upcoming events data
  const upcomingEvents = [
    {
      id: 1,
      title: 'Lunch with Team',
      time: 'Today, 1:00 PM',
      type: 'meal',
      color: '#ea580c'
    },
    {
      id: 2,
      title: 'Evening Workout',
      time: 'Today, 6:30 PM',
      type: 'activity',
      color: '#8b5cf6'
    },
    {
      id: 3,
      title: 'Meal Prep Sunday',
      time: 'Tomorrow, 10:00 AM',
      type: 'meal',
      color: '#22c55e'
    },
    {
      id: 4,
      title: 'Nutrition Consultation',
      time: 'Friday, 3:00 PM',
      type: 'appointment',
      color: '#0891b2'
    }
  ];

  return (
    <Card>
      <div style={{ position: 'relative' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: 32,
              height: 32,
              background: '#f0fdf4',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <CalendarIcon width={20} height={20} color="#22c55e" />
            </div>
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#374151', margin: 0 }}>
              Upcoming Events
            </h3>
          </div>
          <button
            onClick={() => {}}
            style={{
              padding: '6px 12px',
              background: '#f0fdf4',
              border: '1px solid #bbf7d0',
              borderRadius: '8px',
              fontSize: '12px',
              fontWeight: '600',
              color: '#16a34a',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#dcfce7';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = '#f0fdf4';
            }}
          >
            View Calendar
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {upcomingEvents.map((event) => (
            <div
              key={event.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                padding: '16px',
                background: '#f9fafb',
                borderRadius: '12px',
                transition: 'all 0.2s',
                cursor: 'pointer',
                border: '1px solid transparent'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#f3f4f6';
                e.currentTarget.style.borderColor = '#e5e7eb';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = '#f9fafb';
                e.currentTarget.style.borderColor = 'transparent';
              }}
            >
              <div style={{
                width: 4,
                height: 48,
                background: event.color,
                borderRadius: '2px',
                marginRight: '16px'
              }}></div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '14px', fontWeight: '600', color: '#111827', marginBottom: '4px' }}>
                  {event.title}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Clock width={14} height={14} color="#6b7280" />
                  <span style={{ fontSize: '12px', color: '#6b7280' }}>{event.time}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Empty state - show when no events */}
        {upcomingEvents.length === 0 && (
          <div style={{
            textAlign: 'center',
            padding: '32px',
            color: '#9ca3af'
          }}>
            <CalendarIcon width={48} height={48} color="#d1d5db" style={{ margin: '0 auto 12px' }} />
            <p style={{ fontSize: '14px', margin: 0 }}>No upcoming events</p>
          </div>
        )}
      </div>
    </Card>
  );
};

// Health Tip of the Day Component
const HealthTipOfTheDay = () => {
  // Mock health tip - will be based on user's health goals from API
  const healthTip = {
    title: "Stay Hydrated",
    tip: "Drinking water before meals can help reduce appetite and support weight loss. Aim for at least 8 glasses throughout the day.",
    category: "Hydration"
  };

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
            {healthTip.category}
          </div>

          <h4 style={{
            fontSize: '16px',
            fontWeight: '700',
            color: '#111827',
            margin: '0 0 12px 0'
          }}>
            {healthTip.title}
          </h4>

          <p style={{
            fontSize: '14px',
            color: '#374151',
            lineHeight: '1.6',
            margin: 0
          }}>
            {healthTip.tip}
          </p>
        </div>

        <div style={{
          marginTop: '16px',
          textAlign: 'center'
        }}>
          <button
            style={{
              padding: '8px 16px',
              background: 'transparent',
              border: '1px solid #fde68a',
              borderRadius: '8px',
              fontSize: '12px',
              fontWeight: '600',
              color: '#d97706',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#fef3c7';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent';
            }}
          >
            View All Tips
          </button>
        </div>
      </div>
    </Card>
  );
};

  const handleActionClick = async (actionKey) => {
    console.log('Action clicked:', actionKey);

    // Close the menu
    setShowQuickActionsMenu(false);

    // Handle specific actions
    if (actionKey === 'calorieCounter') {
      setShowCalorieCounter(true);
    }

    // TODO: Add handlers for other quick actions
    // Service integration would go here
  };

  const currentNutritionData = nutritionData || mockNutritionData;

  // Show login page if not logged in
  if (!isLoggedIn) {
    return <Login onLogin={handleLogin} />;
  }

  if (loading) {
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
      background: '#f9fafb',
      opacity: isAnimating ? 1 : 0,
      transform: isAnimating ? 'translateY(0)' : 'translateY(20px)',
      transition: 'opacity 0.6s ease-out, transform 0.6s ease-out'
    }}>
      {/* Header */}
      <header style={{
        background: '#ffffff',
        boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
        borderBottom: '1px solid #f3f4f6'
      }}>
        <div style={{
          maxWidth: '80rem',
          margin: '0 auto',
          padding: '0 16px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          height: '64px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: 40,
              height: 40,
              background: '#22c55e',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)'
            }}>
              <Apple width={24} height={24} color="#ffffff" strokeWidth={2.5} />
            </div>

            <h1 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#111827',
              letterSpacing: '-0.025em',
              margin: 0
            }}>
              HealthLab
            </h1>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <NotificationBellButton
            unreadCount={unreadNotifications}
            onClick={() => setShowNotifications(!showNotifications)}
         />
            <div style={{ fontSize: '14px', color: '#6b7280' }}>
              Hello, <span style={{ fontWeight: '600', color: '#374151' }}>{user.name}</span>
              <span style={{ marginLeft: '4px' }}>👋</span>
            </div>
            <div style={{
              width: 36,
              height: 36,
              background: '#f0fdf4',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '2px solid #bbf7d0'
            }}>
              <User width={20} height={20} color="#15803d" />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '32px 16px' }}>
        {/* Navigation Tabs */}
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '12px',
          marginBottom: '32px',
          background: '#ffffff',
          padding: '12px',
          borderRadius: '16px',
          boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
          border: '1px solid #f3f4f6',
          alignItems: 'center'
        }}>

          {Object.entries(iconConfig.navigation).map(([key, navItem]) => (
            <button
              key={key}
              onClick={() => setActiveTab(key)}
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
                border: 'none',
                cursor: 'pointer',
                background: activeTab === key ? '#22c55e' :
                           hoveredNavButton === key ? '#f0fdf4' : 'transparent',
                color: activeTab === key ? '#ffffff' : '#6b7280',
                boxShadow: activeTab === key ? '0 10px 15px -3px rgb(34 197 94 / 0.3)' : 'none',
                transform: activeTab === key ?  'scale(1.05)' :
                           hoveredNavButton === key ? 'scale(1.02' : 'scale(1)'
              }}
            >
              <IconWrapper
                iconKey={key}
                category="navigation"
                size="small"
              />
              <span>{navItem.label}</span>
            </button>
          ))}

          {/* Quick Actions Dropdown Button */}
          <div style={{ position: 'relative', marginLeft: 'auto' }}>
            <button
              onClick={() => setShowQuickActionsMenu(!showQuickActionsMenu)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px 20px',
                background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
                color: '#ffffff',
                border: 'none',
                borderRadius: '12px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                boxShadow: '0 4px 6px -1px rgb(34 197 94 / 0.3)',
                transition: 'all 0.2s'
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
              <Zap width={16} height={16} />
              <span>Quick Actions</span>
            </button>

            {/* Dropdown Menu */}
            {showQuickActionsMenu && (
              <>
                {/* Backdrop to close menu when clicking outside */}
                <div
                  onClick={() => setShowQuickActionsMenu(false)}
                  style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    zIndex: 10
                  }}
                />

                {/* Dropdown Content */}
                <div style={{
                  position: 'absolute',
                  top: 'calc(100% + 8px)',
                  right: 0,
                  minWidth: '320px',
                  background: '#ffffff',
                  borderRadius: '16px',
                  boxShadow: '0 10px 25px -5px rgb(0 0 0 / 0.2)',
                  border: '1px solid #f3f4f6',
                  padding: '8px',
                  zIndex: 20,
                  animation: 'slideDown 0.2s ease-out'
                }}>
                  <style>
                    {`
                      @keyframes slideDown {
                        from {
                          opacity: 0;
                          transform: translateY(-8px);
                        }
                        to {
                          opacity: 1;
                          transform: translateY(0);
                        }
                      }
                    `}
                  </style>

                  {Object.entries(iconConfig.quickActions).map(([key, action]) => {
                    const IconComponent = action.icon;
                    const colorMap = {
                      green: { bg: '#f0fdf4', hover: '#dcfce7', text: '#16a34a' },
                      orange: { bg: '#fff7ed', hover: '#ffedd5', text: '#ea580c' },
                      yellow: { bg: '#fefce8', hover: '#fef3c7', text: '#d97706' },
                      cyan: { bg: '#ecfeff', hover: '#cffafe', text: '#0891b2' },
                      purple: { bg: '#faf5ff', hover: '#f3e8ff', text: '#9333ea' }
                    };
                    const colors = colorMap[action.color] || colorMap.green;

                    return (
                      <button
                        key={key}
                        onClick={() => handleActionClick(key)}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '12px',
                          width: '100%',
                          padding: '12px 16px',
                          background: 'transparent',
                          border: 'none',
                          borderRadius: '12px',
                          cursor: 'pointer',
                          transition: 'all 0.2s',
                          textAlign: 'left'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.background = colors.hover;
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.background = 'transparent';
                        }}
                      >
                        <div style={{
                          width: '40px',
                          height: '40px',
                          background: colors.bg,
                          borderRadius: '10px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          flexShrink: 0
                        }}>
                          <IconComponent width={20} height={20} color={colors.text} />
                        </div>
                        <span style={{
                          fontSize: '14px',
                          fontWeight: '600',
                          color: '#374151'
                        }}>
                          {action.label}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </>
            )}
          </div>
        </div>

        {/* Auto-show NutriTest for new users */}
        {activeTab === 'dashboard' && !hasCompletedNutriTest && (
          <div style={{
            background: '#ffffff',
            borderRadius: '24px',
            padding: '32px',
            boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
            border: '1px solid #f3f4f6',
            marginBottom: '32px'
          }}>
            <NutriTest onComplete={handleNutriTestComplete} />
          </div>
        )}

        {/* Dashboard Content */}
        {activeTab === 'dashboard' && hasCompletedNutriTest && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
            {/* Stats Grid */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: '24px'
            }}>
            {/* Calories Card - REPLACE YOUR EXISTING ONE WITH THIS */}
            <Card>
              <div style={{
                position: 'absolute',
                top: 0,
                right: 0,
                width: 80,
                height: 80,
                background: '#f0fdf4',
                borderRadius: '50%',
                transform: 'translate(32px, -32px)'
              }}></div>
              <div style={{ position: 'relative' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '32px' }}>
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

                {/* Centered content with progress ring and info below */}
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '24px' }}>
                  {/* Progress Ring */}
                  <ProgressRing
                    percentage={currentNutritionData.calories.percentage}
                    size={120}
                    strokeWidth={10}
                    color="#22c55e"
                    onClick={() => setShowCalorieCounter(true)}
                  />

                  {/* Info below the wheel */}
                  <div style={{ textAlign: 'center', width: '100%' }}>
                    <p style={{
                      fontSize: '14px',
                      color: '#6b7280',
                      fontWeight: '500',
                      margin: '0 0 8px 0'
                    }}>
                      Goal: {currentNutritionData.calories.target} kcal
                    </p>
                    <div style={{
                      padding: '8px 12px',
                      background: '#f0fdf4',
                      borderRadius: '8px',
                      border: '1px solid #bbf7d0',
                      display: 'inline-block'
                    }}>
                      <p style={{
                        fontSize: '12px',
                        color: '#16a34a',
                        fontWeight: '600',
                        margin: 0
                      }}>
                        {currentNutritionData.calories.target - currentNutritionData.calories.current} kcal remaining
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </Card>

              {/* Macronutrients Card */}
              <Card>
                <div style={{
                  position: 'absolute',
                  top: 0,
                  right: 0,
                  width: 80,
                  height: 80,
                  background: '#f0fdf4',
                  borderRadius: '50%',
                  transform: 'translate(32px, -32px)'
                }}></div>
                <div style={{ position: 'relative' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '32px' }}>
                    <div style={{
                      width: 32,
                      height: 32,
                      background: '#f0fdf4',
                      borderRadius: '8px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      <Target width={20} height={20} color="#22c55e" />
                    </div>
                    <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#374151', margin: 0 }}>
                      Macronutrients
                    </h3>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
                    {/* Protein */}
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <span style={{ fontSize: '14.7px', fontWeight: '600', color: '#374151' }}>Protein</span>
                        <span style={{ fontSize: '14.7px', fontWeight: '600', color: '#6b7280' }}>
                          {currentNutritionData.protein.current}g / {currentNutritionData.protein.target}g
                        </span>
                      </div>
                      <div style={{ display: 'flex', gap: '4px', height: '8px' }}>
                        {Array.from({ length: 10 }).map((_, i) => {
                          const filled = i < Math.floor((currentNutritionData.protein.current / currentNutritionData.protein.target) * 10);
                          return (
                            <div
                              key={i}
                              style={{
                                flex: 1,
                                background: filled ? '#ef4444' : '#f3f4f6',
                                borderRadius: '4px',
                                transition: 'background 0.3s ease'
                              }}
                            />
                          );
                        })}
                      </div>
                    </div>

                    {/* Carbs */}
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <span style={{ fontSize: '14.7px', fontWeight: '600', color: '#374151' }}>Carbs</span>
                        <span style={{ fontSize: '14.7px', fontWeight: '600', color: '#6b7280' }}>
                          {currentNutritionData.carbs.current}g / {currentNutritionData.carbs.target}g
                        </span>
                      </div>
                      <div style={{ display: 'flex', gap: '4px', height: '8px' }}>
                        {Array.from({ length: 10 }).map((_, i) => {
                          const filled = i < Math.floor((currentNutritionData.carbs.current / currentNutritionData.carbs.target) * 10);
                          return (
                            <div
                              key={i}
                              style={{
                                flex: 1,
                                background: filled ? '#fbbf24' : '#f3f4f6',
                                borderRadius: '4px',
                                transition: 'background 0.3s ease'
                              }}
                            />
                          );
                        })}
                      </div>
                    </div>

                    {/* Fat */}
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <span style={{ fontSize: '14.7px', fontWeight: '600', color: '#374151' }}>Fat</span>
                        <span style={{ fontSize: '14.7px', fontWeight: '600', color: '#6b7280' }}>
                          {currentNutritionData.fat.current}g / {currentNutritionData.fat.target}g
                        </span>
                      </div>
                      <div style={{ display: 'flex', gap: '4px', height: '8px' }}>
                        {Array.from({ length: 10 }).map((_, i) => {
                          const filled = i < Math.floor((currentNutritionData.fat.current / currentNutritionData.fat.target) * 10);
                          return (
                            <div
                              key={i}
                              style={{
                                flex: 1,
                                background: filled ? '#8b5cf6' : '#f3f4f6',
                                borderRadius: '4px',
                                transition: 'background 0.3s ease'
                              }}
                            />
                          );
                        })}
                      </div>
                    </div>
                  </div>
                </div>
              </Card>

              {/* Today's Activity Card */}
              <Card>
                <div style={{
                  position: 'absolute',
                  top: 0,
                  right: 0,
                  width: 80,
                  height: 80,
                  background: '#f0fdf4',
                  borderRadius: '50%',
                  transform: 'translate(32px, -32px)'
                }}></div>
                <div style={{ position: 'relative' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '32px' }}>
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
                    {/* Meals */}
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '16px',
                      background: '#f9fafb',
                      borderRadius: '12px'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
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
                        <div>
                          <div style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>Meals Logged</div>
                          <div style={{ fontSize: '12px', color: '#6b7280' }}>3 of 5 meals</div>
                        </div>
                      </div>
                      <div style={{ fontSize: '24px', fontWeight: '700', color: '#111827' }}>3</div>
                    </div>

                    {/* Water */}
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '16px',
                      background: '#f9fafb',
                      borderRadius: '12px'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{
                          width: 40,
                          height: 40,
                          background: '#ecfeff',
                          borderRadius: '10px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}>
                          <Droplets width={20} height={20} color="#0891b2" />
                        </div>
                        <div>
                          <div style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>Water Intake</div>
                          <div style={{ fontSize: '12px', color: '#6b7280' }}>Goal: 2000ml</div>
                        </div>
                      </div>
                      <div style={{ fontSize: '20px', fontWeight: '700', color: '#111827' }}>
                        {currentNutritionData.water.current}
                        <span style={{ fontSize: '14px', color: '#6b7280', fontWeight: '500' }}>ml</span>
                      </div>
                    </div>

                    {/* Streak */}
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
                        <div style={{ fontSize: '28px', fontWeight: '700', color: '#111827' }}>7</div>
                        <div style={{ fontSize: '12px', color: '#78716c', fontWeight: '500' }}>days</div>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            </div>

            {/* Calendar Events and Health Tip Section */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
              gap: '24px'
            }}>
              <UpcomingEventsWidget />
              <HealthTipOfTheDay />
            </div>

          </div>
        )}

        {/* NutriTest Tab */}
        {activeTab === 'nutritest' && (
          <div style={{
            background: '#ffffff',
            borderRadius: '24px',
            padding: '32px',
            boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
            border: '1px solid #f3f4f6'
          }}>
            <NutriTest onComplete={handleNutriTestComplete} />
          </div>
        )}

        {/* Calendar */}
        {activeTab === 'calendar' && (
          <Calendar />
        )}

        {/* Other Tabs */}
        {activeTab !== 'dashboard' && activeTab !== 'nutritest' && activeTab !== 'calendar' && (
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
      {/* Notifications Panel */}
      <NotificationsPanel
        isOpen={showNotifications}
        onClose={() => setShowNotifications(false)}
        user={user}
      />

      {/* Calorie Detail Modal */}
      <CalorieDetailModal
        isOpen={showCalorieModal}
        onClose={() => setShowCalorieModal(false)}
        calorieData={currentNutritionData.calories}
      />

      {/* Calorie Counter Modal */}
      <CalorieCounter
        isOpen={showCalorieCounter}
        onClose={() => setShowCalorieCounter(false)}
      />
    </div>
  );
}

export default App;