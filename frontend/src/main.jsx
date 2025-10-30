import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import './index.css'
import App from './App.jsx'
import Login from './components/auth/Login.jsx'
import SignUp from './components/auth/SignUp.jsx'
import ForgotPassword from './components/auth/ForgotPassword.jsx'
import ResetPassword from './components/auth/ResetPassword.jsx'
import { AuthProvider, useAuth } from './context/AuthContext.jsx'
// import { DashboardProvider } from './contexts/DashboardContext.jsx' // DEPRECATED
import { DataProvider } from './context/DataContext.jsx'
import OnboardingWizard from './components/onboarding/OnboardingWizard.jsx'
import ProfilePage from './components/profile/ProfilePage.jsx'
import AppLayout from './components/layout/AppLayout.jsx'
import SettingsPage from './pages/SettingsPage.jsx'
import HelpPage from './pages/HelpPage.jsx'
import DisplayPage from './pages/DisplayPage.jsx'
import IngredientBrowserPage from './pages/IngredientBrowserPage.jsx'
import IngredientDetailPage from './pages/IngredientDetailPage.jsx'
import ApothecaryPage from './pages/ApothecaryPage.jsx'
import { ThemeProvider } from './context/ThemeContext.jsx'
import NutriTest from './components/onboarding/NutriTest.jsx'

function ProtectedRoute({ children }) {
  const { token, loading } = useAuth();
  if (loading) return <div style={{minHeight:'100vh',display:'flex',alignItems:'center',justifyContent:'center'}}>Loading...</div>;
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

function DebugHome() {
  return (
    <div style={{minHeight:'100vh',display:'flex',flexDirection:'column'}}>
      <div style={{padding:16,background:'#e5e7eb'}}>Debug Home: shell rendered</div>
      <div style={{flex:1,display:'flex',alignItems:'center',justifyContent:'center'}}>Content area</div>
    </div>
  );
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ThemeProvider>
      <AuthProvider>
        <DataProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<Login onLogin={() => {}} />} />
              <Route path="/signup" element={<SignUp />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password" element={<ResetPassword />} />

              <Route path="/" element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
                <Route index element={<App />} />
                <Route path="onboarding" element={<OnboardingWizard />} />
                <Route path="profile" element={<ProfilePage />} />
                <Route path="nutritest" element={<NutriTest />} />
                <Route path="settings" element={<SettingsPage />} />
                <Route path="help" element={<HelpPage />} />
                <Route path="display" element={<DisplayPage />} />
                <Route path="ingredients" element={<IngredientBrowserPage />} />
                <Route path="ingredients/:ingredientId" element={<IngredientDetailPage />} />
                <Route path="apothecary" element={<ApothecaryPage />} />
              </Route>

              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </BrowserRouter>
        </DataProvider>
      </AuthProvider>
    </ThemeProvider>
  </StrictMode>,
)
