# Authentication Service API Documentation

## Overview
The Authentication Service provides secure user authentication, authorization, and session management for the AI Software Factory platform. It supports JWT tokens, OAuth2 integration, and role-based access control.

## Base URL
```
POST /api/v1/auth/login
POST /api/v1/auth/register
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
GET /api/v1/auth/me
POST /api/v1/auth/password/reset
POST /api/v1/auth/password/change
```

## Public Endpoints (No Authentication Required)

### User Registration
```
POST /api/v1/auth/register
```

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "company": "Acme Corp"  // Optional
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "user_1234567890abcdef",
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "is_verified": false,
    "created_at": "2024-01-15T10:30:00Z"
  },
  "message": "User registered successfully. Please check your email for verification."
}
```

### User Login
```
POST /api/v1/auth/login
```

**Request Body:**
```json
{
  "username": "johndoe",  // Can be username or email
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "refresh_1234567890abcdef...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": "user_1234567890abcdef",
      "username": "johndoe",
      "email": "john@example.com",
      "full_name": "John Doe",
      "roles": ["user"],
      "permissions": ["read:projects", "write:projects"]
    }
  },
  "message": "Login successful"
}
```

### Refresh Token
```
POST /api/v1/auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "refresh_1234567890abcdef..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

## Protected Endpoints (Authentication Required)

### Get Current User
```
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "user_1234567890abcdef",
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "company": "Acme Corp",
    "is_active": true,
    "is_verified": true,
    "is_superuser": false,
    "roles": ["user", "developer"],
    "permissions": [
      "read:projects",
      "write:projects",
      "read:deployments",
      "execute:deployments"
    ],
    "last_login": "2024-01-15T10:25:00Z",
    "created_at": "2024-01-01T09:00:00Z"
  }
}
```

### Logout
```
POST /api/v1/auth/logout
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "refresh_token": "refresh_1234567890abcdef..."  // Optional
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully logged out"
}
```

### Change Password
```
POST /api/v1/auth/password/change
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "current_password": "OldPassword123!",
  "new_password": "NewSecurePassword456!"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

### Reset Password Request
```
POST /api/v1/auth/password/reset
```

**Request Body:**
```json
{
  "email": "john@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password reset instructions sent to your email"
}
```

### Reset Password Confirm
```
POST /api/v1/auth/password/reset/confirm
```

**Request Body:**
```json
{
  "token": "reset_token_from_email...",
  "new_password": "NewSecurePassword456!"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password reset successfully"
}
```

## Token Management

### Access Token
- **Lifetime**: 1 hour (3600 seconds)
- **Purpose**: Authenticate API requests
- **Storage**: Should be stored securely (HTTP-only cookies recommended)
- **Format**: JWT with user claims and permissions

### Refresh Token
- **Lifetime**: 7 days (604800 seconds)
- **Purpose**: Obtain new access tokens without re-authentication
- **Storage**: Secure storage (database with encryption)
- **Rotation**: Rotated on each use for security

## JWT Token Structure

### Access Token Claims
```json
{
  "sub": "user_1234567890abcdef",
  "username": "johndoe",
  "email": "john@example.com",
  "roles": ["user", "developer"],
  "permissions": ["read:projects", "write:projects"],
  "exp": 1705318200,
  "iat": 1705314600,
  "jti": "token_1234567890abcdef"
}
```

### Refresh Token Claims
```json
{
  "sub": "user_1234567890abcdef",
  "token_type": "refresh",
  "exp": 1705923000,
  "iat": 1705318200,
  "jti": "refresh_1234567890abcdef"
}
```

## Role-Based Access Control

### Standard Roles
- `user`: Basic authenticated user
- `developer`: Can create and manage projects
- `admin`: Full system administration access
- `superuser`: Highest privilege level

### Permission Scopes
- `read:projects` - View project information
- `write:projects` - Create and modify projects
- `delete:projects` - Delete projects
- `read:deployments` - View deployment status
- `execute:deployments` - Trigger deployments
- `manage:users` - User management (admin only)
- `system:admin` - Full system access (superuser only)

## Security Features

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character
- Not a common password

### Rate Limiting
- 5 login attempts per minute per IP
- 3 password reset requests per hour per email
- 10 registration attempts per hour per IP

### Session Management
- Automatic logout after 24 hours of inactivity
- Concurrent session limit: 5 active sessions per user
- Session invalidation on password change

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": "Validation error",
  "details": [
    {
      "field": "password",
      "message": "Password must contain at least one uppercase letter"
    }
  ]
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "error": "Invalid credentials",
  "message": "Username or password is incorrect"
}
```

### 403 Forbidden
```json
{
  "success": false,
  "error": "Insufficient permissions",
  "message": "You don't have permission to perform this action"
}
```

### 429 Too Many Requests
```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after": 60
}
```

## OAuth2 Integration

### Google OAuth Login
```
GET /api/v1/auth/oauth/google
```

### GitHub OAuth Login
```
GET /api/v1/auth/oauth/github
```

### OAuth Callback
```
GET /api/v1/auth/oauth/callback?code=<authorization_code>&state=<state>
```

## Webhook Events

### user.registered
```json
{
  "event": "user.registered",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "user_id": "user_1234567890abcdef",
    "username": "johndoe",
    "email": "john@example.com",
    "registration_source": "direct"  // direct, google, github
  }
}
```

### user.logged_in
### user.password_changed
### user.account_locked

## Integration Examples

### Python Client with Automatic Token Refresh
```python
import requests
from datetime import datetime, timedelta

class AuthenticatedClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
    
    def authenticate(self):
        """Authenticate and get initial tokens"""
        response = requests.post(
            f"{self.base_url}/api/v1/auth/login",
            json={
                "username": self.username,
                "password": self.password
            }
        )
        
        if response.status_code == 200:
            data = response.json()["data"]
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
            self.token_expires_at = datetime.now() + timedelta(seconds=data["expires_in"])
            return True
        return False
    
    def ensure_authenticated(self):
        """Ensure we have a valid access token"""
        if not self.access_token or datetime.now() >= self.token_expires_at:
            if self.refresh_token:
                # Try to refresh
                response = requests.post(
                    f"{self.base_url}/api/v1/auth/refresh",
                    json={"refresh_token": self.refresh_token}
                )
                if response.status_code == 200:
                    data = response.json()["data"]
                    self.access_token = data["access_token"]
                    self.token_expires_at = datetime.now() + timedelta(seconds=data["expires_in"])
                    return True
            
            # Fall back to full authentication
            return self.authenticate()
        return True
    
    def make_request(self, method, endpoint, **kwargs):
        """Make authenticated request with automatic token refresh"""
        if not self.ensure_authenticated():
            raise Exception("Authentication failed")
        
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"
        
        response = requests.request(
            method,
            f"{self.base_url}{endpoint}",
            headers=headers,
            **kwargs
        )
        
        # Handle token expiration
        if response.status_code == 401:
            if self.ensure_authenticated():
                headers["Authorization"] = f"Bearer {self.access_token}"
                response = requests.request(
                    method,
                    f"{self.base_url}{endpoint}",
                    headers=headers,
                    **kwargs
                )
        
        return response

# Usage
client = AuthenticatedClient(
    "http://localhost:8000",
    "johndoe",
    "SecurePassword123!"
)

# Make authenticated requests
response = client.make_request("GET", "/api/v1/projects")
projects = response.json()
```

### React Hook for Authentication
```javascript
import { useState, useEffect } from 'react';

const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [accessToken, setAccessToken] = useState(localStorage.getItem('access_token'));
  
  const login = async (username, password) => {
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    if (response.ok) {
      const data = await response.json();
      const { access_token, refresh_token, user } = data.data;
      
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      setAccessToken(access_token);
      setUser(user);
      
      return { success: true };
    }
    
    return { success: false, error: await response.text() };
  };
  
  const logout = async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    await fetch('/api/v1/auth/logout', {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ refresh_token: refreshToken })
    });
    
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setAccessToken(null);
    setUser(null);
  };
  
  const getCurrentUser = async () => {
    if (!accessToken) return null;
    
    try {
      const response = await fetch('/api/v1/auth/me', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUser(data.data);
        return data.data;
      }
    } catch (error) {
      console.error('Failed to get current user:', error);
    }
    
    return null;
  };
  
  useEffect(() => {
    getCurrentUser().finally(() => setLoading(false));
  }, [accessToken]);
  
  return { user, loading, login, logout, isAuthenticated: !!user };
};

export default useAuth;
```