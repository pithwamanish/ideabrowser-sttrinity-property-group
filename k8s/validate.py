#!/usr/bin/env python3
"""
Kubernetes Manifests Validator
Validates all Kubernetes manifests for correctness and best practices
"""

import yaml
import os
import json
from pathlib import Path

def validate_yaml_syntax(file_path):
    """Validate YAML syntax"""
    try:
        with open(file_path, 'r') as f:
            docs = list(yaml.safe_load_all(f))
        return True, len(docs)
    except yaml.YAMLError as e:
        return False, str(e)

def validate_kubernetes_resources(file_path):
    """Validate Kubernetes resource structure"""
    issues = []
    
    try:
        with open(file_path, 'r') as f:
            docs = list(yaml.safe_load_all(f))
        
        for doc in docs:
            if doc is None:
                continue
                
            # Check required fields
            if 'apiVersion' not in doc:
                issues.append(f"Missing apiVersion in {file_path}")
            if 'kind' not in doc:
                issues.append(f"Missing kind in {file_path}")
            if 'metadata' not in doc:
                issues.append(f"Missing metadata in {file_path}")
            elif 'name' not in doc['metadata']:
                issues.append(f"Missing metadata.name in {file_path}")
            
            # Check namespace consistency
            if 'namespace' in doc.get('metadata', {}):
                if doc['metadata']['namespace'] != 'ideaboard':
                    issues.append(f"Inconsistent namespace in {file_path}: {doc['metadata']['namespace']}")
    
    except Exception as e:
        issues.append(f"Error parsing {file_path}: {str(e)}")
    
    return issues

def validate_resource_references(k8s_dir):
    """Validate cross-resource references"""
    issues = []
    services = set()
    deployments = set()
    configmaps = set()
    secrets = set()
    
    # Collect all resources
    for yaml_file in k8s_dir.glob('*.yaml'):
        if yaml_file.name in ['README.md']:
            continue
            
        try:
            with open(yaml_file, 'r') as f:
                docs = list(yaml.safe_load_all(f))
            
            for doc in docs:
                if doc is None:
                    continue
                
                kind = doc.get('kind', '')
                name = doc.get('metadata', {}).get('name', '')
                
                if kind == 'Service':
                    services.add(name)
                elif kind == 'Deployment':
                    deployments.add(name)
                elif kind == 'ConfigMap':
                    configmaps.add(name)
                elif kind == 'Secret':
                    secrets.add(name)
        
        except Exception as e:
            issues.append(f"Error processing {yaml_file}: {str(e)}")
    
    # Validate references
    expected_services = {'mongodb-service', 'backend-service', 'frontend-service'}
    expected_deployments = {'mongodb-deployment', 'backend-deployment', 'frontend-deployment'}
    expected_configmaps = {'backend-config', 'frontend-config'}
    
    for expected in expected_services:
        if expected not in services:
            issues.append(f"Missing expected service: {expected}")
    
    for expected in expected_deployments:
        if expected not in deployments:
            issues.append(f"Missing expected deployment: {expected}")
    
    for expected in expected_configmaps:
        if expected not in configmaps:
            issues.append(f"Missing expected configmap: {expected}")
    
    return issues

def validate_resource_limits():
    """Validate resource limits and requests"""
    issues = []
    
    deployment_file = Path('/app/k8s/deployment.yaml')
    if deployment_file.exists():
        with open(deployment_file, 'r') as f:
            docs = list(yaml.safe_load_all(f))
        
        for doc in docs:
            if doc and doc.get('kind') == 'Deployment':
                containers = doc.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [])
                
                for container in containers:
                    resources = container.get('resources', {})
                    if not resources:
                        issues.append(f"No resources defined for container {container.get('name')} in {doc['metadata']['name']}")
                    else:
                        if 'requests' not in resources:
                            issues.append(f"No resource requests for container {container.get('name')}")
                        if 'limits' not in resources:
                            issues.append(f"No resource limits for container {container.get('name')}")
    
    return issues

def validate_health_checks():
    """Validate health check configurations"""
    issues = []
    
    deployment_file = Path('/app/k8s/deployment.yaml')
    if deployment_file.exists():
        with open(deployment_file, 'r') as f:
            docs = list(yaml.safe_load_all(f))
        
        for doc in docs:
            if doc and doc.get('kind') == 'Deployment':
                containers = doc.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [])
                
                for container in containers:
                    name = container.get('name', 'unknown')
                    
                    if 'readinessProbe' not in container:
                        issues.append(f"No readiness probe for container {name}")
                    
                    if 'livenessProbe' not in container:
                        issues.append(f"No liveness probe for container {name}")
    
    return issues

def main():
    """Main validation function"""
    print("🔍 Kubernetes Manifests Validation")
    print("=" * 50)
    
    k8s_dir = Path('/app/k8s')
    if not k8s_dir.exists():
        print("❌ k8s directory not found")
        return False
    
    total_issues = 0
    yaml_files = list(k8s_dir.glob('*.yaml'))
    
    print(f"📁 Found {len(yaml_files)} YAML files")
    print()
    
    # Validate YAML syntax
    print("🔍 Validating YAML Syntax:")
    for yaml_file in yaml_files:
        valid, result = validate_yaml_syntax(yaml_file)
        if valid:
            print(f"✅ {yaml_file.name}: Valid ({result} documents)")
        else:
            print(f"❌ {yaml_file.name}: Invalid - {result}")
            total_issues += 1
    
    print()
    
    # Validate Kubernetes resources
    print("🔍 Validating Kubernetes Resources:")
    for yaml_file in yaml_files:
        issues = validate_kubernetes_resources(yaml_file)
        if not issues:
            print(f"✅ {yaml_file.name}: Valid Kubernetes resources")
        else:
            print(f"❌ {yaml_file.name}: Issues found:")
            for issue in issues:
                print(f"   - {issue}")
            total_issues += len(issues)
    
    print()
    
    # Validate resource references
    print("🔍 Validating Resource References:")
    ref_issues = validate_resource_references(k8s_dir)
    if not ref_issues:
        print("✅ All resource references are valid")
    else:
        print("❌ Resource reference issues:")
        for issue in ref_issues:
            print(f"   - {issue}")
        total_issues += len(ref_issues)
    
    print()
    
    # Validate resource limits
    print("🔍 Validating Resource Limits:")
    limit_issues = validate_resource_limits()
    if not limit_issues:
        print("✅ Resource limits properly configured")
    else:
        print("❌ Resource limit issues:")
        for issue in limit_issues:
            print(f"   - {issue}")
        total_issues += len(limit_issues)
    
    print()
    
    # Validate health checks
    print("🔍 Validating Health Checks:")
    health_issues = validate_health_checks()
    if not health_issues:
        print("✅ Health checks properly configured")
    else:
        print("❌ Health check issues:")
        for issue in health_issues:
            print(f"   - {issue}")
        total_issues += len(health_issues)
    
    print()
    print("=" * 50)
    
    if total_issues == 0:
        print("🎉 ALL KUBERNETES MANIFESTS ARE VALID!")
        print("✅ Ready for production deployment")
        print()
        print("🚀 Deployment Commands:")
        print("   # Full deployment")
        print("   ./k8s/deploy.sh full")
        print()
        print("   # Manual deployment")
        print("   kubectl apply -f k8s/")
        return True
    else:
        print(f"❌ Found {total_issues} issues that need to be addressed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)