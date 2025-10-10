
import React, { useState } from 'react';
import { Calendar, Target, BarChart3, Clock, Utensils, History, QrCode, Apple, Database, Calculator, User, Heart, ChefHat, TrendingUp } from 'lucide-react';

const NutritionDashboard = () => {
  const [activeTab, setActiveTab] = useState('dashboard');

  // Explanation: I'm using useState to manage which tab is currently active
  // This is a fundamental React pattern for managing component state

  const nutritionData = {
    calories: { current: 1247, target: 2000, percentage: 62 },
    protein: { current: 45, target: 150, unit: 'g' },
    carbs: { current: 156, target: 250, unit: 'g' },
    fat: { current: 42, target: 67, unit: 'g' },
    water: { current: 1200, target: 2000, unit: 'ml' }
  };

  // Explanation: I'm storing nutrition data in an object structure
  // This makes it easy to access and update values consistently

  const quickActions = [
    { icon: Calculator, label: 'Calorie Counter', color: 'bg-green-100 text-green-700' },
    { icon: Apple, label: 'Meal Data', color: 'bg-orange-100 text-orange-700' },
    { icon: Target, label: 'Diet Goals', color: 'bg-yellow-100 text-yellow-700' },
    { icon: QrCode, label: 'Barcode Scanner', color: 'bg-cyan-100 text-cyan-700' },
    { icon: Database, label: 'Recipe Database', color: 'bg-green-100 text-green-700' },
    { icon: ChefHat, label: 'Recipe & Calorie', color: 'bg-orange-100 text-orange-700' },
    { icon: User, label: 'User Registration', color: 'bg-yellow-100 text-yellow-700' },
    { icon: Heart, label: 'Wearable Devices', color: 'bg-cyan-100 text-cyan-700' },
    { icon: Utensils, label: 'Food Log', color: 'bg-green-100 text-green-700' },
    { icon: TrendingUp, label: 'Data Dashboard', color: 'bg-orange-100 text-orange-700' }
  ];

  // Explanation: I'm creating an array of objects for quick actions
  // Each object contains an icon component, label, and color classes
  // This approach makes the code more maintainable and reusable

  const CircularProgress = ({ percentage, color, size = 120 }) => {
    // Explanation: This is a reusable component for circular progress indicators
    // I'm using SVG to create custom circular progress bars
    // The circumference calculation (2 * π * r) determines the circle's perimeter

    const radius = (size - 20) / 2;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (percentage / 100) * circumference;

    return (
      <div className="relative" style={{ width: size, height: size }}>
        <svg className="transform -rotate-90" width={size} height={size}>
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            className="text-gray-200"
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className={color}
            style={{ transition: 'stroke-dashoffset 0.5s ease-in-out' }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl font-bold text-gray-800">{percentage}%</span>
        </div>
      </div>
    );
  };

  const NutrientBar = ({ label, current, target, unit, color }) => {
    // Explanation: Another reusable component for horizontal progress bars
    // I'm calculating percentage and using it to set the width of the progress bar

    const percentage = Math.min((current / target) * 100, 100);

    return (
      <div className="bg-white rounded-lg p-4 shadow-sm">
        <div className="flex justify-between items-center mb-2">
          <span className="font-medium text-gray-700">{label}</span>
          <span className="text-sm text-gray-500">{current}/{target}{unit}</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className={`${color} h-3 rounded-full transition-all duration-500 ease-out`}
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
      </div>
    );
  };

  const TabButton = ({ id, label, icon: Icon, isActive, onClick }) => {
    // Explanation: Tab component with conditional styling
    // I'm using template literals to conditionally apply CSS classes based on active state

    return (
      <button
        onClick={() => onClick(id)}
        className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
          isActive
            ? 'bg-green-500 text-white shadow-md'
            : 'text-gray-600 hover:bg-green-50 hover:text-green-600'
        }`}
      >
        <Icon size={20} />
        <span className="font-medium">{label}</span>
      </button>
    );
  };

  const DashboardContent = () => (
    <div className="space-y-6">
      {/* Main Nutrition Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Calories Circle */}
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Daily Calories</h3>
          <div className="flex items-center justify-center">
            <CircularProgress
              percentage={nutritionData.calories.percentage}
              color="text-green-500"
            />
          </div>
          <div className="text-center mt-4">
            <p className="text-2xl font-bold text-gray-800">
              {nutritionData.calories.current}
            </p>
            <p className="text-sm text-gray-500">of {nutritionData.calories.target} kcal</p>
          </div>
        </div>

        {/* Today's Summary */}
        <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Today's Summary</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Meals logged</span>
              <span className="font-semibold text-orange-600">3/5</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Water intake</span>
              <span className="font-semibold text-cyan-600">1.2L</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Exercise</span>
              <span className="font-semibold text-green-600">45 min</span>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="bg-gradient-to-br from-cyan-50 to-cyan-100 rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Stats</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Streak</span>
              <div className="flex items-center space-x-1">
                <span className="font-bold text-yellow-600">7</span>
                <span className="text-sm text-gray-500">days</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Goal Progress</span>
              <span className="font-semibold text-green-600">86%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Macronutrients */}
      <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-xl p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Macronutrients</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <NutrientBar
            label="Protein"
            current={nutritionData.protein.current}
            target={nutritionData.protein.target}
            unit={nutritionData.protein.unit}
            color="bg-green-500"
          />
          <NutrientBar
            label="Carbs"
            current={nutritionData.carbs.current}
            target={nutritionData.carbs.target}
            unit={nutritionData.carbs.unit}
            color="bg-orange-500"
          />
          <NutrientBar
            label="Fat"
            current={nutritionData.fat.current}
            target={nutritionData.fat.target}
            unit={nutritionData.fat.unit}
            color="bg-yellow-500"
          />
          <NutrientBar
            label="Water"
            current={nutritionData.water.current}
            target={nutritionData.water.target}
            unit={nutritionData.water.unit}
            color="bg-cyan-500"
          />
        </div>
      </div>

      {/* Quick Actions Grid */}
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {quickActions.map((action, index) => (
            <button
              key={index}
              className="flex flex-col items-center p-4 rounded-lg hover:shadow-md transition-shadow"
            >
              <div className={`${action.color} p-3 rounded-full mb-2`}>
                <action.icon size={24} />
              </div>
              <span className="text-sm font-medium text-gray-700 text-center">
                {action.label}
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                <Apple className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-bold text-gray-900">NutriTrack</h1>
            </div>

            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                Hello, <span className="font-semibold">Sarah</span> 👋
              </div>
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-green-600" />
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Navigation Tabs */}
        <div className="flex flex-wrap gap-2 mb-8 bg-white p-2 rounded-xl shadow-sm">
          <TabButton
            id="dashboard"
            label="Dashboard"
            icon={BarChart3}
            isActive={activeTab === 'dashboard'}
            onClick={setActiveTab}
          />
          <TabButton
            id="recipes"
            label="Recipe Generator"
            icon={ChefHat}
            isActive={activeTab === 'recipes'}
            onClick={setActiveTab}
          />
          <TabButton
            id="history"
            label="Meal History"
            icon={History}
            isActive={activeTab === 'history'}
            onClick={setActiveTab}
          />
          <TabButton
            id="calendar"
            label="Calendar"
            icon={Calendar}
            isActive={activeTab === 'calendar'}
            onClick={setActiveTab}
          />
        </div>

        {/* Content */}
        {activeTab === 'dashboard' && <DashboardContent />}

        {activeTab === 'recipes' && (
          <div className="bg-white rounded-xl p-8 shadow-sm text-center">
            <ChefHat className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Recipe Generator</h2>
            <p className="text-gray-600">Generate personalized recipes based on your dietary preferences and available ingredients.</p>
          </div>
        )}

        {activeTab === 'history' && (
          <div className="bg-white rounded-xl p-8 shadow-sm text-center">
            <History className="w-16 h-16 text-orange-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Meal History</h2>
            <p className="text-gray-600">View your complete meal history and track your nutritional progress over time.</p>
          </div>
        )}

        {activeTab === 'calendar' && (
          <div className="bg-white rounded-xl p-8 shadow-sm text-center">
            <Calendar className="w-16 h-16 text-cyan-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Calendar View</h2>
            <p className="text-gray-600">Plan your meals and track your nutrition goals across different days and weeks.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default NutritionDashboard;
