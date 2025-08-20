# Personal AI Assistant - Setup Instructions

## Prerequisites

Before running the application, ensure you have the following installed:

1. **Node.js** (v18 or higher) - [Download here](https://nodejs.org/)
2. **Python** (v3.9 or higher) - [Download here](https://python.org/)
3. **Docker & Docker Compose** - [Download here](https://docker.com/)
4. **Git** - [Download here](https://git-scm.com/)

## Quick Start Guide

### Step 1: Install Frontend Dependencies

The frontend dependencies should already be installed. If not, run:

```bash
npm install
```

### Step 2: Start Database Services

Start PostgreSQL, Redis, and Neo4j using Docker:

```bash
docker-compose up -d
```

This will start:
- PostgreSQL on port 5432
- Redis on port 6379  
- Neo4j on port 7474 (web interface) and 7687 (bolt)

### Step 3: Install Python Dependencies

Install the backend dependencies:

```bash
pip install -r backend/requirements.txt
```

If you encounter any issues, try using a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### Step 4: Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/ai_assistant
REDIS_URL=redis://localhost:6379/0

# Authentication (Generate a secure secret key)
SECRET_KEY=your-very-secure-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# AI Configuration (Optional - for production AI integration)
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Application
DEBUG=true
```

### Step 5: Start the Backend Server

Run the backend server:

```bash
python run_backend.py
```

The backend will start on `http://localhost:8000`

### Step 6: Start the Frontend (if not already running)

The frontend should already be running. If not, start it:

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Verification Steps

1. **Check Database Connection**: Visit `http://localhost:8000/health` - should return `{"status": "healthy"}`

2. **Check Neo4j**: Visit `http://localhost:7474` - Neo4j browser interface

3. **Test Frontend**: Visit `http://localhost:5173` - should show the login page

## Usage Instructions

### First Time Setup

1. **Create an Account**:
   - Go to `http://localhost:5173`
   - Click "Sign up" 
   - Fill in your details (name, email, password)
   - Click "Create Account"

2. **Start Chatting**:
   - After login, you'll see the chat interface
   - Click "New Conversation" to start
   - Type your message and press Enter
   - The AI will respond with context-aware replies

### Features to Test

1. **Context Retention**: 
   - Ask about something, then refer to it later in the conversation
   - The AI remembers previous context

2. **User Preferences**:
   - Tell the AI your preferences (e.g., "I prefer formal communication")
   - Notice how responses adapt to your style

3. **Memory System**:
   - Share important information
   - The system stores and recalls relevant details

4. **Multiple Conversations**:
   - Create multiple conversations
   - Each maintains separate context

## Troubleshooting

### Common Issues

1. **Database Connection Error**:
   ```bash
   # Check if Docker containers are running
   docker-compose ps
   
   # Restart if needed
   docker-compose down
   docker-compose up -d
   ```

2. **Python Module Not Found**:
   ```bash
   # Make sure you're in the right directory and virtual environment is activated
   pip install -r backend/requirements.txt
   ```

3. **Port Already in Use**:
   ```bash
   # Kill processes on ports 8000 or 5173
   # On Windows:
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   
   # On macOS/Linux:
   lsof -ti:8000 | xargs kill -9
   ```

4. **Frontend Build Issues**:
   ```bash
   # Clear node modules and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

### Database Issues

If you need to reset the database:

```bash
# Stop containers
docker-compose down

# Remove volumes (WARNING: This deletes all data)
docker-compose down -v

# Start fresh
docker-compose up -d
```

### Backend Logs

To see detailed backend logs:

```bash
# Run with more verbose logging
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

## Development Tips

1. **Hot Reload**: Both frontend and backend support hot reload during development

2. **API Documentation**: Visit `http://localhost:8000/docs` for interactive API documentation

3. **Database Admin**: Use tools like pgAdmin or DBeaver to inspect the PostgreSQL database

4. **Redis Monitoring**: Use Redis CLI or Redis Desktop Manager to monitor cache

## Production Deployment

For production deployment:

1. **Environment Variables**: Update `.env` with production values
2. **Database**: Use managed PostgreSQL service
3. **Redis**: Use managed Redis service  
4. **Security**: Enable HTTPS, update CORS settings
5. **Monitoring**: Set up logging and monitoring

## Support

If you encounter issues:

1. Check the console logs in your browser (F12)
2. Check backend logs in the terminal
3. Verify all services are running with `docker-compose ps`
4. Ensure all environment variables are set correctly

The application features sophisticated AI capabilities with context retention, user personalization, and multi-level memory architecture for an enhanced conversational experience.