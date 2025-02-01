#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}Starting SimpleS3DMS...${NC}"

# Check if required directories exist
if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo -e "${RED}Error: Missing required directories (frontend or backend)${NC}"
    echo -e "Please ensure you're running this script from the project root directory"
    echo -e "Current directory structure:"
    ls -la
    exit 1
fi

# Start MongoDB
echo -e "${YELLOW}Starting MongoDB...${NC}"
if ! brew services start mongodb-community; then
    echo -e "${RED}Failed to start MongoDB. Is it installed?${NC}"
    echo "Install with: brew install mongodb-community"
    exit 1
fi
echo -e "${GREEN}MongoDB started successfully${NC}"

# Wait for MongoDB to be ready
sleep 2

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
uvicorn main:app --reload --port 8080 &
BACKEND_PID=$!
cd "$SCRIPT_DIR"
echo -e "${GREEN}Backend started successfully${NC}"

# Wait for backend to be ready
sleep 2

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
    kill $BACKEND_PID
    kill $FRONTEND_PID
    brew services stop mongodb-community
    deactivate
    echo -e "${GREEN}All services stopped${NC}"
    exit 0
}

# Register the cleanup function for script termination
trap cleanup SIGINT SIGTERM

echo -e "${GREEN}All services are running!${NC}"
echo -e "Frontend: http://localhost:8501"
echo -e "Backend: http://localhost:8080"
echo -e "Press Ctrl+C to stop all services"

# Keep the script running
wait 