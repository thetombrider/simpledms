#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Testing SimpleS3DMS Docker Deployment${NC}"

# Function to check if a service is healthy
check_service() {
    local service=$1
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}Checking $service...${NC}"
    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps $service | grep -q "Up"; then
            echo -e "${GREEN}$service is up!${NC}"
            return 0
        fi
        echo -n "."
        sleep 1
        attempt=$((attempt + 1))
    done
    echo -e "\n${RED}$service failed to start${NC}"
    return 1
}

# Clean start
echo -e "${YELLOW}Cleaning up previous deployment...${NC}"
docker-compose down -v
docker-compose build --no-cache

# Start services
echo -e "${YELLOW}Starting services...${NC}"
docker-compose up -d

# Check services
for service in mongodb backend frontend; do
    if ! check_service $service; then
        echo -e "${RED}Deployment test failed at $service startup${NC}"
        docker-compose logs $service
        exit 1
    fi
done

# Test MongoDB connection
echo -e "${YELLOW}Testing MongoDB connection...${NC}"
if ! docker exec simpledms-mongodb-1 mongosh --eval "db.runCommand({ ping: 1 })" > /dev/null; then
    echo -e "${RED}MongoDB connection test failed${NC}"
    exit 1
fi
echo -e "${GREEN}MongoDB connection test passed${NC}"

# Test Backend API
echo -e "${YELLOW}Testing Backend API...${NC}"
if ! curl -s http://localhost:8080/api/v1/health > /dev/null; then
    echo -e "${RED}Backend API test failed${NC}"
    exit 1
fi
echo -e "${GREEN}Backend API test passed${NC}"

# Test Frontend
echo -e "${YELLOW}Testing Frontend...${NC}"
if ! curl -s http://localhost:8501 > /dev/null; then
    echo -e "${RED}Frontend test failed${NC}"
    exit 1
fi
echo -e "${GREEN}Frontend test passed${NC}"

# Check network connectivity
echo -e "${YELLOW}Testing inter-service communication...${NC}"
if ! docker exec simpledms-backend-1 curl -s mongodb:27017 > /dev/null; then
    echo -e "${RED}Backend to MongoDB communication failed${NC}"
    exit 1
fi
echo -e "${GREEN}Network connectivity test passed${NC}"

# All tests passed
echo -e "${GREEN}All deployment tests passed!${NC}"
echo -e "You can access the app at:"
echo -e "Frontend: http://localhost:8501"
echo -e "Backend: http://localhost:8080"
echo -e "MongoDB: localhost:27017"

# Show resource usage
echo -e "\n${YELLOW}Current resource usage:${NC}"
docker stats --no-stream simpledms-mongodb-1 simpledms-backend-1 simpledms-frontend-1 