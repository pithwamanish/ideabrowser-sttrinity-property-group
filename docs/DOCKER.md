# Docker Deployment Guide

## Prerequisites

- Docker Engine 20.10 or higher
- Docker Compose 2.0 or higher
- At least 2GB free disk space
- Ports 3000, 8000, and 27017 available

## Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd idea-board-platform
```

### 2. Start the Application
```bash
# Start all services (builds images if needed)
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 4. Stop the Application
```bash
# Stop all services
docker-compose down

# Stop and remove data volumes (resets database)
docker-compose down -v
```

## Container Architecture

### Services

#### Frontend (`ideaboard_frontend`)
- **Image**: Custom Node.js build
- **Port**: 3000
- **Technology**: React + Tailwind CSS
- **Serves**: Production optimized build

#### Backend (`ideaboard_backend`)
- **Image**: Custom Python build
- **Port**: 8000
- **Technology**: FastAPI + Uvicorn
- **Features**: Health checks, auto-restart

#### Database (`ideaboard_mongodb`)
- **Image**: Official MongoDB 7.0
- **Port**: 27017
- **Persistence**: Named volume `mongodb_data`
- **Database**: `ideaboard_db`

### Network
- **Name**: `ideaboard_network`
- **Type**: Bridge network
- **Purpose**: Isolated container communication

## Development Mode

### Hot Reloading Setup
```bash
# Use development compose file
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Development Features
- **Backend**: Auto-reload on code changes
- **Frontend**: Hot module replacement
- **Database**: Development database (`ideaboard_dev`)
- **Volumes**: Source code mounted for live editing

## Production Deployment

### Optimized Frontend Build
```bash
# Build production frontend with Nginx
docker build -f frontend/Dockerfile.prod -t ideaboard-frontend:prod frontend/
```

### Environment Configuration

Create production environment files:

**backend/.env.prod**:
```bash
MONGO_URL=mongodb://mongodb:27017
DB_NAME=ideaboard_prod
CORS_ORIGINS=https://yourdomain.com
```

**frontend/.env.prod**:
```bash
REACT_APP_BACKEND_URL=https://api.yourdomain.com
```

### Production Compose
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    ports:
      - "80:80"
    environment:
      - NODE_ENV=production
```

## Monitoring & Health Checks

### Health Check Endpoints

```bash
# Backend health
curl http://localhost:8000/api/

# Check all container status
docker-compose ps

# View service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mongodb
```

### Container Health Status
```bash
# Check backend health status
docker inspect ideaboard_backend --format='{{.State.Health.Status}}'
```

## Data Management

### Backup Database
```bash
# Create backup
docker-compose exec mongodb mongodump --db ideaboard_db --out /backup

# Copy backup to host
docker cp ideaboard_mongodb:/backup ./mongodb_backup
```

### Restore Database
```bash
# Copy backup to container
docker cp ./mongodb_backup ideaboard_mongodb:/backup

# Restore database
docker-compose exec mongodb mongorestore --db ideaboard_db /backup/ideaboard_db
```

### Reset Database
```bash
# Stop services and remove volumes
docker-compose down -v

# Start fresh
docker-compose up --build
```

## Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check what's using the ports
sudo lsof -i :3000
sudo lsof -i :8000
sudo lsof -i :27017

# Kill processes if needed
sudo kill -9 <PID>
```

#### Container Won't Start
```bash
# Check container logs
docker-compose logs <service-name>

# Check Docker daemon
sudo systemctl status docker

# Restart Docker if needed
sudo systemctl restart docker
```

#### Database Connection Issues
```bash
# Test MongoDB connection
docker-compose exec backend python -c "from motor.motor_asyncio import AsyncIOMotorClient; print('MongoDB connection test')"

# Check network connectivity
docker-compose exec backend ping mongodb
```

#### Frontend Not Loading
```bash
# Check if backend is responding
curl http://localhost:8000/api/

# Check CORS configuration
# Look for CORS errors in browser console

# Verify environment variables
docker-compose exec frontend env | grep REACT_APP
```

### Performance Optimization

#### Resource Limits
```yaml
# Add to docker-compose.yml services
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

#### Image Size Optimization
```bash
# Check image sizes
docker images | grep ideaboard

# Clean up unused images
docker system prune -f
```

## Security Considerations

### Production Security
- Change default MongoDB credentials
- Use HTTPS in production
- Implement rate limiting
- Add authentication if needed
- Use Docker secrets for sensitive data

### Network Security
```yaml
# Restrict MongoDB access
services:
  mongodb:
    expose:
      - "27017"  # Don't publish to host in production
    # Remove 'ports' section for production
```

## Scaling

### Horizontal Scaling
```yaml
# Scale specific services
docker-compose up --scale backend=3 --scale frontend=2
```

### Load Balancer Configuration
```yaml
# Add Nginx load balancer
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend
      - backend
```

## Maintenance

### Regular Tasks
```bash
# Update images
docker-compose pull

# Rebuild with latest code
docker-compose up --build --force-recreate

# Clean up old images
docker image prune -f
```

### Logs Management
```bash
# Limit log size in compose file
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```
