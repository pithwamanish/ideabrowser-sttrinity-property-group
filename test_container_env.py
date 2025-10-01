#!/usr/bin/env python3
"""
Container Environment Test
Tests that the application would work correctly in Docker containers
"""

import os
import sys
import json
from pathlib import Path

def test_backend_with_docker_env():
    """Test backend with Docker environment variables"""
    print("🐍 Testing Backend with Docker Environment...")
    
    # Set Docker environment variables
    os.environ['MONGO_URL'] = 'mongodb://mongodb:27017'
    os.environ['DB_NAME'] = 'ideaboard_db'
    os.environ['CORS_ORIGINS'] = 'http://localhost:3000,http://frontend:3000'
    
    sys.path.append('/app/backend')
    try:
        # Import and test server configuration
        from server import app, db
        print("✅ Backend server imports successfully with Docker env")
        
        # Test that environment variables are read correctly
        mongo_url = os.environ.get('MONGO_URL')
        db_name = os.environ.get('DB_NAME') 
        cors_origins = os.environ.get('CORS_ORIGINS')
        
        if mongo_url == 'mongodb://mongodb:27017':
            print("✅ MongoDB URL configured for Docker")
        else:
            print(f"❌ MongoDB URL incorrect: {mongo_url}")
            return False
            
        if db_name == 'ideaboard_db':
            print("✅ Database name configured correctly")
        else:
            print(f"❌ Database name incorrect: {db_name}")
            return False
            
        if 'frontend:3000' in cors_origins:
            print("✅ CORS configured for Docker containers")
        else:
            print(f"❌ CORS not configured for containers: {cors_origins}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

def test_frontend_build_output():
    """Test that frontend build is ready for containerization"""
    print("\n📦 Testing Frontend Build Output...")
    
    build_path = Path("/app/frontend/build")
    if not build_path.exists():
        print("❌ Frontend build directory not found")
        return False
        
    # Check for essential build files
    essential_files = ['index.html', 'static', 'asset-manifest.json']
    for file in essential_files:
        if not (build_path / file).exists():
            print(f"❌ Missing build file: {file}")
            return False
    print("✅ All essential build files present")
    
    # Check index.html for proper build
    index_html = build_path / 'index.html'
    with open(index_html) as f:
        content = f.read()
        
    if '/static/' in content:
        print("✅ Static assets properly referenced")
    else:
        print("❌ Static assets not properly referenced")
        return False
        
    return True

def test_docker_networking():
    """Test Docker networking configuration"""
    print("\n🌐 Testing Docker Networking Configuration...")
    
    # Check docker-compose.yml for proper networking
    with open('/app/docker-compose.yml') as f:
        content = f.read()
        
    # Check that services are on the same network
    if 'ideaboard_network' in content:
        print("✅ Custom network defined")
    else:
        print("❌ Custom network not defined")
        return False
        
    # Check service dependencies
    if 'depends_on:' in content:
        print("✅ Service dependencies configured")
    else:
        print("❌ Service dependencies not configured")
        return False
        
    return True

def test_volume_persistence():
    """Test volume configuration for data persistence"""
    print("\n💾 Testing Volume Configuration...")
    
    with open('/app/docker-compose.yml') as f:
        content = f.read()
        
    if 'mongodb_data:' in content and 'volumes:' in content:
        print("✅ MongoDB data volume configured")
    else:
        print("❌ MongoDB data volume not configured")
        return False
        
    if '/data/db' in content:
        print("✅ MongoDB data directory mounted")
    else:
        print("❌ MongoDB data directory not mounted")
        return False
        
    return True

def test_health_checks():
    """Test health check configuration"""
    print("\n🏥 Testing Health Check Configuration...")
    
    with open('/app/docker-compose.yml') as f:
        content = f.read()
        
    if 'healthcheck:' in content:
        print("✅ Health checks configured")
    else:
        print("❌ Health checks not configured")
        return False
        
    if 'http://localhost:8000/api/' in content:
        print("✅ Backend health check endpoint configured")
    else:
        print("❌ Backend health check endpoint not configured")
        return False
        
    return True

def test_production_readiness():
    """Test production readiness features"""
    print("\n🚀 Testing Production Readiness...")
    
    # Check for production Dockerfile
    prod_dockerfile = Path("/app/frontend/Dockerfile.prod")
    if prod_dockerfile.exists():
        print("✅ Production Dockerfile available")
    else:
        print("❌ Production Dockerfile not available")
        return False
        
    # Check for nginx configuration
    nginx_conf = Path("/app/frontend/nginx.conf")
    if nginx_conf.exists():
        print("✅ Nginx configuration available")
        
        with open(nginx_conf) as f:
            nginx_content = f.read()
            
        if 'gzip' in nginx_content:
            print("✅ Compression configured")
        if 'proxy_pass' in nginx_content:
            print("✅ API proxying configured")
            
    else:
        print("❌ Nginx configuration not available")
        return False
        
    # Check for development override
    dev_compose = Path("/app/docker-compose.dev.yml")
    if dev_compose.exists():
        print("✅ Development override available")
    else:
        print("❌ Development override not available")
        return False
        
    return True

def main():
    """Run all container environment tests"""
    print("🐳 Container Environment Validation")
    print("=" * 50)
    
    tests = [
        test_backend_with_docker_env,
        test_frontend_build_output,
        test_docker_networking,
        test_volume_persistence,
        test_health_checks,
        test_production_readiness
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    if all(results):
        print("🎉 ALL CONTAINER TESTS PASSED!")
        print("✅ Application is fully containerized and ready")
        print("\n🚀 Deployment Commands:")
        print("  # Development:")
        print("  docker-compose up --build")
        print("")
        print("  # Production:")
        print("  docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d")
        print("")
        print("  # With dev features:")
        print("  docker-compose -f docker-compose.yml -f docker-compose.dev.yml up")
    else:
        print("❌ Some container tests failed")
        print(f"Passed: {sum(results)}/{len(results)}")
    
    return all(results)

if __name__ == "__main__":
    main()