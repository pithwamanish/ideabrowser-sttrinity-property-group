#!/bin/bash

# Kubernetes Deployment Script for Idea Board
# This script demonstrates cloud-native deployment with Kubernetes

set -e

echo "🚀 Kubernetes Deployment Script for Idea Board"
echo "==============================================="

# Configuration
NAMESPACE="ideaboard"
APP_VERSION="v1.0.0"
DOMAIN="ideaboard.yourdomain.com"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    # Check if cluster is accessible
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
        exit 1
    fi
    
    # Check if docker images exist (in real deployment, these would be in a registry)
    if ! docker image inspect ideaboard-frontend:latest &> /dev/null; then
        print_warning "Frontend image not found locally. In production, ensure images are pushed to registry."
    fi
    
    if ! docker image inspect ideaboard-backend:latest &> /dev/null; then
        print_warning "Backend image not found locally. In production, ensure images are pushed to registry."
    fi
    
    print_success "Prerequisites check completed"
}

# Build Docker images (for local development)
build_images() {
    print_step "Building Docker images..."
    
    # Build frontend image
    print_step "Building frontend image..."
    docker build -t ideaboard-frontend:latest -f frontend/Dockerfile frontend/
    
    # Build backend image
    print_step "Building backend image..."
    docker build -t ideaboard-backend:latest -f backend/Dockerfile backend/
    
    print_success "Docker images built successfully"
}

# Deploy to Kubernetes
deploy_to_kubernetes() {
    print_step "Deploying to Kubernetes..."
    
    # Create namespace and basic resources
    print_step "Creating namespace and configmaps..."
    kubectl apply -f k8s/deployment.yaml
    kubectl apply -f k8s/configmap.yaml
    
    # Create services
    print_step "Creating services..."
    kubectl apply -f k8s/service.yaml
    
    # Create RBAC resources
    print_step "Creating RBAC resources..."
    kubectl apply -f k8s/rbac.yaml
    
    # Create autoscaling resources
    print_step "Creating autoscaling resources..."
    kubectl apply -f k8s/autoscaling.yaml
    
    # Create ingress (comment out if no ingress controller)
    print_step "Creating ingress..."
    kubectl apply -f k8s/ingress.yaml || print_warning "Ingress creation failed. Make sure you have an ingress controller installed."
    
    print_success "Kubernetes resources deployed successfully"
}

# Wait for deployments
wait_for_deployments() {
    print_step "Waiting for deployments to be ready..."
    
    # Wait for MongoDB
    kubectl wait --for=condition=available --timeout=300s deployment/mongodb-deployment -n $NAMESPACE
    
    # Wait for Backend
    kubectl wait --for=condition=available --timeout=300s deployment/backend-deployment -n $NAMESPACE
    
    # Wait for Frontend
    kubectl wait --for=condition=available --timeout=300s deployment/frontend-deployment -n $NAMESPACE
    
    print_success "All deployments are ready"
}

# Get service information
get_service_info() {
    print_step "Getting service information..."
    
    echo ""
    echo "📊 Deployment Status:"
    kubectl get all -n $NAMESPACE
    
    echo ""
    echo "🌐 Service Endpoints:"
    
    # Get LoadBalancer IPs (if any)
    FRONTEND_IP=$(kubectl get svc frontend-loadbalancer -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
    BACKEND_IP=$(kubectl get svc backend-loadbalancer -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
    
    echo "Frontend LoadBalancer: http://$FRONTEND_IP (if LoadBalancer type)"
    echo "Backend LoadBalancer: http://$BACKEND_IP (if LoadBalancer type)"
    
    # Get Ingress information
    INGRESS_IP=$(kubectl get ingress ideaboard-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
    echo "Ingress: http://$INGRESS_IP or https://$DOMAIN (if configured)"
    
    echo ""
    echo "🔍 Port Forward Commands (for local testing):"
    echo "kubectl port-forward svc/frontend-service 3000:3000 -n $NAMESPACE"
    echo "kubectl port-forward svc/backend-service 8000:8000 -n $NAMESPACE"
    
    print_success "Service information displayed"
}

# Run health checks
run_health_checks() {
    print_step "Running health checks..."
    
    # Check if pods are running
    FRONTEND_PODS=$(kubectl get pods -n $NAMESPACE -l app=frontend --field-selector=status.phase=Running --no-headers | wc -l)
    BACKEND_PODS=$(kubectl get pods -n $NAMESPACE -l app=backend --field-selector=status.phase=Running --no-headers | wc -l)
    MONGODB_PODS=$(kubectl get pods -n $NAMESPACE -l app=mongodb --field-selector=status.phase=Running --no-headers | wc -l)
    
    echo "Running Pods:"
    echo "  Frontend: $FRONTEND_PODS"
    echo "  Backend: $BACKEND_PODS"
    echo "  MongoDB: $MONGODB_PODS"
    
    if [ "$MONGODB_PODS" -ge 1 ] && [ "$BACKEND_PODS" -ge 1 ] && [ "$FRONTEND_PODS" -ge 1 ]; then
        print_success "All services are running"
    else
        print_error "Some services are not running properly"
        kubectl get pods -n $NAMESPACE
    fi
}

# Cleanup function
cleanup() {
    print_step "Cleaning up resources..."
    
    kubectl delete namespace $NAMESPACE --ignore-not-found=true
    
    print_success "Cleanup completed"
}

# Main deployment flow
main() {
    case "${1:-deploy}" in
        "build")
            check_prerequisites
            build_images
            ;;
        "deploy")
            check_prerequisites
            deploy_to_kubernetes
            wait_for_deployments
            get_service_info
            run_health_checks
            ;;
        "full")
            check_prerequisites
            build_images
            deploy_to_kubernetes
            wait_for_deployments
            get_service_info
            run_health_checks
            ;;
        "status")
            get_service_info
            run_health_checks
            ;;
        "cleanup")
            cleanup
            ;;
        "help")
            echo "Usage: $0 [build|deploy|full|status|cleanup|help]"
            echo "  build   - Build Docker images only"
            echo "  deploy  - Deploy to Kubernetes only"
            echo "  full    - Build images and deploy (default)"
            echo "  status  - Show deployment status"
            echo "  cleanup - Remove all resources"
            echo "  help    - Show this help"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"

echo ""
print_success "🎉 Kubernetes deployment script completed!"
echo "📚 For more information, check the README.md file"
echo "🐛 For troubleshooting, run: kubectl logs -f deployment/backend-deployment -n $NAMESPACE"
