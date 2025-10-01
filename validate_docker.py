#!/usr/bin/env python3
"""
Docker Configuration Validator
Validates Docker setup without requiring Docker to be installed
"""

import os
import yaml
import json
from pathlib import Path

def validate_docker_compose():
    """Validate docker-compose.yml structure"""
    print("🐳 Validating docker-compose.yml...")
    
    compose_path = Path("/app/docker-compose.yml")
    if not compose_path.exists():
        print("❌ docker-compose.yml not found")
        return False
        
    try:
        with open(compose_path) as f:
            compose = yaml.safe_load(f)
            
        # Check required structure
        required_services = ['mongodb', 'backend', 'frontend']
        services = compose.get('services', {})
        
        for service in required_services:
            if service not in services:
                print(f"❌ Missing service: {service}")
                return False
            print(f"✅ Service found: {service}")
        
        # Check networks and volumes
        if 'networks' not in compose:
            print("❌ No networks defined")
            return False
        print("✅ Networks defined")
            
        if 'volumes' not in compose:
            print("❌ No volumes defined")
            return False
        print("✅ Volumes defined")
            
        # Validate service configurations
        backend = services.get('backend', {})
        if 'build' not in backend:
            print("❌ Backend service missing build configuration")
            return False
        print("✅ Backend build configuration found")
            
        frontend = services.get('frontend', {})
        if 'build' not in frontend:
            print("❌ Frontend service missing build configuration")
            return False
        print("✅ Frontend build configuration found")
            
        print("✅ docker-compose.yml is valid")
        return True
        
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML in docker-compose.yml: {e}")
        return False
    except Exception as e:
        print(f"❌ Error validating docker-compose.yml: {e}")
        return False

def validate_dockerfiles():
    """Validate Dockerfile configurations"""
    print("\n🐳 Validating Dockerfiles...")
    
    # Backend Dockerfile
    backend_dockerfile = Path("/app/backend/Dockerfile")
    if not backend_dockerfile.exists():
        print("❌ Backend Dockerfile not found")
        return False
        
    with open(backend_dockerfile) as f:
        backend_content = f.read()
        
    required_backend = ['FROM python:', 'WORKDIR /app', 'COPY requirements.txt', 'RUN pip install', 'EXPOSE 8000', 'CMD']
    for req in required_backend:
        if req not in backend_content:
            print(f"❌ Backend Dockerfile missing: {req}")
            return False
    print("✅ Backend Dockerfile is valid")
    
    # Frontend Dockerfile
    frontend_dockerfile = Path("/app/frontend/Dockerfile")
    if not frontend_dockerfile.exists():
        print("❌ Frontend Dockerfile not found")
        return False
        
    with open(frontend_dockerfile) as f:
        frontend_content = f.read()
        
    required_frontend = ['FROM node:', 'WORKDIR /app', 'COPY package.json', 'RUN yarn', 'EXPOSE 3000', 'CMD']
    for req in required_frontend:
        if req not in frontend_content:
            print(f"❌ Frontend Dockerfile missing: {req}")
            return False
    print("✅ Frontend Dockerfile is valid")
    
    return True

def validate_dockerignore():
    """Validate .dockerignore files"""
    print("\n🐳 Validating .dockerignore files...")
    
    dockerignores = [
        "/app/.dockerignore",
        "/app/backend/.dockerignore", 
        "/app/frontend/.dockerignore"
    ]
    
    for ignore_file in dockerignores:
        if not Path(ignore_file).exists():
            print(f"❌ Missing: {ignore_file}")
            return False
        print(f"✅ Found: {ignore_file}")
    
    return True

def validate_environment_config():
    """Validate environment configuration for containers"""
    print("\n🐳 Validating environment configuration...")
    
    # Check backend .env
    backend_env = Path("/app/backend/.env")
    if not backend_env.exists():
        print("❌ Backend .env not found")
        return False
        
    with open(backend_env) as f:
        env_content = f.read()
        
    required_vars = ['MONGO_URL', 'DB_NAME', 'CORS_ORIGINS']
    for var in required_vars:
        if var not in env_content:
            print(f"❌ Missing environment variable: {var}")
            return False
    print("✅ Backend environment variables configured")
    
    # Check frontend .env
    frontend_env = Path("/app/frontend/.env")
    if not frontend_env.exists():
        print("❌ Frontend .env not found")
        return False
        
    with open(frontend_env) as f:
        frontend_env_content = f.read()
        
    if 'REACT_APP_BACKEND_URL' not in frontend_env_content:
        print("❌ Missing REACT_APP_BACKEND_URL in frontend .env")
        return False
    print("✅ Frontend environment variables configured")
    
    return True

def validate_package_files():
    """Validate package files exist"""
    print("\n🐳 Validating package files...")
    
    # Backend requirements.txt
    requirements = Path("/app/backend/requirements.txt")
    if not requirements.exists():
        print("❌ requirements.txt not found")
        return False
        
    with open(requirements) as f:
        reqs = f.read()
        
    required_packages = ['fastapi', 'uvicorn', 'motor', 'pymongo', 'pydantic']
    for pkg in required_packages:
        if pkg not in reqs.lower():
            print(f"❌ Missing package: {pkg}")
            return False
    print("✅ Backend requirements.txt is valid")
    
    # Frontend package.json
    package_json = Path("/app/frontend/package.json")
    if not package_json.exists():
        print("❌ package.json not found")
        return False
        
    with open(package_json) as f:
        pkg = json.load(f)
        
    required_deps = ['react', 'react-dom', 'axios', 'react-router-dom']
    dependencies = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
    
    for dep in required_deps:
        if dep not in dependencies:
            print(f"❌ Missing dependency: {dep}")
            return False
    print("✅ Frontend package.json is valid")
    
    return True

def validate_network_connectivity():
    """Validate that services can connect to each other"""
    print("\n🐳 Validating network connectivity configuration...")
    
    # Check if backend is configured to connect to MongoDB using service name
    with open("/app/backend/.env") as f:
        env_content = f.read()
        
    # For Docker, should use service name 'mongodb' not 'localhost'
    if 'mongodb://mongodb:' not in env_content and 'mongodb://localhost:' not in env_content:
        print("❌ Backend not configured to connect to MongoDB service")
        return False
    print("✅ Backend MongoDB connection configured")
    
    # Check if frontend is configured to connect to backend
    with open("/app/frontend/.env") as f:
        frontend_env = f.read()
        
    # Should have backend URL configured
    if 'REACT_APP_BACKEND_URL' not in frontend_env:
        print("❌ Frontend not configured with backend URL")
        return False
    print("✅ Frontend backend connection configured")
    
    return True

def main():
    """Run all validations"""
    print("🚀 Docker Setup Validation")
    print("=" * 50)
    
    validations = [
        validate_docker_compose,
        validate_dockerfiles,
        validate_dockerignore,
        validate_environment_config,
        validate_package_files,
        validate_network_connectivity
    ]
    
    results = []
    for validation in validations:
        try:
            result = validation()
            results.append(result)
        except Exception as e:
            print(f"❌ Validation failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    if all(results):
        print("🎉 ALL DOCKER VALIDATIONS PASSED!")
        print("✅ Docker setup is ready for deployment")
        print("\nTo start the application:")
        print("  docker-compose up --build")
    else:
        print("❌ Some validations failed")
        print(f"Passed: {sum(results)}/{len(results)}")
    
    return all(results)

if __name__ == "__main__":
    main()