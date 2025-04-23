#!/usr/bin/env python3
"""
Simple script to test Redis connection
"""
from redis_client import RedisClient

def main():
    """Test Redis connection and list variables"""
    print("Testing Redis connection...")
    client = RedisClient()
    
    try:
        # Test connection
        ping_response = client.client.ping()
        print(f"✅ Redis connection successful! Ping response: {ping_response}")
        
        # List variables
        print("\nListing Redis variables:")
        client.list_variables()
        
        return 0
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("\nPlease check your Redis configuration in .env file:")
        print(f"- Host: {client.host}")
        print(f"- Port: {client.port}")
        print(f"- DB: {client.db}")
        return 1

if __name__ == "__main__":
    main() 