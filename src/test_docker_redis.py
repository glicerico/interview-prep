#!/usr/bin/env python3
"""
Utility script to test Redis connection in Docker environment
"""
import os
import sys
import socket
import argparse
import subprocess
from dotenv import load_dotenv

def check_host_resolution(hostname):
    """Check if a hostname can be resolved"""
    try:
        ip_address = socket.gethostbyname(hostname)
        print(f"✅ Hostname '{hostname}' resolves to {ip_address}")
        return ip_address
    except socket.gaierror:
        print(f"❌ Cannot resolve hostname '{hostname}'")
        return None

def check_port_connectivity(host, port):
    """Check if a port is open on a host"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((host, port))
    if result == 0:
        print(f"✅ Port {port} is open on {host}")
        return True
    else:
        print(f"❌ Port {port} is not accessible on {host}")
        return False
    
def list_docker_containers():
    """List running Docker containers"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}\t{{.Ports}}"], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            print("\nRunning Docker containers:")
            print(result.stdout)
            return True
        return False
    except Exception:
        print("❌ Could not list Docker containers. Is Docker running?")
        return False

def list_docker_networks():
    """List Docker networks"""
    try:
        result = subprocess.run(
            ["docker", "network", "ls"], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            print("\nDocker networks:")
            print(result.stdout)
            return True
        return False
    except Exception:
        print("❌ Could not list Docker networks. Is Docker running?")
        return False

def test_redis_connection():
    """Test Redis connection using redis_client.py"""
    try:
        from redis_client import RedisClient
        client = RedisClient()
        print(f"\nTesting Redis connection to {client.host}:{client.port} (DB: {client.db})")
        
        try:
            client.client.ping()
            print("✅ Successfully connected to Redis!")
            return True
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            return False
    except ImportError:
        print("❌ Could not import RedisClient. Make sure you're running from the project root.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test Redis connectivity in Docker environment")
    parser.add_argument("--host", help="Redis host to test (default: from .env or 'redis')")
    parser.add_argument("--port", type=int, default=6379, help="Redis port to test (default: 6379)")
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Get Redis host from args, env, or default
    redis_host = args.host or os.getenv("REDIS_HOST", "redis")
    redis_port = args.port or int(os.getenv("REDIS_PORT", 6379))
    
    print(f"🔍 Testing Redis connectivity to {redis_host}:{redis_port}")
    
    # Check Docker environment
    list_docker_containers()
    list_docker_networks()
    
    # Check hostname resolution
    ip = check_host_resolution(redis_host)
    if ip:
        # Check port connectivity
        check_port_connectivity(ip, redis_port)
    else:
        print("\n🔧 Suggestions:")
        print("1. If using container name, make sure you're on the same Docker network")
        print("2. Try using 'localhost' or the Docker host IP if running from host machine")
        print("3. Check if the Redis container is running with 'docker ps | grep redis'")
    
    # Test actual Redis connection
    test_redis_connection()
    
    print("\n📋 Summary:")
    print(f"- Redis host: {redis_host}")
    print(f"- Redis port: {redis_port}")
    print("- Check the output above for connection status and suggestions")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 