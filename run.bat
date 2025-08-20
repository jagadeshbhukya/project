@echo off
REM Personal AI Assistant - Quick Start Script for Windows

echo 🚀 Starting Personal AI Assistant...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.9 or higher.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 18 or higher.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed!

REM Start database services
echo 🗄️  Starting database services...
docker-compose up -d

REM Wait for databases to be ready
echo ⏳ Waiting for databases to be ready...
timeout /t 10 /nobreak >nul

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 🐍 Creating Python virtual environment...
    python -m venv venv
)

REM Install Python dependencies
echo 📦 Installing Python dependencies...
call venv\Scripts\activate
pip install -r backend/requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo ⚙️  Creating environment file...
    copy .env.example .env
    echo 📝 Please edit .env file with your configuration before proceeding.
)

REM Install Node.js dependencies
echo 📦 Installing Node.js dependencies...
npm install

echo 🎉 Setup complete!
echo.
echo To start the application:
echo 1. Backend: python run_backend.py
echo 2. Frontend: npm run dev
echo.
echo Or use the provided npm scripts:
echo - npm run start:db    # Start databases
echo - npm run start:backend # Start backend server  
echo - npm run dev         # Start frontend
echo.
echo Visit http://localhost:5173 to access the application
pause