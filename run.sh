#!/bin/bash

# Personal AI Assistant - Quick Start Script

echo "🚀 Starting Personal AI Assistant..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Python is installed
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

echo "✅ Prerequisites check passed!"

# Start database services
echo "🗄️  Starting database services..."
docker-compose up -d

# Wait for databases to be ready
echo "⏳ Waiting for databases to be ready..."
sleep 10

# Install Python dependencies if not already installed
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python -m venv venv
fi

echo "📦 Installing Python dependencies..."
source venv/bin/activate 2>/dev/null || venv\Scripts\activate
pip install -r backend/requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating environment file..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration before proceeding."
fi

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install

echo "🎉 Setup complete!"
echo ""
echo "To start the application:"
echo "1. Backend: python run_backend.py"
echo "2. Frontend: npm run dev"
echo ""
echo "Or use the provided npm scripts:"
echo "- npm run start:db    # Start databases"
echo "- npm run start:backend # Start backend server"
echo "- npm run dev         # Start frontend"
echo ""
echo "Visit http://localhost:5173 to access the application"