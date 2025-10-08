# FlavorLab API Integration Plan - 2 Week Implementation

> **Goal:** Connect backend APIs to frontend components to replace all mock data with real, database-driven information.

**Timeline:** 2 Weeks (10 working days)
**Approach:** Incremental integration by feature priority
**Status:** Planning Phase

---

## 📊 Current State Analysis

### Existing Mock Data in Frontend

| Component | Mock Data | Location | Priority |
|-----------|-----------|----------|----------|
| **Authentication** | Hardcoded user | App.jsx:208 | 🔴 Critical |
| **Nutrition Data** | mockNutritionData | App.jsx:226-232 | 🔴 Critical |
| **Notifications** | Empty array | App.jsx:211 | 🟡 High |
| **Calorie Counter** | Local state only | CalorieCounter.jsx | 🟡 High |
| **Calendar Events** | Component local | Calendar.jsx | 🟢 Medium |
| **NutriTest Results** | Component local | NutriTest.jsx | 🟢 Medium |

### Existing Service Stubs

```javascript
// App.jsx:53-67
class ApiService {
  baseURL = 'http://localhost:3001'
  - fetchNutritionData() // Returns null
  - logMeal()            // Returns mock success
}

// App.jsx:69-83
class LLMService {
  endpoint = 'https://api.your-llm-provider.com/v1/chat'
  - getChatResponse()    // Returns placeholder
  - generateRecipe()     // Returns placeholder
}
```

---

## 🎯 Integration Strategy

### Core Principles

1. **Incremental Integration** - One feature at a time, test thoroughly
2. **Backwards Compatibility** - Keep mock data as fallback during development
3. **Error Handling First** - Build robust error states before success paths
4. **Single Source of Truth** - All data flows through centralized API service
5. **Type Safety** - Document expected data shapes for each endpoint

### Architecture Decision

**✅ Recommended: REST API with Service Layer Pattern**

```
Frontend Components
       ↓
Custom Hooks (useAuth, useNutrition, etc.)
       ↓
Service Classes (ApiService, LLMService)
       ↓
Axios/Fetch Layer
       ↓
Backend REST API
```

**Why this approach?**
- Clear separation of concerns
- Easy to test and mock
- Can swap backend without touching components
- Already started in codebase

---

## 📅 2-Week Sprint Plan

### Week 1: Core Data & Authentication (Days 1-5)

#### **Day 1: Foundation Setup**

**Backend Tasks:**
- [ ] Set up Express.js server structure
- [ ] Configure PostgreSQL/MongoDB connection
- [ ] Set up CORS and middleware
- [ ] Create base API error handling

**Frontend Tasks:**
- [ ] Install `axios` for HTTP requests
- [ ] Create centralized API configuration
- [ ] Set up environment variables (.env)
- [ ] Create error handling utilities

**Deliverable:** Backend server running, frontend can ping `/health` endpoint

---

#### **Day 2: Authentication System** 🔴 Critical

**Backend Endpoints:**
```javascript
POST   /api/auth/register     // Create new user account
POST   /api/auth/login        // Login and get JWT token
POST   /api/auth/logout       // Invalidate token
GET    /api/auth/me           // Get current user info
```

**Database Schema:**
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**Frontend Integration:**
- [ ] Implement ApiService.login()
- [ ] Implement ApiService.register()
- [ ] Implement ApiService.getCurrentUser()
- [ ] Store JWT in localStorage
- [ ] Create authentication context
- [ ] Update Login.jsx to use real API
- [ ] Add loading states and error messages

**Code Changes:**
```javascript
// src/services/api.service.js
class ApiService {
  async login(email, password) {
    const response = await axios.post(`${this.baseURL}/api/auth/login`, {
      email, password
    });
    localStorage.setItem('token', response.data.token);
    return response.data.user;
  }

  async getCurrentUser() {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${this.baseURL}/api/auth/me`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  }
}
```

**Testing Checklist:**
- [ ] Can register new account
- [ ] Can login with correct credentials
- [ ] Error shows for wrong password
- [ ] Token persists on page refresh
- [ ] Logout clears token

**Deliverable:** Full authentication flow working

---

#### **Day 3: User Nutrition Goals & Profile** 🔴 Critical

**Backend Endpoints:**
```javascript
GET    /api/users/:userId/nutrition-goals  // Get user's calorie/macro goals
PUT    /api/users/:userId/nutrition-goals  // Update goals
GET    /api/users/:userId/profile          // Get user profile
PUT    /api/users/:userId/profile          // Update profile
```

**Database Schema:**
```sql
CREATE TABLE user_nutrition_goals (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  calorie_target INT NOT NULL,
  protein_target INT,
  carbs_target INT,
  fat_target INT,
  water_target INT DEFAULT 2000,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**Frontend Integration:**
- [ ] Create `useNutritionGoals` custom hook
- [ ] Replace mockNutritionData with API call
- [ ] Update Dashboard cards to show real data
- [ ] Add loading skeleton states
- [ ] Handle case where user hasn't set goals yet

**Code Changes:**
```javascript
// src/hooks/useNutritionGoals.js
export const useNutritionGoals = (userId) => {
  const [goals, setGoals] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchGoals = async () => {
      try {
        const data = await apiService.getNutritionGoals(userId);
        setGoals(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchGoals();
  }, [userId]);

  return { goals, loading, error };
};

// In App.jsx - Replace line 226-232
const { goals: nutritionGoals, loading: goalsLoading } = useNutritionGoals(user.id);
```

**Testing Checklist:**
- [ ] Dashboard shows real user goals
- [ ] Loading state displays properly
- [ ] Can update goals and see changes
- [ ] Error message if API fails

**Deliverable:** Real user nutrition data on dashboard

---

#### **Day 4: Daily Nutrition Tracking** 🔴 Critical

**Backend Endpoints:**
```javascript
GET    /api/nutrition/:userId/daily         // Get today's nutrition summary
GET    /api/nutrition/:userId/history       // Get past days (with date range)
POST   /api/meals/log                       // Log a meal
GET    /api/meals/:userId/today             // Get all meals logged today
DELETE /api/meals/:mealId                   // Delete a logged meal
```

**Database Schema:**
```sql
CREATE TABLE meals (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  name VARCHAR(255) NOT NULL,
  calories INT NOT NULL,
  protein INT,
  carbs INT,
  fat INT,
  meal_type VARCHAR(50), -- breakfast, lunch, dinner, snack
  logged_at TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW()
);

-- For efficient daily aggregation
CREATE INDEX idx_meals_user_date ON meals(user_id, DATE(logged_at));
```

**Frontend Integration:**
- [ ] Implement CalorieCounter.jsx save to API
- [ ] Update Dashboard to show today's totals
- [ ] Create real-time progress updates
- [ ] Add meal history view

**Code Changes:**
```javascript
// src/services/api.service.js
async logMeal(userId, mealData) {
  const response = await axios.post(`${this.baseURL}/api/meals/log`, {
    userId,
    ...mealData,
    logged_at: new Date().toISOString()
  }, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
  });
  return response.data;
}

async getTodayNutrition(userId) {
  const response = await axios.get(
    `${this.baseURL}/api/nutrition/${userId}/daily`,
    { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }}
  );
  return response.data;
}

// In CalorieCounter.jsx:30
const handleAddIntake = async () => {
  if (calorieIntake && mealName) {
    const newIntake = {
      meal: mealName,
      calories: Number(calorieIntake),
      timestamp: new Date().toISOString()
    };

    try {
      // Save to API instead of just local state
      await apiService.logMeal(user.id, newIntake);
      setIntakeHistory([...intakeHistory, newIntake]);
      setCalorieIntake('');
      setMealName('');
    } catch (error) {
      console.error('Failed to log meal:', error);
      // Show error message to user
    }
  }
};
```

**Testing Checklist:**
- [ ] Can log meals and see them immediately
- [ ] Dashboard progress updates in real-time
- [ ] Calories remaining calculates correctly
- [ ] Meal data persists on page refresh

**Deliverable:** Full calorie tracking with persistent data

---

#### **Day 5: Notifications System** 🟡 High

**Backend Endpoints:**
```javascript
GET    /api/notifications/:userId           // Get all notifications
POST   /api/notifications/:userId           // Create notification (system)
PUT    /api/notifications/:notifId/read     // Mark as read
DELETE /api/notifications/:notifId          // Delete notification
```

**Database Schema:**
```sql
CREATE TABLE notifications (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  type VARCHAR(50) NOT NULL,  -- meal_reminder, nutrition_summary, achievement
  title VARCHAR(255) NOT NULL,
  message TEXT NOT NULL,
  is_read BOOLEAN DEFAULT false,
  icon VARCHAR(50),
  color VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_notifications_user_unread ON notifications(user_id, is_read);
```

**Frontend Integration:**
- [ ] Fetch notifications on login
- [ ] Update NotificationsPanel to use API
- [ ] Implement delete functionality
- [ ] Implement mark as read functionality
- [ ] Add real-time badge count

**Code Changes:**
```javascript
// In App.jsx - Add useEffect after line 218
useEffect(() => {
  const fetchNotifications = async () => {
    if (!isLoggedIn) return;

    try {
      const data = await apiService.getNotifications(user.id);
      setNotifications(data);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  };

  fetchNotifications();

  // Optional: Poll for new notifications every 30 seconds
  const interval = setInterval(fetchNotifications, 30000);
  return () => clearInterval(interval);
}, [isLoggedIn, user.id]);

// In NotificationsPanel.jsx - Update deleteNotification
const deleteNotification = async (notificationId) => {
  try {
    await apiService.deleteNotification(notificationId);
    setNotifications(prev =>
      prev.filter(notif => notif.id !== notificationId)
    );
  } catch (error) {
    console.error('Failed to delete notification:', error);
  }
};
```

**Testing Checklist:**
- [ ] Notifications load on login
- [ ] Badge shows correct unread count
- [ ] Can delete notifications
- [ ] Can mark as read
- [ ] UI updates immediately

**Deliverable:** Live notification system

---

### Week 2: Advanced Features & Polish (Days 6-10)

#### **Day 6: Calendar & Meal Planning** 🟢 Medium

**Backend Endpoints:**
```javascript
GET    /api/meal-plans/:userId              // Get meal plans by date range
POST   /api/meal-plans                      // Create meal plan
PUT    /api/meal-plans/:planId              // Update meal plan
DELETE /api/meal-plans/:planId              // Delete meal plan
```

**Database Schema:**
```sql
CREATE TABLE meal_plans (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  title VARCHAR(255),
  planned_date DATE NOT NULL,
  meal_type VARCHAR(50),
  calories INT,
  notes TEXT,
  completed BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_meal_plans_user_date ON meal_plans(user_id, planned_date);
```

**Frontend Integration:**
- [ ] Connect Calendar.jsx to API
- [ ] Display planned meals on calendar
- [ ] Add/edit meal plans
- [ ] Mark plans as completed

**Deliverable:** Interactive meal planning calendar

---

#### **Day 7: NutriTest Integration** 🟢 Medium

**Backend Endpoints:**
```javascript
POST   /api/nutritest/submit                // Submit quiz answers
GET    /api/nutritest/:userId/results       // Get user's quiz results
PUT    /api/users/:userId/preferences       // Update dietary preferences
```

**Database Schema:**
```sql
CREATE TABLE nutritest_results (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  activity_level VARCHAR(50),
  dietary_preference VARCHAR(50),
  health_goals TEXT[],
  allergies TEXT[],
  recommended_calories INT,
  recommended_protein INT,
  recommended_carbs INT,
  recommended_fat INT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**Frontend Integration:**
- [ ] Save NutriTest results to database
- [ ] Use results to set initial nutrition goals
- [ ] Show results history

**Deliverable:** Persistent NutriTest results

---

#### **Day 8: LLM Integration (Recipe Generator & AI Chat)** 🟡 High

**Backend Endpoints:**
```javascript
POST   /api/llm/chat                        // Send message to AI nutritionist
POST   /api/llm/generate-recipe             // Generate recipe with AI
GET    /api/recipes/:userId/saved           // Get user's saved recipes
POST   /api/recipes/save                    // Save a recipe
```

**Backend Implementation:**
```javascript
// Use OpenAI, Claude, or custom LLM
async generateRecipe(req, res) {
  const { preferences, ingredients, nutritionGoals } = req.body;

  const prompt = `Generate a healthy recipe with these requirements:
    - Dietary preferences: ${preferences}
    - Available ingredients: ${ingredients}
    - Target calories: ${nutritionGoals.calories}
    - Must be high in protein

    Return JSON with: name, ingredients, instructions, nutrition facts`;

  const response = await openai.chat.completions.create({
    model: "gpt-4",
    messages: [{ role: "user", content: prompt }],
    response_format: { type: "json_object" }
  });

  return res.json(response.choices[0].message.content);
}
```

**Frontend Integration:**
- [ ] Connect LLMService to actual API
- [ ] Add loading states for AI requests
- [ ] Display generated recipes
- [ ] Save favorite recipes

**Deliverable:** Working AI recipe generation

---

#### **Day 9: Data Aggregation & Analytics** 🟢 Medium

**Backend Endpoints:**
```javascript
GET    /api/analytics/:userId/weekly        // Weekly nutrition summary
GET    /api/analytics/:userId/monthly       // Monthly trends
GET    /api/analytics/:userId/streaks       // Track daily logging streaks
```

**Database Queries:**
```sql
-- Weekly calorie trend
SELECT
  DATE(logged_at) as date,
  SUM(calories) as total_calories,
  SUM(protein) as total_protein
FROM meals
WHERE user_id = $1
  AND logged_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(logged_at)
ORDER BY date;

-- Streak calculation
SELECT
  COUNT(DISTINCT DATE(logged_at)) as streak_days
FROM meals
WHERE user_id = $1
  AND logged_at >= (
    SELECT MAX(date) FROM (
      SELECT DATE(logged_at) as date,
             LAG(DATE(logged_at)) OVER (ORDER BY DATE(logged_at)) as prev_date
      FROM meals
      WHERE user_id = $1
    ) WHERE date - prev_date > 1
  );
```

**Frontend Integration:**
- [ ] Add charts for weekly trends
- [ ] Show streak achievements
- [ ] Display goal progress over time

**Deliverable:** Analytics dashboard with charts

---

#### **Day 10: Testing, Error Handling & Polish** ✅ Final

**Focus Areas:**

1. **Error States** - Every API call has proper error handling
2. **Loading States** - Skeletons/spinners for all async operations
3. **Empty States** - Messages when no data exists
4. **Offline Handling** - Graceful degradation when API is down
5. **Token Refresh** - Handle expired JWT tokens
6. **Data Validation** - Client-side validation before API calls

**Testing Checklist:**
- [ ] All features work end-to-end
- [ ] Error messages are user-friendly
- [ ] No console errors
- [ ] Loading states appear properly
- [ ] Data persists across sessions
- [ ] Mobile responsive (if applicable)

**Code Review:**
- [ ] Remove all console.logs
- [ ] Update TODO comments
- [ ] Document API endpoints
- [ ] Add JSDoc comments to functions

**Deliverable:** Production-ready application

---

## 🛠️ Technical Implementation Details

### 1. Environment Configuration

**Backend `.env`:**
```bash
PORT=3001
DATABASE_URL=postgresql://user:password@localhost:5432/flavorlab
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_EXPIRY=7d
OPENAI_API_KEY=sk-your-openai-key
NODE_ENV=development
CORS_ORIGIN=http://localhost:5173
```

**Frontend `.env`:**
```bash
VITE_API_BASE_URL=http://localhost:3001
VITE_ENV=development
```

---

### 2. Centralized API Service (Enhanced)

**File: `src/services/api.service.js`**
```javascript
import axios from 'axios';

class ApiService {
  constructor() {
    this.baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001';
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      }
    });

    // Add auth token to every request
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Handle token expiration
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // ========== AUTH ==========
  async login(email, password) {
    const response = await this.client.post('/api/auth/login', { email, password });
    localStorage.setItem('token', response.data.token);
    return response.data.user;
  }

  async register(userData) {
    const response = await this.client.post('/api/auth/register', userData);
    localStorage.setItem('token', response.data.token);
    return response.data.user;
  }

  async logout() {
    localStorage.removeItem('token');
    return this.client.post('/api/auth/logout');
  }

  async getCurrentUser() {
    const response = await this.client.get('/api/auth/me');
    return response.data;
  }

  // ========== NUTRITION ==========
  async getNutritionGoals(userId) {
    const response = await this.client.get(`/api/users/${userId}/nutrition-goals`);
    return response.data;
  }

  async updateNutritionGoals(userId, goals) {
    const response = await this.client.put(`/api/users/${userId}/nutrition-goals`, goals);
    return response.data;
  }

  async getTodayNutrition(userId) {
    const response = await this.client.get(`/api/nutrition/${userId}/daily`);
    return response.data;
  }

  // ========== MEALS ==========
  async logMeal(userId, mealData) {
    const response = await this.client.post('/api/meals/log', {
      userId,
      ...mealData
    });
    return response.data;
  }

  async getTodayMeals(userId) {
    const response = await this.client.get(`/api/meals/${userId}/today`);
    return response.data;
  }

  async deleteMeal(mealId) {
    const response = await this.client.delete(`/api/meals/${mealId}`);
    return response.data;
  }

  // ========== NOTIFICATIONS ==========
  async getNotifications(userId) {
    const response = await this.client.get(`/api/notifications/${userId}`);
    return response.data;
  }

  async markNotificationRead(notificationId) {
    const response = await this.client.put(`/api/notifications/${notificationId}/read`);
    return response.data;
  }

  async deleteNotification(notificationId) {
    const response = await this.client.delete(`/api/notifications/${notificationId}`);
    return response.data;
  }

  // ========== MEAL PLANS ==========
  async getMealPlans(userId, startDate, endDate) {
    const response = await this.client.get(`/api/meal-plans/${userId}`, {
      params: { startDate, endDate }
    });
    return response.data;
  }

  async createMealPlan(planData) {
    const response = await this.client.post('/api/meal-plans', planData);
    return response.data;
  }

  async updateMealPlan(planId, updates) {
    const response = await this.client.put(`/api/meal-plans/${planId}`, updates);
    return response.data;
  }

  async deleteMealPlan(planId) {
    const response = await this.client.delete(`/api/meal-plans/${planId}`);
    return response.data;
  }

  // ========== LLM ==========
  async getChatResponse(message, context) {
    const response = await this.client.post('/api/llm/chat', {
      message,
      context
    });
    return response.data;
  }

  async generateRecipe(preferences, ingredients, nutritionGoals) {
    const response = await this.client.post('/api/llm/generate-recipe', {
      preferences,
      ingredients,
      nutritionGoals
    });
    return response.data;
  }

  // ========== ANALYTICS ==========
  async getWeeklyAnalytics(userId) {
    const response = await this.client.get(`/api/analytics/${userId}/weekly`);
    return response.data;
  }

  async getStreakData(userId) {
    const response = await this.client.get(`/api/analytics/${userId}/streaks`);
    return response.data;
  }
}

export default new ApiService();
```

---

### 3. Custom Hooks Pattern

**File: `src/hooks/useAuth.js`**
```javascript
import { useState, useEffect, createContext, useContext } from 'react';
import apiService from '../services/api.service';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on mount
    const initAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const userData = await apiService.getCurrentUser();
          setUser(userData);
        } catch (error) {
          localStorage.removeItem('token');
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    const userData = await apiService.login(email, password);
    setUser(userData);
    return userData;
  };

  const logout = async () => {
    await apiService.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

**Usage in App.jsx:**
```javascript
import { AuthProvider, useAuth } from './hooks/useAuth';

function AppContent() {
  const { user, loading, logout } = useAuth();

  if (loading) return <div>Loading...</div>;
  if (!user) return <Login />;

  return <Dashboard user={user} onLogout={logout} />;
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
```

---

### 4. Error Handling Pattern

**File: `src/utils/errorHandler.js`**
```javascript
export const handleApiError = (error, fallbackMessage = 'Something went wrong') => {
  if (error.response) {
    // Server responded with error status
    return error.response.data.message || fallbackMessage;
  } else if (error.request) {
    // Request made but no response
    return 'Cannot connect to server. Please check your internet connection.';
  } else {
    // Something else happened
    return error.message || fallbackMessage;
  }
};

export const showErrorToast = (error) => {
  const message = handleApiError(error);
  // Replace with your toast library
  console.error(message);
  alert(message); // Temporary - replace with proper toast
};
```

**Usage:**
```javascript
try {
  await apiService.logMeal(userId, mealData);
} catch (error) {
  showErrorToast(error);
}
```

---

## 📦 Required Dependencies

**Install on Day 1:**
```bash
# Frontend
npm install axios

# Backend
npm install express cors dotenv bcryptjs jsonwebtoken
npm install pg        # If using PostgreSQL
npm install mongoose  # If using MongoDB
npm install openai    # For LLM features
```

---

## 🧪 Testing Strategy

### Daily Testing Routine

After each feature implementation:

1. **Manual Testing**
   - Test happy path (everything works)
   - Test error cases (wrong input, network failure)
   - Test edge cases (empty data, very long strings)

2. **Data Validation**
   - Check database records are created correctly
   - Verify data types match schema
   - Check for SQL injection vulnerabilities

3. **Performance Testing**
   - API responds in < 500ms
   - No unnecessary re-renders
   - Proper loading states

### End-of-Week Integration Test

**Test Scenarios:**
```
1. New User Journey
   - Register account
   - Take NutriTest
   - Set nutrition goals
   - Log first meal
   - Check dashboard updates
   - Receive notification

2. Returning User Journey
   - Login
   - View yesterday's data
   - Log today's meals
   - Plan tomorrow's meals
   - Generate recipe with AI
   - View weekly analytics

3. Error Scenarios
   - Login with wrong password
   - Try to access data without token
   - Submit invalid meal data
   - Lose internet connection mid-operation
```

---

## 🚨 Risk Mitigation

### Potential Blockers & Solutions

| Risk | Probability | Solution |
|------|-------------|----------|
| Database schema changes | High | Use migrations from day 1 |
| API rate limits (LLM) | Medium | Implement caching & queue |
| Frontend state sync issues | Medium | Use React Query or SWR |
| Authentication bugs | High | Test thoroughly on Day 2 |
| CORS errors | High | Configure properly on Day 1 |
| Time zone issues | Medium | Store all dates in UTC |

### Fallback Plan

If behind schedule by Day 5:
1. Skip LLM integration (Day 8) - keep as mock
2. Skip analytics (Day 9) - implement later
3. Focus on core loop: Auth → Nutrition → Meals → Notifications

---

## 📈 Success Metrics

**Definition of Done:**

✅ All mock data replaced with API calls
✅ User can create account and login
✅ Dashboard shows real user data
✅ Meals persist in database
✅ Notifications work
✅ No critical bugs
✅ App works offline gracefully (shows cached data)

**Performance Targets:**
- Initial page load < 2 seconds
- API calls < 500ms
- No visible lag when logging meals

---

## 📚 Documentation Requirements

### Update These Files

1. **README.md** - Add API documentation
2. **REACT-CHEATSHEET.md** - Add API integration patterns
3. **API-DOCS.md** (new) - Full endpoint documentation
4. **.env.example** (new) - Template for environment variables

### API Documentation Template

```markdown
## POST /api/meals/log

Log a meal for the current user.

**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "userId": "uuid",
  "name": "Grilled Chicken Salad",
  "calories": 450,
  "protein": 35,
  "carbs": 20,
  "fat": 18,
  "meal_type": "lunch"
}
```

**Response:** 201 Created
```json
{
  "id": "meal-uuid",
  "message": "Meal logged successfully"
}
```

**Error Responses:**
- 401: Unauthorized (missing/invalid token)
- 400: Bad Request (invalid data)
- 500: Server Error
```

---

## 🎓 Learning Resources

Since this is your first major integration:

1. **REST API Basics** - [MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/HTTP)
2. **JWT Authentication** - [jwt.io](https://jwt.io/introduction)
3. **React Data Fetching** - [React Docs](https://react.dev/learn/synchronizing-with-effects)
4. **Error Handling** - [Axios Error Handling](https://axios-http.com/docs/handling_errors)

---

## 🤝 Daily Standup Template

Use this to track progress:

```
Day X: [Feature Name]

✅ Completed:
- [List what you finished]

🚧 In Progress:
- [What you're working on now]

⏸️ Blocked:
- [Any issues preventing progress]

📝 Notes:
- [Learnings, questions, observations]

⏰ Tomorrow:
- [What you plan to tackle next]
```

---

## 📞 Support & Questions

**If you get stuck:**
1. Check browser console for error messages
2. Check backend logs for API errors
3. Use Postman/Insomnia to test API directly
4. Review this document for code examples
5. Ask for help (include error message + what you tried)

---

**Last Updated:** 2025-10-03
**Status:** Ready to Begin
**Next Step:** Day 1 - Foundation Setup

Good luck! You've got this! 🚀
