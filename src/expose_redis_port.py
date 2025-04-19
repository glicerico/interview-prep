#!/usr/bin/env python3
"""
Script to expose Redis port from Docker container to host
"""
import subprocess
import argparse
import os
import time
from dotenv import load_dotenv

def check_socat_installed():
    """Check if socat is installed"""
    try:
        result = subprocess.run(
            ["which", "socat"],
            capture_output=True, text=True
        )
        return result.returncode == 0
    except Exception:
        return False

def get_container_ip(container_name, network_name=None):
    """Get the IP address of a Docker container"""
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
        import json
        container_info = json.loads(result.stdout)
        
        # If network name is provided, look for that specific network
        if network_name:
            networks = container_info[0]["NetworkSettings"]["Networks"]
            if network_name in networks:
                return networks[network_name]["IPAddress"]
            else:
                print(f"❌ Container is not connected to network '{network_name}'")
                print(f"Available networks: {', '.join(networks.keys())}")
                return None
        
        # Otherwise, get the first IP address we find
        networks = container_info[0]["NetworkSettings"]["Networks"]
        for network, details in networks.items():
            ip_address = details["IPAddress"]
            if ip_address:
                return ip_address
        
        print(f"❌ No IP address found for {container_name}")
        return None
    
    except Exception as e:
        print(f"❌ Error inspecting container: {e}")
        return None

def create_port_forward(container_ip, container_port, host_port):
    """Create a port forward using socat"""
    if not check_socat_installed():
        print("❌ socat is not installed. Please install it first:")
        print("  - Ubuntu/Debian: sudo apt-get install socat")
        print("  - macOS: brew install socat")
        print("  - Windows: Install WSL and then install socat in WSL")
        return None
    
    try:
        # Start socat in the background
        cmd = ["socat", f"TCP-LISTEN:{host_port},fork,reuseaddr", f"TCP:{container_ip}:{container_port}"]
        print(f"Starting port forward: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment to see if it starts successfully
        time.sleep(1)
        if process.poll() is not None:
            # Process exited already
            stdout, stderr = process.communicate()
            print(f"❌ Port forward failed: {stderr.decode()}")
            return None
        
        print(f"✅ Port forward created: localhost:{host_port} -> {container_ip}:{container_port}")
        print("Press Ctrl+C to stop the port forward")
        
        # Update .env file
        update_env_file("localhost", host_port)
        
        return process
    
    except Exception as e:
        print(f"❌ Error creating port forward: {e}")
        return None

def update_env_file(host, port):
    """Update the .env file with the Redis host and port"""
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
        
        # Update Redis host and port
        env_vars["REDIS_HOST"] = host
        env_vars["REDIS_PORT"] = str(port)
        
        # Write back to .env file
        with open(".env", "w") as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        print(f"✅ Updated .env file with REDIS_HOST={host} and REDIS_PORT={port}")
        return True
    
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Expose Redis port from Docker container to host")
    parser.add_argument("--container", default="hrsdk-redis-1", help="Redis container name")
    parser.add_argument("--network", default="hrsdk_default", help="Docker network name")
    parser.add_argument("--container-port", type=int, default=6379, help="Redis port in container")
    parser.add_argument("--host-port", type=int, default=6379, help="Port to expose on host")
    
    args = parser.parse_args()
    
    print(f"🔍 Looking for container '{args.container}' on network '{args.network}'...")
    
    # Get container IP
    container_ip = get_container_ip(args.container, args.network)
    if not container_ip:
        return 1
    
    print(f"✅ Found container IP: {container_ip}")
    
    # Create port forward
    process = create_port_forward(container_ip, args.container_port, args.host_port)
    if not process:
        return 1
    
    # Keep running until user interrupts
    try:
        process.wait()
    except KeyboardInterrupt:
        process.terminate()
        print("\n✅ Port forward stopped")
    
    return 0

if __name__ == "__main__":
    main() 