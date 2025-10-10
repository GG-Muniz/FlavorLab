source@echo off
echo FlavorLab Backend Setup
echo ======================

echo Checking Python installation...
py --version
if %errorlevel% neq 0 (
    echo Python not found. Please install Python 3.9+ and try again.
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
py -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo Setting up environment...
if not exist .env (
    if exist .env.example (
        copy .env.example .env
        echo Created .env file from template
    ) else (
        echo .env.example not found, skipping
    )
) else (
    echo .env file already exists
)

echo.
echo Initializing database...
py scripts/init_db.py
if %errorlevel% neq 0 (
    echo Database initialization failed.
    pause
    exit /b 1
)

echo.
echo Setup completed successfully!
echo.
echo To start the server, run:
echo   uvicorn app.main:app --reload
echo.
echo Then visit: http://localhost:8000/docs
echo.
pause