# FlavorLab Development Setup Guide

This guide walks you through setting up the FlavorLab development environment after the recent project restructuring.

## 📁 New Project Structure

```
FlavorLab/
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── api/               # API route handlers
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic services
│   │   ├── config.py          # App configuration
│   │   ├── database.py        # Database setup
│   │   └── main.py            # FastAPI entry point (runs on port 8000)
│   ├── scripts/               # Utility scripts
│   ├── tests/                 # Backend tests
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React + Vite frontend application
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── auth/
│   │   │   ├── calendar/
│   │   │   ├── modals/
│   │   │   ├── notifications/
│   │   │   └── onboarding/
│   │   ├── App.jsx            # Main App component
│   │   └── main.jsx           # Vite entry point
│   ├── public/                # Static assets
│   ├── index.html             # HTML entry point
│   ├── vite.config.js         # Vite configuration
│   ├── package.json           # NPM dependencies
│   └── .env.example           # Environment variables template
│
├── .gitignore                 # Git ignore rules
├── README.md                  # Project overview
└── SETUP.md                   # This file
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+** (for backend)
- **Node.js 16+** (for frontend)
- **npm** or **yarn** (for frontend package management)
- **PostgreSQL** or **SQLite** (for database)

---

## Backend Setup

### 1. Navigate to backend directory

```bash
cd backend
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**On Linux/macOS:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables (optional)

Create a `.env` file in the `backend/` directory:

```bash
# backend/.env
DATABASE_URL=sqlite:///./flavorlab.db
SECRET_KEY=your-secret-key-here
DEBUG=True
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

### 6. Run the backend server

```bash
# From the backend/ directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at: **http://localhost:8000**
API documentation (Swagger UI): **http://localhost:8000/docs**

---

## Frontend Setup

### 1. Navigate to frontend directory

```bash
cd frontend
```

### 2. Install Node.js dependencies

```bash
npm install
```

**Note:** If you encounter issues, you may need to reinstall dependencies since `node_modules/` was moved:

```bash
rm -rf node_modules package-lock.json
npm install
```

### 3. Configure environment variables (optional)

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `frontend/.env` if you need to customize the API URL:

```bash
# frontend/.env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 4. Run the frontend development server

```bash
npm run dev
```

The frontend will be available at: **http://localhost:5173** (Vite's default port)

---

## 🔧 Development Workflow

### Running Both Servers Concurrently

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### API Configuration

The frontend is configured to connect to the backend at:
- **Default:** `http://localhost:8000/api/v1`
- **Configurable via:** `VITE_API_BASE_URL` environment variable in `frontend/.env`

The API base URL is set in [frontend/src/App.jsx:52](frontend/src/App.jsx#L52):
```javascript
this.baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
```

---

## 📝 Available Scripts

### Frontend Scripts

From the `frontend/` directory:

```bash
npm run dev      # Start development server (Vite)
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

### Backend Scripts

From the `backend/` directory:

```bash
# Start server
uvicorn app.main:app --reload

# Run tests
pytest

# Run with specific port
uvicorn app.main:app --reload --port 8000
```

---

## 🐛 Troubleshooting

### Frontend Issues

**Issue:** "Cannot find module" errors after moving files
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Issue:** API requests failing
- Verify backend is running on port 8000
- Check `VITE_API_BASE_URL` in `frontend/.env`
- Ensure CORS is configured correctly in `backend/app/config.py`

### Backend Issues

**Issue:** Database errors
```bash
# Reset database (SQLite)
cd backend
rm -f flavorlab.db
# Restart the server - tables will be recreated
```

**Issue:** Module import errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## 🔒 Environment Variables

### Backend (`backend/.env`)
```env
APP_NAME=FlavorLab
DEBUG=True
DATABASE_URL=sqlite:///./flavorlab.db
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

### Frontend (`frontend/.env`)
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## 📚 Next Steps

1. ✅ Backend and frontend are now in separate directories
2. ✅ API base URL has been updated to use port 8000
3. ✅ Environment variable support added
4. ⏳ Implement missing API endpoints (see API-INTEGRATION-PLAN.md)
5. ⏳ Set up proper authentication flow
6. ⏳ Connect frontend components to real API endpoints

---

## 🤝 Contributing

When making changes:
1. Keep backend and frontend code separate
2. Update environment variable examples when adding new configs
3. Run linters before committing (`npm run lint` for frontend)
4. Ensure both servers run without errors

---

## 📄 License

This project is licensed under the MIT License.
