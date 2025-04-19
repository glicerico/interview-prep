#!/usr/bin/env python3
"""
Script to find the IP address of a Redis container in a Docker network
"""
import subprocess
import json
import argparse
import os
from dotenv import load_dotenv

def find_container_ip(container_name, network_name=None):
    """Find the IP address of a Docker container"""
    try:
        # Get container details
        result = subprocess.run(
            ["docker", "inspect", container_name],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            print(f"❌ Container '{container_name}' not found")
            return None
        
        # Parse the JSON output
        container_info = json.loads(result.stdout)
        
        # If network name is provided, look for that specific network
        if network_name:
            networks = container_info[0]["NetworkSettings"]["Networks"]
            if network_name in networks:
                ip_address = networks[network_name]["IPAddress"]
                print(f"✅ Found {container_name} on network '{network_name}' with IP: {ip_address}")
                return ip_address
            else:
                print(f"❌ Container is not connected to network '{network_name}'")
                print(f"Available networks: {', '.join(networks.keys())}")
                return None
        
        # Otherwise, get the first IP address we find
        networks = container_info[0]["NetworkSettings"]["Networks"]
        for network, details in networks.items():
            ip_address = details["IPAddress"]
            if ip_address:
                print(f"✅ Found {container_name} on network '{network}' with IP: {ip_address}")
                return ip_address
        
        print(f"❌ No IP address found for {container_name}")
        return None
    
    except Exception as e:
        print(f"❌ Error inspecting container: {e}")
        return None

def update_env_file(ip_address):
    """Update the .env file with the Redis IP address"""
    try:
        # Load current .env file
        load_dotenv()
        env_vars = {}
        
        # Read existing variables
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key] = value
        
        # Update Redis host
        env_vars["REDIS_HOST"] = ip_address
        
        # Write back to .env file
        with open(".env", "w") as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        print(f"✅ Updated .env file with REDIS_HOST={ip_address}")
        return True
    
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Find the IP address of a Redis container")
    parser.add_argument("--container", default="hrsdk-redis-1", help="Redis container name")
    parser.add_argument("--network", default="hrsdk_default", help="Docker network name")
    parser.add_argument("--update-env", action="store_true", help="Update .env file with the IP address")
    
    args = parser.parse_args()
    
    print(f"🔍 Looking for container '{args.container}' on network '{args.network}'...")
    
    ip_address = find_container_ip(args.container, args.network)
    
    if ip_address and args.update_env:
        update_env_file(ip_address)
        print("\n📝 Next steps:")
        print("1. Try connecting to Redis using the IP address:")
        print(f"   python src/redis_client.py --host {ip_address} --list")
        print("2. Or run your interview context manager:")
        print("   python src/manage_interview_context.py")
    
    return 0

if __name__ == "__main__":
    main() 