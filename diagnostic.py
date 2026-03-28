#!/usr/bin/env python3
"""
Comprehensive Diagnostic Script for AI Software Factory
Checks container status, network connectivity, and service health
"""

import asyncio
import httpx
import socket
import sys
from typing import Dict, Any

async def check_port_connectivity(host: str, port: int, service_name: str) -> Dict[str, Any]:
    """Check if a port is open and accepting connections"""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), 
            timeout=5.0
        )
        writer.close()
        await writer.wait_closed()
        return {
            "status": "success",
            "message": f"{service_name} port {port} is accessible",
            "host": host,
            "port": port
        }
    except asyncio.TimeoutError:
        return {
            "status": "error",
            "message": f"{service_name} port {port} connection timed out",
            "host": host,
            "port": port
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"{service_name} port {port} connection failed: {str(e)}",
            "host": host,
            "port": port
        }

async def test_direct_backend_access() -> Dict[str, Any]:
    """Test direct access to backend service"""
    # Try to connect to backend container directly
    tests = [
        ("localhost", 8000, "Local Backend"),
        ("backend", 8000, "Backend Container"),  # This would work inside docker network
    ]
    
    results = []
    for host, port, service_name in tests:
        result = await check_port_connectivity(host, port, service_name)
        results.append(result)
        
        if result["status"] == "success":
            # Try to get health endpoint
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"http://{host}:{port}/api/v1/health")
                    if response.status_code == 200:
                        return {
                            "status": "success",
                            "message": f"Direct backend access successful via {host}:{port}",
                            "health_data": response.json(),
                            "endpoint": f"http://{host}:{port}/api/v1/health"
                        }
            except Exception:
                pass
    
    # If no direct access worked
    failed_results = [r for r in results if r["status"] == "error"]
    if failed_results:
        return {
            "status": "error",
            "message": "Cannot access backend directly: " + "; ".join([r["message"] for r in failed_results])
        }
    
    return {
        "status": "warning",
        "message": "Backend ports accessible but health endpoint unavailable"
    }

async def test_dns_resolution(hostname: str) -> Dict[str, Any]:
    """Test DNS resolution for a hostname"""
    try:
        ip_addresses = socket.getaddrinfo(hostname, None)
        ips = [addr[4][0] for addr in ip_addresses]
        return {
            "status": "success",
            "message": f"DNS resolution successful for {hostname}",
            "ips": ips
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"DNS resolution failed for {hostname}: {str(e)}"
        }

async def comprehensive_diagnostics():
    """Run comprehensive diagnostics"""
    print("🔍 AI Software Factory - Comprehensive Diagnostics")
    print("=" * 60)
    
    # Test DNS resolution
    print("\n📡 DNS Resolution Tests:")
    dns_tests = [
        ("ai-staging.thetalogics.com", "Production Domain"),
        ("localhost", "Localhost"),
        ("backend", "Backend Service"),
        ("frontend", "Frontend Service")
    ]
    
    dns_results = []
    for hostname, description in dns_tests:
        result = await test_dns_resolution(hostname)
        dns_results.append((description, result))
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"  {status_icon} {description} ({hostname}): {result['message']}")
    
    # Test port connectivity
    print("\n🔌 Port Connectivity Tests:")
    port_tests = [
        ("ai-staging.thetalogics.com", 80, "Production HTTP"),
        ("ai-staging.thetalogics.com", 443, "Production HTTPS"),
        ("localhost", 8000, "Local Backend"),
        ("localhost", 3000, "Local Frontend")
    ]
    
    port_results = []
    for host, port, description in port_tests:
        result = await check_port_connectivity(host, port, description)
        port_results.append((description, result))
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"  {status_icon} {description}: {result['message']}")
    
    # Test direct backend access
    print("\n🔧 Backend Direct Access Test:")
    backend_result = await test_direct_backend_access()
    status_icon = "✅" if backend_result["status"] == "success" else "❌"
    print(f"  {status_icon} {backend_result['message']}")
    if "health_data" in backend_result:
        print(f"    Health Status: {backend_result['health_data'].get('status', 'Unknown')}")
    
    # Test API endpoint discovery
    print("\n🌐 API Endpoint Discovery:")
    base_urls = [
        "https://ai-staging.thetalogics.com",
        "http://localhost:3000",
        "http://localhost:8000"
    ]
    
    possible_endpoints = [
        "/api/v1/health",
        "/api/health",
        "/health",
        "/api/v1/",
        "/api/"
    ]
    
    found_endpoints = []
    for base_url in base_urls:
        print(f"  Testing {base_url}:")
        async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
            for endpoint in possible_endpoints:
                try:
                    full_url = f"{base_url}{endpoint}"
                    response = await client.get(full_url)
                    if response.status_code == 200:
                        found_endpoints.append(full_url)
                        print(f"    ✅ {endpoint} - Status: {response.status_code}")
                    elif response.status_code != 404:
                        print(f"    ⚠️  {endpoint} - Status: {response.status_code}")
                except Exception as e:
                    print(f"    ❌ {endpoint} - Error: {str(e)[:50]}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 DIAGNOSTICS SUMMARY")
    print("=" * 60)
    
    total_tests = len(dns_results) + len(port_results) + 1 + (len(base_urls) * len(possible_endpoints))
    successful_dns = sum(1 for _, result in dns_results if result["status"] == "success")
    successful_ports = sum(1 for _, result in port_results if result["status"] == "success")
    successful_backend = 1 if backend_result["status"] == "success" else 0
    successful_endpoints = len(found_endpoints)
    
    print(f"DNS Resolution: {successful_dns}/{len(dns_results)} passed")
    print(f"Port Connectivity: {successful_ports}/{len(port_results)} passed")
    print(f"Backend Access: {'✅' if successful_backend else '❌'}")
    print(f"API Endpoints Found: {successful_endpoints}")
    
    if found_endpoints:
        print("\n📍 Available API Endpoints:")
        for endpoint in found_endpoints:
            print(f"  • {endpoint}")
    
    overall_success = (successful_dns > 0 and successful_ports > 0 and 
                      (successful_backend > 0 or successful_endpoints > 0))
    
    if overall_success:
        print("\n🎉 System appears to be functioning correctly!")
        print("✅ Network connectivity established")
        print("✅ Services are accessible")
        return 0
    else:
        print("\n💥 Critical issues detected!")
        print("❌ Network or service connectivity problems")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(comprehensive_diagnostics())
    sys.exit(exit_code)