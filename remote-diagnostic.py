#!/usr/bin/env python3
"""
Remote Service Diagnostic for AI Software Factory
Tests various endpoints to determine current deployment status
"""

import asyncio
import httpx
import sys
from typing import Dict, Any

async def test_endpoint(url: str, description: str) -> Dict[str, Any]:
    """Test a specific endpoint"""
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url)
            return {
                "url": url,
                "description": description,
                "status_code": response.status_code,
                "content_length": len(response.content),
                "is_nginx_welcome": b"Welcome to nginx" in response.content,
                "is_frontend": b"<!DOCTYPE html>" in response.content and not b"Welcome to nginx" in response.content,
                "success": response.status_code == 200
            }
    except Exception as e:
        return {
            "url": url,
            "description": description,
            "error": str(e),
            "success": False
        }

async def diagnose_deployment():
    """Run comprehensive deployment diagnosis"""
    print("🔍 AI Software Factory Remote Diagnostic")
    print("=" * 50)
    
    # Test various endpoints
    endpoints = [
        ("https://ai-staging.thetalogics.com", "Main Application"),
        ("https://ai-staging.thetalogics.com/api/v1/health", "Backend Health API"),
        ("https://ai-staging.thetalogics.com/api/", "Backend API Root"),
        ("https://ai-staging.thetalogics.com/health", "Health Check Endpoint"),
    ]
    
    results = []
    
    for url, description in endpoints:
        print(f"\nTesting {description}...")
        result = await test_endpoint(url, description)
        results.append(result)
        
        if "error" in result:
            print(f"  ❌ Error: {result['error']}")
        else:
            status_icon = "✅" if result["success"] else "⚠️"
            print(f"  {status_icon} Status: {result['status_code']}")
            print(f"  Content Length: {result['content_length']} bytes")
            if result["is_nginx_welcome"]:
                print("  🟨 Serving: Default nginx welcome page")
            elif result["is_frontend"]:
                print("  🟩 Serving: Frontend application")
            else:
                print("  🟦 Serving: Unknown content")
    
    # Analysis
    print("\n" + "=" * 50)
    print("📋 DIAGNOSTIC ANALYSIS")
    print("=" * 50)
    
    nginx_welcome_count = sum(1 for r in results if r.get("is_nginx_welcome", False))
    frontend_count = sum(1 for r in results if r.get("is_frontend", False))
    api_accessible = any(r["success"] and "/api/" in r["url"] for r in results)
    
    print(f"Nginx Welcome Pages: {nginx_welcome_count}")
    print(f"Frontend Applications: {frontend_count}")
    print(f"API Endpoints Accessible: {'✅' if api_accessible else '❌'}")
    
    if nginx_welcome_count > 0 and frontend_count == 0:
        print("\n🎯 ISSUE IDENTIFIED:")
        print("The nginx reverse proxy is serving default pages instead of forwarding to application containers.")
        print("\n🔧 RECOMMENDED ACTIONS:")
        print("1. Wait for Watchtower to deploy the updated configuration")
        print("2. Check container logs for startup issues")
        print("3. Verify network connectivity between containers")
        return False
    elif frontend_count > 0:
        print("\n🎉 SUCCESS: Application is accessible!")
        return True
    else:
        print("\n❓ UNCLEAR: Mixed results - manual investigation needed")
        return False

if __name__ == "__main__":
    success = asyncio.run(diagnose_deployment())
    sys.exit(0 if success else 1)