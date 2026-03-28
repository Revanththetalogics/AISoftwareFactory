# Project Service API Documentation

## Overview
The Project Service provides comprehensive project management capabilities for the AI Software Factory platform. It handles project lifecycle management, workflow orchestration, and integration with various development tools.

## Base URL
```
POST /api/v1/projects
GET /api/v1/projects/{project_id}
PUT /api/v1/projects/{project_id}
DELETE /api/v1/projects/{project_id}
GET /api/v1/projects
```

## Authentication
All endpoints require JWT Bearer token authentication:
```
Authorization: Bearer <jwt_token>
```

## Project Endpoints

### Create Project
```
POST /api/v1/projects
```

**Request Body:**
```json
{
  "name": "My AI Project",
  "description": "A cutting-edge AI application",
  "requirements": "Python 3.9+, FastAPI, PostgreSQL",
  "template": "fastapi-starter"  // Optional template to use
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "proj_1234567890abcdef",
    "name": "My AI Project",
    "description": "A cutting-edge AI application",
    "status": "active",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "owner_id": "user_1234567890abcdef"
  },
  "message": "Project created successfully"
}
```

### Get Project Details
```
GET /api/v1/projects/{project_id}
```

**Path Parameters:**
- `project_id` (string, required): The unique project identifier

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "proj_1234567890abcdef",
    "name": "My AI Project",
    "description": "A cutting-edge AI application",
    "status": "active",
    "progress_percent": 75,
    "repository_url": "https://github.com/user/my-ai-project",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T14:45:00Z",
    "owner": {
      "id": "user_1234567890abcdef",
      "username": "john_doe",
      "email": "john@example.com"
    },
    "team_members": [
      {
        "id": "user_0987654321fedcba",
        "username": "jane_smith",
        "role": "developer"
      }
    ],
    "workflows": [
      {
        "id": "wf_1234567890abcdef",
        "name": "Development Workflow",
        "status": "running"
      }
    ]
  }
}
```

### Update Project
```
PUT /api/v1/projects/{project_id}
```

**Request Body:**
```json
{
  "name": "Updated Project Name",
  "description": "Updated description",
  "status": "completed",
  "repository_url": "https://github.com/user/updated-repo"
}
```

### List Projects
```
GET /api/v1/projects
```

**Query Parameters:**
- `status` (string, optional): Filter by status (active, completed, archived)
- `owner_id` (string, optional): Filter by owner
- `page` (integer, optional): Page number (default: 1)
- `size` (integer, optional): Items per page (default: 20, max: 100)

**Response:**
```json
{
  "success": true,
  "data": {
    "projects": [
      {
        "id": "proj_1234567890abcdef",
        "name": "My AI Project",
        "description": "A cutting-edge AI application",
        "status": "active",
        "progress_percent": 75,
        "created_at": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 45,
      "pages": 3
    }
  }
}
```

### Delete Project
```
DELETE /api/v1/projects/{project_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Project deleted successfully"
}
```

## Project Status Values
- `draft`: Project is being planned
- `active`: Project is in development
- `paused`: Project development is temporarily suspended
- `completed`: Project development is finished
- `archived`: Project is archived for historical purposes

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": "Invalid project name",
  "message": "Project name must be between 3 and 100 characters"
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "error": "Authentication required",
  "message": "Valid JWT token is required"
}
```

### 403 Forbidden
```json
{
  "success": false,
  "error": "Access denied",
  "message": "You don't have permission to access this project"
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": "Project not found",
  "message": "Project with ID proj_1234567890abcdef does not exist"
}
```

### 422 Unprocessable Entity
```json
{
  "success": false,
  "error": "Validation error",
  "details": [
    {
      "field": "name",
      "message": "Field is required"
    }
  ]
}
```

## Rate Limiting
- 100 requests per minute per user
- 1000 requests per hour per user

## Webhook Events
The Project Service emits the following webhook events:

### project.created
```json
{
  "event": "project.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "project_id": "proj_1234567890abcdef",
    "name": "My AI Project",
    "owner_id": "user_1234567890abcdef"
  }
}
```

### project.updated
### project.deleted
### project.status_changed

## Integration Examples

### Python Client
```python
import requests

class ProjectClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def create_project(self, name, description, requirements=None):
        data = {
            "name": name,
            "description": description
        }
        if requirements:
            data["requirements"] = requirements
            
        response = requests.post(
            f"{self.base_url}/api/v1/projects",
            json=data,
            headers=self.headers
        )
        return response.json()
    
    def get_project(self, project_id):
        response = requests.get(
            f"{self.base_url}/api/v1/projects/{project_id}",
            headers=self.headers
        )
        return response.json()

# Usage
client = ProjectClient("http://localhost:8000", "your_jwt_token")
project = client.create_project(
    name="New AI Project",
    description="An innovative AI solution"
)
print(project)
```

### JavaScript/TypeScript Client
```typescript
interface Project {
  id: string;
  name: string;
  description: string;
  status: string;
}

class ProjectClient {
  constructor(private baseUrl: string, private token: string) {}
  
  async createProject(name: string, description: string): Promise<Project> {
    const response = await fetch(`${this.baseUrl}/api/v1/projects`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ name, description })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.data;
  }
  
  async getProject(projectId: string): Promise<Project> {
    const response = await fetch(`${this.baseUrl}/api/v1/projects/${projectId}`, {
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.data;
  }
}
```