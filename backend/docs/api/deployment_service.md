# Deployment Service API Documentation

## Overview
The Deployment Service manages application deployment workflows, environment provisioning, and deployment monitoring for the AI Software Factory platform. It supports multiple deployment targets and provides real-time deployment status tracking.

## Base URL
```
POST /api/v1/deployments
GET /api/v1/deployments/{deployment_id}
GET /api/v1/deployments
GET /api/v1/projects/{project_id}/deployments
POST /api/v1/deployments/{deployment_id}/rollback
```

## Authentication
All endpoints require JWT Bearer token authentication:
```
Authorization: Bearer <jwt_token>
```

## Deployment Endpoints

### Create Deployment
```
POST /api/v1/deployments
```

**Request Body:**
```json
{
  "project_id": "proj_1234567890abcdef",
  "environment": "production",
  "branch": "main",
  "target": {
    "type": "docker",  // docker, kubernetes, lambda, vm
    "configuration": {
      "image": "my-app:latest",
      "ports": [8000],
      "environment_variables": {
        "DATABASE_URL": "postgresql://...",
        "REDIS_URL": "redis://..."
      },
      "resources": {
        "cpu": "1000m",
        "memory": "2Gi"
      }
    }
  },
  "strategy": "blue-green",  // rolling, blue-green, recreate
  "auto_rollback": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "deploy_1234567890abcdef",
    "project_id": "proj_1234567890abcdef",
    "environment": "production",
    "status": "pending",
    "branch": "main",
    "created_at": "2024-01-15T10:30:00Z",
    "started_at": null,
    "finished_at": null,
    "created_by": "user_1234567890abcdef"
  },
  "message": "Deployment initiated successfully"
}
```

### Get Deployment Details
```
GET /api/v1/deployments/{deployment_id}
```

**Path Parameters:**
- `deployment_id` (string, required): The unique deployment identifier

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "deploy_1234567890abcdef",
    "project_id": "proj_1234567890abcdef",
    "environment": "production",
    "status": "running",
    "branch": "main",
    "strategy": "blue-green",
    "target": {
      "type": "kubernetes",
      "namespace": "production",
      "service_name": "my-app-service"
    },
    "progress": {
      "current_step": "deploy_containers",
      "total_steps": 5,
      "completed_steps": 3,
      "percentage": 60
    },
    "logs": [
      {
        "timestamp": "2024-01-15T10:30:01Z",
        "level": "info",
        "message": "Starting deployment process"
      },
      {
        "timestamp": "2024-01-15T10:30:05Z",
        "level": "info",
        "message": "Building Docker image"
      }
    ],
    "created_at": "2024-01-15T10:30:00Z",
    "started_at": "2024-01-15T10:30:01Z",
    "finished_at": null
  }
}
```

### List Deployments
```
GET /api/v1/deployments
GET /api/v1/projects/{project_id}/deployments
```

**Query Parameters:**
- `project_id` (string, optional): Filter by project
- `environment` (string, optional): Filter by environment (dev, staging, production)
- `status` (string, optional): Filter by status (pending, running, success, failed, cancelled)
- `page` (integer, optional): Page number (default: 1)
- `size` (integer, optional): Items per page (default: 20, max: 100)

**Response:**
```json
{
  "success": true,
  "data": {
    "deployments": [
      {
        "id": "deploy_1234567890abcdef",
        "project_id": "proj_1234567890abcdef",
        "project_name": "My AI Project",
        "environment": "production",
        "status": "success",
        "branch": "main",
        "duration_seconds": 345,
        "created_at": "2024-01-15T10:30:00Z",
        "finished_at": "2024-01-15T10:35:45Z"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 15,
      "pages": 1
    }
  }
}
```

### Rollback Deployment
```
POST /api/v1/deployments/{deployment_id}/rollback
```

**Request Body:**
```json
{
  "reason": "Critical bug found in production",
  "target_version": "v1.2.0"  // Optional: specific version to rollback to
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "deploy_0987654321fedcba",
    "project_id": "proj_1234567890abcdef",
    "environment": "production",
    "status": "pending",
    "type": "rollback",
    "rollback_target": "deploy_1234567890abcdef",
    "created_at": "2024-01-15T11:00:00Z"
  },
  "message": "Rollback deployment initiated"
}
```

## Deployment Status Values
- `pending`: Deployment is queued and waiting to start
- `running`: Deployment is currently in progress
- `success`: Deployment completed successfully
- `failed`: Deployment failed with errors
- `cancelled`: Deployment was manually cancelled
- `rolling_back`: Automatic rollback in progress due to failure

## Deployment Targets

### Docker
```json
{
  "type": "docker",
  "configuration": {
    "image": "my-app:latest",
    "ports": [8000, 8001],
    "environment_variables": {
      "PORT": "8000",
      "DEBUG": "false"
    },
    "volumes": [
      {
        "host_path": "/var/data",
        "container_path": "/app/data"
      }
    ],
    "network": "bridge"
  }
}
```

### Kubernetes
```json
{
  "type": "kubernetes",
  "configuration": {
    "namespace": "production",
    "deployment_name": "my-app",
    "service_name": "my-app-service",
    "replicas": 3,
    "resources": {
      "requests": {
        "cpu": "500m",
        "memory": "1Gi"
      },
      "limits": {
        "cpu": "1000m",
        "memory": "2Gi"
      }
    },
    "ingress": {
      "enabled": true,
      "host": "myapp.example.com",
      "tls": true
    }
  }
}
```

### AWS Lambda
```json
{
  "type": "lambda",
  "configuration": {
    "function_name": "my-app-handler",
    "runtime": "python3.9",
    "handler": "main.handler",
    "memory_size": 512,
    "timeout": 30,
    "environment_variables": {
      "LOG_LEVEL": "INFO"
    }
  }
}
```

## Deployment Strategies

### Rolling Update
Gradually replaces instances with new versions, minimizing downtime.

### Blue-Green
Maintains two identical environments and switches traffic between them.

### Recreate
Destroys all old instances before creating new ones (causes downtime).

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": "Invalid deployment configuration",
  "message": "Missing required field: target.configuration.image"
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": "Deployment not found",
  "message": "Deployment with ID deploy_1234567890abcdef does not exist"
}
```

### 409 Conflict
```json
{
  "success": false,
  "error": "Deployment in progress",
  "message": "Another deployment is already running for this project/environment"
}
```

## Webhook Events

### deployment.started
```json
{
  "event": "deployment.started",
  "timestamp": "2024-01-15T10:30:01Z",
  "data": {
    "deployment_id": "deploy_1234567890abcdef",
    "project_id": "proj_1234567890abcdef",
    "environment": "production"
  }
}
```

### deployment.completed
### deployment.failed
### deployment.cancelled
### deployment.rollback_started

## Monitoring and Metrics

The deployment service provides real-time metrics:

### Deployment Metrics Endpoint
```
GET /api/v1/deployments/metrics
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_deployments": 142,
    "successful_deployments": 138,
    "failed_deployments": 4,
    "average_deployment_time": 287,
    "success_rate": 97.2,
    "active_deployments": 2,
    "environments": {
      "production": {
        "total": 45,
        "success_rate": 95.6
      },
      "staging": {
        "total": 67,
        "success_rate": 98.5
      }
    }
  }
}
```

## Integration Examples

### Python Client
```python
import requests
import time

class DeploymentClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def deploy(self, project_id, environment, branch="main"):
        data = {
            "project_id": project_id,
            "environment": environment,
            "branch": branch,
            "target": {
                "type": "docker",
                "configuration": {
                    "image": f"my-app:{branch}",
                    "ports": [8000]
                }
            },
            "strategy": "rolling",
            "auto_rollback": True
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/deployments",
            json=data,
            headers=self.headers
        )
        return response.json()
    
    def monitor_deployment(self, deployment_id, poll_interval=5):
        while True:
            response = requests.get(
                f"{self.base_url}/api/v1/deployments/{deployment_id}",
                headers=self.headers
            )
            data = response.json()
            
            status = data["data"]["status"]
            if status in ["success", "failed", "cancelled"]:
                return data
            
            print(f"Deployment status: {status}")
            time.sleep(poll_interval)

# Usage
client = DeploymentClient("http://localhost:8000", "your_jwt_token")
result = client.deploy("proj_1234567890abcdef", "production")
deployment_id = result["data"]["id"]
final_status = client.monitor_deployment(deployment_id)
print(f"Deployment finished with status: {final_status['data']['status']}")
```

### Automated Deployment Pipeline
```yaml
# GitHub Actions workflow example
name: Deploy to Production
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy Application
        run: |
          curl -X POST \
            -H "Authorization: Bearer ${{ secrets.API_TOKEN }}" \
            -H "Content-Type: application/json" \
            -d '{
              "project_id": "${{ secrets.PROJECT_ID }}",
              "environment": "production",
              "branch": "${{ github.ref_name }}",
              "target": {
                "type": "kubernetes",
                "configuration": {
                  "namespace": "production",
                  "deployment_name": "my-app"
                }
              }
            }' \
            https://api.theta-ai.com/api/v1/deployments
```