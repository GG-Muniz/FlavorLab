import React, { createContext, useState, useContext } from 'react';

const DashboardContext = createContext();

export const useDashboard = () => {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error('useDashboard must be used within a DashboardProvider');
  }
  return context;
};

export const DashboardProvider = ({ children }) => {
  const [summary, setSummary] = useState({
    daily_goal: 0,
    total_consumed: 0,
    remaining: 0,
    logged_meals_today: [],
  });

  // This is the function we will call from our components to update the dashboard state
  const updateSummary = (newSummaryData) => {
    setSummary(newSummaryData);
  };

  const value = { summary, updateSummary };

  return (
    <DashboardContext.Provider value={value}>
      {children}
    </DashboardContext.Provider>
  );
};
