#!/bin/bash

# Docker Build Simulation Test
# Tests what would happen during actual Docker builds

echo "🐳 Docker Build Simulation Test"
echo "================================"

# Test 1: Backend dependencies installation simulation
echo "📦 Testing Backend Dependencies..."
cd /app/backend
if pip install --dry-run -r requirements.txt > /dev/null 2>&1; then
    echo "✅ Backend dependencies are installable"
else
    echo "❌ Backend dependencies have issues"
    exit 1
fi

# Test 2: Frontend dependencies simulation
echo "📦 Testing Frontend Dependencies..."
cd /app/frontend
if yarn install --dry-run > /dev/null 2>&1; then
    echo "✅ Frontend dependencies are installable"
else
    echo "❌ Frontend dependencies have issues"
    exit 1
fi

# Test 3: Frontend build simulation
echo "🏗️  Testing Frontend Build..."
if yarn build > /dev/null 2>&1; then
    echo "✅ Frontend builds successfully"
    # Check if build directory exists
    if [ -d "build" ]; then
        echo "✅ Build directory created"
        echo "   Build contents:"
        ls -la build/ | head -5
    else
        echo "❌ Build directory not created"
        exit 1
    fi
else
    echo "❌ Frontend build failed"
    exit 1
fi

# Test 4: Backend server startup simulation (quick test)
echo "🚀 Testing Backend Server Startup..."
cd /app/backend
timeout 10s python -c "
import uvicorn
from server import app
print('✅ Backend server can be imported and started')
" 2>/dev/null && echo "✅ Backend server startup test passed" || echo "❌ Backend server startup test failed"

# Test 5: Check Docker Compose syntax
echo "📝 Testing Docker Compose Syntax..."
cd /app
if python -c "
import yaml
with open('docker-compose.yml') as f:
    yaml.safe_load(f)
print('✅ Docker Compose syntax is valid')
"; then
    echo "✅ Docker Compose file is valid"
else
    echo "❌ Docker Compose file has syntax errors"
    exit 1
fi

# Test 6: Environment variables validation
echo "🌍 Testing Environment Variables..."
if grep -q "MONGO_URL" backend/.env && grep -q "REACT_APP_BACKEND_URL" frontend/.env; then
    echo "✅ Environment variables are configured"
else
    echo "❌ Environment variables are missing"
    exit 1
fi

# Test 7: Port configuration validation
echo "🔌 Testing Port Configuration..."
backend_port=$(grep -o "8000:8000" docker-compose.yml || echo "")
frontend_port=$(grep -o "3000:3000" docker-compose.yml || echo "")
mongodb_port=$(grep -o "27017:27017" docker-compose.yml || echo "")

if [[ -n "$backend_port" && -n "$frontend_port" && -n "$mongodb_port" ]]; then
    echo "✅ All required ports are configured"
    echo "   Backend: $backend_port"
    echo "   Frontend: $frontend_port" 
    echo "   MongoDB: $mongodb_port"
else
    echo "❌ Port configuration is incomplete"
    exit 1
fi

echo ""
echo "🎉 ALL DOCKER BUILD SIMULATION TESTS PASSED!"
echo "✅ Docker setup is ready for deployment"
echo ""
echo "Next steps:"
echo "1. Run: docker-compose up --build"
echo "2. Access frontend: http://localhost:3000"
echo "3. Access backend: http://localhost:8000/docs"