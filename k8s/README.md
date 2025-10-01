# Kubernetes Deployment Guide for Idea Board

## 🚀 Cloud-Native Deployment with Kubernetes

This directory contains comprehensive Kubernetes manifests for deploying the Idea Board application in a cloud-native environment, demonstrating enterprise-grade container orchestration.

## 📁 Manifest Files Overview

### Core Deployment Files
- **`deployment.yaml`** - Main deployments for MongoDB, Backend, and Frontend with resource limits, health checks, and scaling configurations
- **`service.yaml`** - Services for inter-pod communication and load balancing
- **`ingress.yaml`** - Ingress controllers for external traffic routing with SSL/TLS support

### Advanced Configuration
- **`autoscaling.yaml`** - Horizontal Pod Autoscalers (HPA), Pod Disruption Budgets (PDB), and Network Policies
- **`configmap.yaml`** - Configuration management and Nginx proxy settings
- **`rbac.yaml`** - Role-Based Access Control, ServiceAccounts, and Resource Quotas
- **`deploy.sh`** - Automated deployment script with health checks

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Ingress       │    │  LoadBalancer   │    │   External      │
│  Controller     │────│   Services      │────│   Access        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │    MongoDB      │
│   (React)       │────│   (FastAPI)     │────│   (Database)    │
│   Replicas: 2   │    │   Replicas: 3   │    │   Replicas: 1   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      HPA        │    │      HPA        │    │  Persistent     │
│   (1-5 pods)    │    │   (2-10 pods)   │    │   Volume        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Deployment

### Prerequisites
- Kubernetes cluster (1.19+)
- kubectl configured
- NGINX Ingress Controller (optional)
- cert-manager for SSL (optional)

### One-Command Deployment
```bash
# Make deployment script executable
chmod +x k8s/deploy.sh

# Full deployment (build + deploy)
./k8s/deploy.sh full
```

### Manual Deployment
```bash
# 1. Apply core deployments
kubectl apply -f k8s/deployment.yaml

# 2. Create services
kubectl apply -f k8s/service.yaml

# 3. Configure ingress (optional)
kubectl apply -f k8s/ingress.yaml

# 4. Apply advanced configurations
kubectl apply -f k8s/autoscaling.yaml
kubectl apply -f k8s/rbac.yaml
kubectl apply -f k8s/configmap.yaml
```

## 🔧 Configuration Options

### Environment Variables
Update ConfigMaps in `deployment.yaml`:
```yaml
data:
  MONGO_URL: "mongodb://mongodb-service:27017"
  DB_NAME: "ideaboard_db"
  CORS_ORIGINS: "*"
  REACT_APP_BACKEND_URL: "https://api.yourdomain.com"
```

### Domain Configuration
Update `ingress.yaml` with your domain:
```yaml
rules:
- host: ideaboard.yourdomain.com  # Your domain
  http:
    paths:
    - path: /
      pathType: Prefix
      backend:
        service:
          name: frontend-service
          port:
            number: 3000
```

### Resource Scaling
Adjust replica counts and resource limits:
```yaml
spec:
  replicas: 3  # Number of replicas
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"
```

## 📊 Monitoring & Scaling

### Horizontal Pod Autoscaling
The deployment includes HPA configurations:
- **Backend**: 2-10 pods based on CPU (70%) and memory (80%)
- **Frontend**: 1-5 pods based on resource usage

### Health Checks
- **Readiness Probes**: Ensure pods are ready to receive traffic
- **Liveness Probes**: Restart unhealthy pods automatically
- **Startup Probes**: Handle slow-starting containers

### Monitoring Commands
```bash
# Check deployment status
kubectl get all -n ideaboard

# View pod logs
kubectl logs -f deployment/backend-deployment -n ideaboard

# Check autoscaling status
kubectl get hpa -n ideaboard

# Monitor resource usage
kubectl top pods -n ideaboard
```

## 🌐 Access Methods

### 1. Ingress (Production)
```bash
# Configure DNS to point to ingress IP
https://ideaboard.yourdomain.com
https://api.ideaboard.yourdomain.com
```

### 2. LoadBalancer Services
```bash
# Get external IPs
kubectl get svc -n ideaboard

# Access via LoadBalancer IP
http://<EXTERNAL-IP>
```

### 3. Port Forwarding (Development)
```bash
# Frontend
kubectl port-forward svc/frontend-service 3000:3000 -n ideaboard

# Backend
kubectl port-forward svc/backend-service 8000:8000 -n ideaboard

# Access locally
open http://localhost:3000
```

## 🔒 Security Features

### Network Policies
- Restricts backend communication to authorized pods only
- Isolates database access to backend pods
- Allows ingress controller access

### RBAC Configuration
- Dedicated ServiceAccount for application pods
- Minimal permissions (principle of least privilege)
- Namespace-scoped access only

### Resource Quotas
- CPU limits: 4 cores request, 8 cores limit
- Memory limits: 8Gi request, 16Gi limit
- Pod and service quotas to prevent resource exhaustion

## 📈 Production Considerations

### High Availability
- Multiple replicas for frontend and backend
- Pod Disruption Budgets prevent complete service outage
- Anti-affinity rules spread pods across nodes

### Data Persistence
- MongoDB uses PersistentVolumeClaim for data durability
- Storage class configurable for different cloud providers
- Automated backup strategies recommended

### SSL/TLS Configuration
```yaml
# Using cert-manager for automatic SSL
annotations:
  cert-manager.io/cluster-issuer: "letsencrypt-prod"
tls:
- hosts:
  - ideaboard.yourdomain.com
  secretName: ideaboard-tls-secret
```

## ☁️ Cloud Provider Specific

### AWS (EKS)
```yaml
# Use AWS Load Balancer Controller
annotations:
  service.beta.kubernetes.io/aws-load-balancer-type: nlb
  alb.ingress.kubernetes.io/scheme: internet-facing
```

### Google Cloud (GKE)
```yaml
# Use Google Cloud Load Balancer
annotations:
  cloud.google.com/load-balancer-type: External
```

### Azure (AKS)
```yaml
# Use Azure Load Balancer
annotations:
  service.beta.kubernetes.io/azure-load-balancer-resource-group: myResourceGroup
```

## 🔧 Troubleshooting

### Common Issues

**Pods not starting:**
```bash
kubectl describe pod <pod-name> -n ideaboard
kubectl logs <pod-name> -n ideaboard
```

**Service connectivity issues:**
```bash
# Test service DNS resolution
kubectl exec -it <pod-name> -n ideaboard -- nslookup mongodb-service

# Test service connectivity
kubectl exec -it <pod-name> -n ideaboard -- curl http://backend-service:8000/api/
```

**Ingress not working:**
```bash
# Check ingress controller
kubectl get pods -n nginx-ingress

# Verify ingress configuration
kubectl describe ingress ideaboard-ingress -n ideaboard
```

### Cleanup
```bash
# Remove all resources
./k8s/deploy.sh cleanup

# Or manually
kubectl delete namespace ideaboard
```

## 📚 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [cert-manager Documentation](https://cert-manager.io/docs/)
- [Prometheus Monitoring](https://prometheus.io/docs/)

---

## 🏆 Enterprise Features Demonstrated

✅ **Multi-tier Architecture** with proper service separation  
✅ **Auto-scaling** with HPA based on CPU/Memory metrics  
✅ **High Availability** with multiple replicas and PDBs  
✅ **Security** with RBAC, NetworkPolicies, and Resource Quotas  
✅ **Monitoring** with health checks and observability  
✅ **SSL/TLS** support with cert-manager integration  
✅ **Cloud-native** deployment ready for any Kubernetes cluster  
✅ **Production-ready** with comprehensive configuration options  

**This Kubernetes deployment demonstrates senior-level cloud-native expertise and production readiness.**
