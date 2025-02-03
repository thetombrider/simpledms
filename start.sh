#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Function to check if backend is healthy
check_backend_health() {
    local max_attempts=10
    local attempt=1
    local wait_time=1
    
    echo -e "${YELLOW}Waiting for backend to be ready...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "http://localhost:8080/api/v1/health" > /dev/null; then
            echo -e "${GREEN}Backend is ready!${NC}"
            return 0
        fi
        echo -e "${YELLOW}Attempt $attempt/$max_attempts: Backend not ready yet, waiting...${NC}"
        sleep $wait_time
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}Backend failed to start after $max_attempts attempts${NC}"
    return 1
}

echo -e "${YELLOW}Starting SimpleS3DMS...${NC}"

# Check if required directories exist
if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo -e "${RED}Error: Missing required directories (frontend or backend)${NC}"
    echo -e "Please ensure you're running this script from the project root directory"
    echo -e "Current directory structure:"
    ls -la
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Start MongoDB container if not running
if ! docker ps | grep -q "simpledms-mongodb-1"; then
    echo -e "${YELLOW}Starting MongoDB container...${NC}"
    docker-compose up -d mongodb
    sleep 5  # Give MongoDB time to initialize
fi

# Check MongoDB connection
echo -e "${YELLOW}Checking MongoDB connection...${NC}"
if ! docker exec $(docker ps -q -f name=simpledms-mongodb-1) mongosh --eval "db.runCommand({ ping: 1 })" > /dev/null 2>&1; then
    echo -e "${RED}Cannot connect to MongoDB container. Please check docker-compose logs.${NC}"
    exit 1
fi
echo -e "${GREEN}MongoDB connection successful${NC}"

# Create backend virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Start backend in the background
echo -e "${YELLOW}Starting backend service...${NC}"
cd backend
export PYTHONPATH=$SCRIPT_DIR/backend
export MONGODB_URL="mongodb://localhost:27017"  # Use port-forwarded MongoDB
uvicorn main:app --reload --port 8080 &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

# Check if backend starts successfully
if ! check_backend_health; then
    echo -e "${RED}Failed to start backend service${NC}"
    kill $BACKEND_PID 2>/dev/null
    deactivate
    exit 1
fi

# Start frontend
echo -e "${YELLOW}Starting frontend service...${NC}"
cd frontend
export PYTHONPATH=$SCRIPT_DIR/frontend
streamlit run main.py &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"
echo -e "${GREEN}Frontend started successfully${NC}"

# Function to handle script termination
cleanup() {
    echo -e "${YELLOW}Shutting down services...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    deactivate
    echo -e "${GREEN}All services stopped${NC}"
    exit 0
}

# Register the cleanup function for script termination
trap cleanup SIGINT SIGTERM

echo -e "${GREEN}All services are running!${NC}"
echo -e "Frontend: http://localhost:8501"
echo -e "Backend: http://localhost:8080"
echo -e "MongoDB: $MONGODB_URL (Docker container)"
echo -e "Press Ctrl+C to stop all services"

# Keep the script running
wait