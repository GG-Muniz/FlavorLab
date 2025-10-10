# FlavorLab Frontend Setup Guide

## Prerequisites

Before running this project, ensure you have the following installed:

### Frontend Requirements
- **Node.js** (v18 or higher) - [Download here](https://nodejs.org/)
- **npm** (comes with Node.js) or **yarn**

Check your versions:
```bash
node --version
npm --version
```

### Backend Requirements (if running locally)
- **Python** (v3.9 or higher) - [Download here](https://www.python.org/)
- **pip** (comes with Python)

Check your versions:
```bash
python --version
pip --version
```

---

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd flavorlab-app
```

### 2. Install Frontend Dependencies
```bash
npm install
```

or if you use yarn:
```bash
yarn install
```

### 3. Install Backend Dependencies (Python)
If you're also running the backend locally:

```bash
pip install -r requirements.txt
```

**Note:** It's recommended to use a virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Then install dependencies
pip install -r requirements.txt
```

---

## Running the Application

### Development Mode
Start the development server with hot-reload:
```bash
npm run dev
```

The application will be available at: **http://localhost:5173**

### Production Build
Create an optimized production build:
```bash
npm run build
```

### Preview Production Build
Preview the production build locally:
```bash
npm run preview
```

### Linting
Run ESLint to check code quality:
```bash
npm run lint
```

---

## Project Dependencies

### Core Dependencies
- **React 19.1.1** - UI library
- **React DOM 19.1.1** - React rendering
- **Lucide React 0.544.0** - Icon library
- **Tailwind CSS 4.1.13** - Utility-first CSS framework
- **Vite 7.1.6** - Build tool and dev server

### Development Dependencies
- **ESLint** - Code linting
- **@vitejs/plugin-react** - React plugin for Vite
- TypeScript type definitions for React

---

## Environment Variables

Currently, the app uses mock data. When integrating with the backend, create a `.env` file:

```env
VITE_API_BASE_URL=http://localhost:3001
```

Access in code:
```javascript
const apiUrl = import.meta.env.VITE_API_BASE_URL;
```

---

## Project Structure

```
flavorlab-app/
├── public/              # Static assets
├── src/
│   ├── components/      # React components
│   │   ├── auth/       # Login components
│   │   ├── calendar/   # Calendar component
│   │   ├── modals/     # Modal components
│   │   ├── notifications/ # Notifications panel
│   │   └── onboarding/ # NutriTest onboarding
│   ├── App.jsx         # Main app component
│   └── main.jsx        # Entry point
├── package.json        # Dependencies and scripts
└── vite.config.js      # Vite configuration
```

---

## Backend Integration Notes

### API Endpoints to Implement

The frontend is ready to integrate with the following endpoints:

#### User Authentication
- `POST /api/auth/login`
- `POST /api/auth/register`

#### User Profile & Goals
- `GET /api/user/:userId/profile`
- `POST /api/user/:userId/nutritest` - Save NutriTest results
- `GET /api/user/:userId/health-goals`

#### Nutrition Data
- `GET /api/user/:userId/nutrition/daily` - Daily calories, macros, water
- `POST /api/user/:userId/nutrition/log-meal`
- `GET /api/user/:userId/nutrition/history`

#### Calendar & Events
- `GET /api/user/:userId/events/upcoming`
- `POST /api/user/:userId/events`

#### Health Tips
- `GET /api/user/:userId/health-tips/daily` - Personalized based on goals

#### Notifications
- `GET /api/user/:userId/notifications`
- `PUT /api/user/:userId/notifications/:notificationId/read`

See `API-INTEGRATION-PLAN.md` for detailed endpoint specifications.

---

## Troubleshooting

### Port already in use
If port 5173 is occupied:
```bash
# Kill the process using port 5173
lsof -ti:5173 | xargs kill -9

# Or specify a different port
npm run dev -- --port 3000
```

### Module not found errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Build errors
```bash
# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

---

## Contact

For questions about the frontend, contact the frontend development team.

For backend integration questions, refer to `API-INTEGRATION-PLAN.md`.
