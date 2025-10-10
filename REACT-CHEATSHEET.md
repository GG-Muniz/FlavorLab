# FlavorLab React Code Patterns - Cheat Sheet

> A reference guide for common React patterns, JavaScript concepts, and coding practices used in the FlavorLab project.

---

## Table of Contents
1. [React Hooks](#react-hooks)
2. [Array Methods](#array-methods)
3. [Conditional Rendering](#conditional-rendering)
4. [Event Handlers](#event-handlers)
5. [State Management Patterns](#state-management-patterns)
6. [Component Patterns](#component-patterns)
7. [Object Destructuring & Access](#object-destructuring--access)
8. [Inline Styling](#inline-styling)
9. [Service Classes](#service-classes)
10. [Custom Hooks](#custom-hooks)

---

## React Hooks

### `useState` - Managing Component State

**What it does:** Creates a state variable that persists between renders and triggers re-render when changed.

**Syntax:**
```javascript
const [stateValue, setStateValue] = useState(initialValue);
```

**Usage Examples:**

```javascript
// Simple state (boolean)
const [isOpen, setIsOpen] = useState(false);
setIsOpen(true); // Update state

// State with number
const [count, setCount] = useState(0);
setCount(count + 1);

// State with array of objects
const [notifications, setNotifications] = useState([
  { id: 1, message: 'Hello', isRead: false },
  { id: 2, message: 'World', isRead: true }
]);

// State with object
const [user, setUser] = useState({ id: '123', name: 'Sarah' });
```

**Best Practice:** Use separate `useState` calls for unrelated state variables instead of one big object.

---

## Array Methods

### `.map()` - Transform Arrays

**What it does:** Creates a new array by transforming each element.

**When to use:** Rendering lists in React, transforming data.

**Syntax:**
```javascript
array.map((item, index) => {
  return <Component key={item.id} data={item} />
})
```

**Project Example:**
```javascript
// Rendering notification list (NotificationsPanel.jsx:217)
{notifications.map((notification) => {
  const colors = colorMap[notification.color] || colorMap.green;
  const IconComponent = notification.icon;

  return (
    <div key={notification.id}>
      <IconComponent color={colors.text} />
      <p>{notification.message}</p>
    </div>
  );
})}
```

**Common Pattern - Updating State with `.map()`:**
```javascript
// Update specific item in array (NotificationsPanel.jsx:69)
setNotifications(prev =>
  prev.map(notif =>
    notif.id === notificationId
      ? { ...notif, isRead: true }  // Update this one
      : notif                        // Keep others unchanged
  )
);
```

**Remember:** Always include a unique `key` prop when rendering lists!

---

### `.filter()` - Filter Arrays

**What it does:** Creates a new array with elements that pass a test.

**Project Example:**
```javascript
// Count unread notifications (NotificationsPanel.jsx:84)
const unreadCount = notifications.filter(n => !n.isRead).length;
```

**Usage:**
```javascript
const activeUsers = users.filter(user => user.status === 'active');
const adults = people.filter(person => person.age >= 18);
```

---

### 🎓 Deep Dive: Deleting Items from State Arrays

**The Pattern (NotificationsPanel.jsx:84-91):**
```javascript
const deleteNotification = (notificationId) => {
  setNotifications(prev =>
    prev.filter(notif => notif.id !== notificationId)
  );
};
```

**Let me break this down for you, step by step:**

#### What's Happening Here?

This is a **deletion pattern** for removing an item from a state array. Let's understand each piece:

1. **Function Declaration:**
   ```javascript
   const deleteNotification = (notificationId) => { ... }
   ```
   - We create a function that takes one parameter: `notificationId`
   - This is the ID of the notification we want to delete
   - Think of it like: "Tell me WHICH notification to delete, and I'll remove it"

2. **State Update with Function:**
   ```javascript
   setNotifications(prev => ...)
   ```
   - We're using the **functional update form** of `setNotifications`
   - `prev` represents the **current/previous state** (the current array of notifications)
   - **Why use `prev`?** Because React might batch state updates. Using `prev` ensures we're working with the latest, most up-to-date version of the array

3. **The Filter Magic:**
   ```javascript
   prev.filter(notif => notif.id !== notificationId)
   ```
   - `.filter()` goes through each notification in the array
   - For each notification (we call it `notif`), it checks: `notif.id !== notificationId`
   - **Translation:** "Keep this notification ONLY if its ID is NOT equal to the ID we want to delete"
   - All notifications that pass this test (return `true`) are kept in a new array
   - The one that matches gets filtered OUT

#### Real-World Example

Let's say we have this state:
```javascript
notifications = [
  { id: 1, message: 'Welcome!' },
  { id: 2, message: 'New recipe' },
  { id: 3, message: 'Goal achieved' }
]
```

User clicks delete on notification with `id: 2`. Here's what happens:

```javascript
deleteNotification(2); // Call the function with ID 2

// Step 1: Get current state (prev)
prev = [
  { id: 1, message: 'Welcome!' },
  { id: 2, message: 'New recipe' },      // ← Target to delete
  { id: 3, message: 'Goal achieved' }
]

// Step 2: Filter runs on each item
// Check id 1: 1 !== 2? YES → KEEP ✓
// Check id 2: 2 !== 2? NO  → REMOVE ✗
// Check id 3: 3 !== 2? YES → KEEP ✓

// Step 3: New state is set
notifications = [
  { id: 1, message: 'Welcome!' },
  { id: 3, message: 'Goal achieved' }
]
// ID 2 is gone! 🎉
```

#### Why Not Just Modify the Array Directly?

**❌ NEVER do this:**
```javascript
// BAD - Direct mutation
const deleteNotification = (notificationId) => {
  const index = notifications.findIndex(n => n.id === notificationId);
  notifications.splice(index, 1); // Mutating state directly!
  setNotifications(notifications); // React won't detect the change!
};
```

**Why is this bad?**
- React uses **reference equality** to detect changes
- If you modify the same array, its reference stays the same
- React thinks: "Same reference = no change = no re-render"
- Your UI won't update! 😱

**✅ The CORRECT way (what we're doing):**
```javascript
// GOOD - Create new array
setNotifications(prev =>
  prev.filter(notif => notif.id !== notificationId)
);
```
- `.filter()` creates a **brand new array**
- New array = new reference
- React detects the change and re-renders
- UI updates correctly! ✨

#### Key Takeaways

1. **Always create new arrays/objects when updating state** - never mutate directly
2. **Use `prev` in state setters** when the new state depends on the old state
3. **`.filter()` is perfect for deletion** because it creates a new array without the unwanted item
4. **The `!==` comparison** means "keep everything EXCEPT the one we want to delete"
5. **This pattern is immutable** - we don't change the original array, we create a new one

#### When You'll Use This Pattern

- Deleting items from a list (todos, notifications, cart items)
- Removing users from a team
- Clearing search results
- Any time you need to "take one out" of an array in state

#### Practice Challenge

Try modifying this to delete multiple notifications at once:
```javascript
const deleteMultipleNotifications = (idsToDelete) => {
  setNotifications(prev =>
    prev.filter(notif => !idsToDelete.includes(notif.id))
  );
};

// Usage:
deleteMultipleNotifications([1, 3, 5]); // Removes notifications 1, 3, and 5
```

**Remember:** In React, state is **immutable**. Always create new arrays/objects instead of modifying existing ones! 🚀

---

## Conditional Rendering

### Pattern 1: `&&` Operator (Short Circuit)

**When to use:** Show element only if condition is true.

```javascript
// Show only if unreadCount > 0 (NotificationsPanel.jsx:159)
{unreadCount > 0 && (
  <p>{unreadCount} unread</p>
)}

// Show mark all button only if there are unread items (NotificationsPanel.jsx:193)
{unreadCount > 0 && (
  <button onClick={markAllAsRead}>
    Mark all as read
  </button>
)}
```

### Pattern 2: Ternary Operator `? :`

**When to use:** Choose between two options.

```javascript
// Toggle between two icons (Login.jsx:219)
{showPassword ? (
  <EyeOff width={20} height={20} />
) : (
  <Eye width={20} height={20} />
)}

// Dynamic styling
background: isHovered ? '#f3f4f6' : 'transparent'
```

### Pattern 3: Early Return

**When to use:** Show different UI for different states.

```javascript
// Show login if not authenticated (App.jsx:356)
if (!isLoggedIn) {
  return <Login onLogin={handleLogin} />;
}

// Show loading state (App.jsx:360)
if (loading) {
  return <div>Loading your nutrition data...</div>;
}

// Show main content
return <Dashboard />;
```

---

## Event Handlers

### onClick - Click Events

**Project Pattern:**
```javascript
// Close button (NotificationsPanel.jsx:170)
<button onClick={onClose}>
  <X width={20} height={20} />
</button>

// With parameter
<button onClick={() => markAsRead(notification.id)}>
  Mark as Read
</button>

// Prevent default behavior (Login.jsx:272)
<a href="#" onClick={(e) => {
  e.preventDefault();
  console.log('Forgot password clicked');
}}>
  Forgot password?
</a>
```

### Hover Events (onMouseEnter/onMouseLeave)

**Project Pattern:**
```javascript
// Hover state management (NotificationBellButton.jsx:344)
<button
  onMouseEnter={() => setIsHovered(true)}
  onMouseLeave={() => setIsHovered(false)}
  style={{
    background: isHovered ? '#f3f4f6' : 'transparent'
  }}
>
  <Bell />
</button>
```

### Form Events

**Project Pattern:**
```javascript
// Form submission (Login.jsx:10)
const handleSubmit = async (e) => {
  e.preventDefault(); // Prevent page reload
  console.log('Form submitted:', { email, password });
};

// Input change
<input
  value={email}
  onChange={(e) => setEmail(e.target.value)}
/>
```

### Inline Hover Handlers (Older Pattern)

```javascript
// Direct style manipulation (NotificationsPanel.jsx:181)
<button
  onMouseOver={(e) => {
    e.target.style.background = '#f3f4f6';
  }}
  onMouseOut={(e) => {
    e.target.style.background = 'transparent';
  }}
>
```

**Note:** `onMouseEnter/onMouseLeave` + state is more React-like than direct style manipulation.

---

## State Management Patterns

### Functional State Updates

**When to use:** When new state depends on previous state.

```javascript
// Mark all as read (NotificationsPanel.jsx:79)
const markAllAsRead = () => {
  setNotifications(prev =>
    prev.map(notif => ({ ...notif, isRead: true }))
  );
};

// Safer than:
setNotifications(
  notifications.map(notif => ({ ...notif, isRead: true }))
);
```

**Why?** React batches state updates. Using `prev` ensures you get the latest value.

---

### 🎓 Deep Dive: Derived State Pattern (Notification Badge Count)

**The Pattern (App.jsx:211-215):**
```javascript
// Store the full notifications array
const [notifications, setNotifications] = useState([]);

// Calculate unread count from notifications array
const unreadNotifications = notifications.filter(n => !n.isRead).length;
```

**Let me explain this important React pattern:**

#### What is Derived State?

**Derived state** means calculating a value from existing state rather than storing it separately. Instead of maintaining two separate pieces of state that need to stay in sync, we store the source data and calculate what we need from it.

#### The Problem We're Solving

**❌ BAD Approach - Storing the same data twice:**
```javascript
const [notifications, setNotifications] = useState([]);
const [unreadCount, setUnreadCount] = useState(0); // ❌ Redundant!

// Now you have to update BOTH every time notifications change
const markAsRead = (id) => {
  setNotifications(prev =>
    prev.map(n => n.id === id ? {...n, isRead: true} : n)
  );
  setUnreadCount(prev => prev - 1); // ❌ Easy to forget or mess up!
};
```

**Problems with this approach:**
- Two pieces of state to maintain
- Risk of them getting out of sync (notifications say 3 unread, but count says 2)
- More code to write and more bugs to fix
- Harder to reason about

**✅ GOOD Approach - Derive it when needed:**
```javascript
const [notifications, setNotifications] = useState([]);
// Derived state - calculated from source of truth
const unreadNotifications = notifications.filter(n => !n.isRead).length;

// Only update the source data
const markAsRead = (id) => {
  setNotifications(prev =>
    prev.map(n => n.id === id ? {...n, isRead: true} : n)
  );
  // unreadNotifications automatically updates! ✨
};
```

**Benefits:**
- Single source of truth (`notifications` array)
- Impossible for count to be wrong - it's always calculated from the data
- Less code, fewer bugs
- React automatically recalculates when `notifications` changes

#### How It Works Step-by-Step

Let's trace through an example:

```javascript
// Initial state
const [notifications, setNotifications] = useState([
  { id: 1, message: 'Welcome!', isRead: false },
  { id: 2, message: 'New recipe', isRead: false },
  { id: 3, message: 'Goal hit!', isRead: true }
]);

// Step 1: Filter runs on render
const unreadNotifications = notifications.filter(n => !n.isRead).length;
// Result: 2 (notifications 1 and 2 are unread)

// Step 2: User marks notification 1 as read
markAsRead(1);

// Step 3: notifications state updates
// New value: [
//   { id: 1, message: 'Welcome!', isRead: true },  // ← Changed!
//   { id: 2, message: 'New recipe', isRead: false },
//   { id: 3, message: 'Goal hit!', isRead: true }
// ]

// Step 4: React re-renders component
// Step 5: Filter runs again automatically
const unreadNotifications = notifications.filter(n => !n.isRead).length;
// Result: 1 (only notification 2 is unread now)

// Step 6: Bell badge updates to show "1" ✓
```

#### Real-World Usage in Our App

**In the header (App.jsx:242-244):**
```javascript
<NotificationBellButton
  unreadCount={unreadNotifications}  // ← Derived value
  onClick={() => setShowNotifications(!showNotifications)}
/>
```

The bell icon badge automatically shows the correct count because:
1. We pass `unreadNotifications` (derived from the array)
2. When any notification changes, React re-renders
3. The filter recalculates automatically
4. Badge displays the new count

#### When to Use Derived State

**Use derived state when:**
- The value can be calculated from existing state
- Calculating it is fast (like `.filter()` or `.length`)
- The value always depends on the source data

**Examples from our app:**
```javascript
// Unread notification count
const unreadCount = notifications.filter(n => !n.isRead).length;

// Total calories consumed
const totalCalories = meals.reduce((sum, meal) => sum + meal.calories, 0);

// Remaining calorie budget
const remaining = calorieGoal - totalCalories;

// Percentage of goal reached
const percentage = Math.round((totalCalories / calorieGoal) * 100);

// Is form valid?
const isFormValid = email.length > 0 && password.length >= 8;
```

#### When NOT to Use Derived State

**Don't derive state if:**
- The calculation is expensive (complex loops, heavy processing)
- You need to run side effects based on changes
- The value needs to persist across unmounts

**For expensive calculations, use `useMemo`:**
```javascript
// If filtering 10,000 notifications with complex logic
const unreadCount = useMemo(() =>
  notifications.filter(n => !n.isRead && n.priority === 'high').length,
  [notifications] // Only recalculate when notifications change
);
```

#### API Integration Pattern

When you connect this to an API, the pattern stays the same:

```javascript
const [notifications, setNotifications] = useState([]);
const unreadNotifications = notifications.filter(n => !n.isRead).length;

// Fetch from API
useEffect(() => {
  const fetchNotifications = async () => {
    const response = await apiService.getNotifications(user.id);
    setNotifications(response.data); // Set source data
    // unreadNotifications updates automatically!
  };

  fetchNotifications();
}, [user.id]);
```

**API Endpoint Structure:**
```javascript
// GET /api/notifications/:userId
// Response:
{
  "data": [
    { "id": 1, "message": "...", "isRead": false, "timestamp": "..." },
    { "id": 2, "message": "...", "isRead": true, "timestamp": "..." }
  ]
}
```

#### Key Takeaways

1. **Don't store what you can calculate** - Derive values from source state
2. **Single source of truth** - Store data once, calculate everything else from it
3. **Automatic updates** - Derived values recalculate on every render
4. **Less code, fewer bugs** - No need to keep multiple states in sync
5. **Performance** - For fast calculations, this is fine. For slow ones, use `useMemo`

#### Practice Challenge

Imagine you have a shopping cart. Which should be state vs derived?

```javascript
// What should be state?
const [cartItems, setCartItems] = useState([
  { id: 1, name: 'Apple', price: 2.50, quantity: 3 },
  { id: 2, name: 'Bread', price: 3.00, quantity: 1 }
]);

// What can be derived?
const itemCount = cartItems.reduce((sum, item) => sum + item.quantity, 0);
const subtotal = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
const tax = subtotal * 0.08;
const total = subtotal + tax;
const isEmpty = cartItems.length === 0;
```

**Answer:** Only `cartItems` needs to be state! Everything else is derived. ✨

---

## Component Patterns

### Functional Component Structure

**Project Pattern:**
```javascript
// Component with props and state (NotificationsPanel.jsx:14)
const NotificationsPanel = ({ isOpen, onClose, user }) => {
  const [notifications, setNotifications] = useState([]);

  const markAsRead = (notificationId) => {
    // Function logic
  };

  return (
    <div>
      {/* JSX content */}
    </div>
  );
};

export default NotificationsPanel;
```

### Reusable Component with Configuration

**Project Pattern:**
```javascript
// Icon configuration object (App.jsx:30)
const iconConfig = {
  navigation: {
    dashboard: { icon: LayoutDashboard, label: 'Dashboard' },
    recipes: { icon: ChefHat, label: 'Recipe Generator' }
  }
};

// IconWrapper component (App.jsx:92)
const IconWrapper = ({ iconKey, category = 'navigation', size = 'default' }) => {
  const iconData = iconConfig[category]?.[iconKey];
  if (!iconData) return null;

  const IconComponent = iconData.icon;
  return <IconComponent {...sizeMap[size]} />;
};
```

---

## Object Destructuring & Access

### Safe Property Access with Fallback

**Project Pattern:**
```javascript
// Fallback to green if color doesn't exist (NotificationsPanel.jsx:218)
const colors = colorMap[notification.color] || colorMap.green;
```

**Breakdown:**
- `colorMap[notification.color]` tries to get the color
- If undefined/null/falsy, use `colorMap.green` as default

**Example:**
```javascript
const colorMap = {
  red: '#ff0000',
  green: '#00ff00'
};

const notification = { color: 'purple' }; // purple doesn't exist!
const colors = colorMap[notification.color] || colorMap.green;
// Result: '#00ff00'
```

### Optional Chaining `?.`

**Project Pattern:**
```javascript
// Safe nested property access (App.jsx:100)
const iconData = iconConfig[category]?.[iconKey];

// Without optional chaining (would error if category doesn't exist):
const iconData = iconConfig[category][iconKey]; // ❌ Error if category is undefined
```

### Spread Operator `...` for Immutable Updates

**Project Pattern:**
```javascript
// Update one property, keep the rest (NotificationsPanel.jsx:72)
{ ...notif, isRead: true }

// Creates new object:
// { id: 1, message: 'Hello', isRead: true }
// Instead of modifying original
```

---

## Inline Styling

### Dynamic Inline Styles

**Project Pattern:**
```javascript
// Conditional styling (NotificationsPanel.jsx:227)
style={{
  borderLeft: !notification.isRead
    ? `3px solid ${colors.text}`
    : '3px solid transparent',
  background: !notification.isRead ? '#fafafa' : 'transparent'
}}

// Transform based on state (NotificationsPanel.jsx:126)
style={{
  transform: isOpen ? 'translateX(0)' : 'translateX(100%)',
  transition: 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
}}
```

### Color Mapping Pattern

**Project Pattern:**
```javascript
// Color configuration object (App.jsx:138)
const colorMap = {
  green: { bg: '#f0fdf4', hover: '#dcfce7', text: '#16a34a' },
  orange: { bg: '#fff7ed', hover: '#ffedd5', text: '#ea580c' }
};

// Usage
const colors = colorMap[action.color] || colorMap.green;
<div style={{ background: colors.bg, color: colors.text }} />
```

---

## Service Classes

### API Service Pattern

**Project Pattern:**
```javascript
// Service class definition (App.jsx:51)
class ApiService {
  constructor() {
    this.baseURL = 'http://localhost:3001';
  }

  async fetchNutritionData(userId) {
    console.log(`Fetching nutrition data for user: ${userId}`);
    return null; // TODO: Implement actual API call
  }

  async logMeal(mealData) {
    console.log('Logging meal:', mealData);
    return { success: true };
  }
}

// Usage in component
const apiService = new ApiService();
await apiService.fetchNutritionData(user.id);
```

**Best Practice:** Separate business logic from UI components using service classes.

---

## Custom Hooks

### Custom Hook Pattern

**Project Pattern:**
```javascript
// Custom hook for data fetching (App.jsx:84)
const useNutritionData = (userId) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // TODO: Add useEffect to fetch data

  return { data, loading, error };
};

// Usage in component
const { data: nutritionData, loading } = useNutritionData(user.id);
```

**Naming Convention:** Custom hooks MUST start with `use` (e.g., `useNutritionData`, `useAuth`).

---

## Common JavaScript Patterns

### Arrow Functions

**Syntax:**
```javascript
// Traditional function
function add(a, b) {
  return a + b;
}

// Arrow function
const add = (a, b) => a + b;

// With block
const add = (a, b) => {
  const result = a + b;
  return result;
};
```

**Project Usage:**
```javascript
// Event handler
onClick={() => setIsOpen(true)}

// Map callback
notifications.map((notification) => {
  return <div key={notification.id} />;
})
```

---

## Component Naming Conventions

### PascalCase for Components

**Project Pattern:**
```javascript
// Component stored in variable MUST be PascalCase (NotificationsPanel.jsx:219)
const IconComponent = notification.icon;

// Usage in JSX
<IconComponent width={20} height={20} />

// ❌ Wrong (lowercase won't work):
const iconComponent = notification.icon;
<iconComponent /> // React thinks this is HTML tag!
```

**Rule:** React components = PascalCase, HTML elements = lowercase.

---

## Common Gotchas & Best Practices

### ✅ DO's

1. **Always use unique keys in lists**
```javascript
{items.map(item => (
  <div key={item.id}>{item.name}</div>
))}
```

2. **Use functional updates for dependent state**
```javascript
setCount(prev => prev + 1); // ✅
setCount(count + 1); // ❌ May be stale
```

3. **Prevent default on form submissions**
```javascript
const handleSubmit = (e) => {
  e.preventDefault();
  // Your code
};
```

### ❌ DON'Ts

1. **Don't mutate state directly**
```javascript
// ❌ Wrong
notifications.push(newNotification);

// ✅ Correct
setNotifications([...notifications, newNotification]);
```

2. **Don't use indexes as keys (unless stable)**
```javascript
// ❌ Avoid
{items.map((item, index) => <div key={index} />)}

// ✅ Better
{items.map(item => <div key={item.id} />)}
```

---

## Quick Reference Table

| Pattern | Use Case | Example |
|---------|----------|---------|
| `.map()` | Render lists | `items.map(item => <div key={item.id} />)` |
| `.filter()` | Filter arrays | `items.filter(item => item.active)` |
| `&&` | Conditional render | `{isOpen && <Modal />}` |
| `? :` | Choose between two | `{loading ? <Spinner /> : <Content />}` |
| `useState` | Manage state | `const [count, setCount] = useState(0)` |
| Spread `...` | Copy objects/arrays | `{ ...user, name: 'New' }` |
| Optional `?.` | Safe access | `user?.address?.city` |
| `\|\|` | Fallback value | `colors \|\| defaultColors` |

---

## Project-Specific Patterns

### Modal/Panel Toggle Pattern

```javascript
// State
const [isOpen, setIsOpen] = useState(false);

// Toggle button
<button onClick={() => setIsOpen(!isOpen)}>
  Open Panel
</button>

// Panel component
<Panel isOpen={isOpen} onClose={() => setIsOpen(false)} />
```

### Notification Badge Pattern

```javascript
{unreadCount > 0 && (
  <div style={{
    position: 'absolute',
    background: '#ef4444',
    borderRadius: '50%'
  }}>
    {unreadCount > 9 ? '9+' : unreadCount}
  </div>
)}
```

---

## Tech Stack Summary

- **React:** ^19.1.1
- **Build Tool:** Vite
- **Icons:** lucide-react
- **Styling:** Inline styles (no CSS-in-JS library)
- **State Management:** React useState (no Redux/Context yet)

---

## Resources

- [React Docs](https://react.dev)
- [JavaScript Array Methods](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array)
- [Lucide Icons](https://lucide.dev)

---

*Last Updated: 2025-10-01*
