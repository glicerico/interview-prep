#!/usr/bin/env python3

import redis
import argparse
import os
from dotenv import load_dotenv

class RedisClient:
    def __init__(self, host=None, port=None, db=0, password=None):
        # Load environment variables if not already loaded
        load_dotenv()
        
        # Use parameters if provided, otherwise fall back to environment variables
        self.host = host or os.getenv('REDIS_HOST', '127.0.0.1')
        self.port = port or int(os.getenv('REDIS_PORT', 6379))
        self.db = db or int(os.getenv('REDIS_DB', 0))
        self.password = password or os.getenv('REDIS_PASSWORD', None)
        
        # Create Redis client with the configured parameters
        self.client = redis.Redis(
            host=self.host, 
            port=self.port, 
            db=self.db,
            password=self.password,
            decode_responses=True  # Automatically decode responses to strings
        )

    def get_variable(self, key):
        """Get the value of a variable, handling different Redis types"""
        key_type = self.client.type(key)
        
        if key_type == 'string':
            value = self.client.get(key)
            print(f"{key} (string): {value}")
            return value

        elif key_type == 'hash':
            value = self.client.hgetall(key)
            print(f"{key} (hash): {value}")
            return value

        elif key_type == 'list':
            value = self.client.lrange(key, 0, -1)
            print(f"{key} (list): {value}")
            return value

        elif key_type == 'set':
            value = self.client.smembers(key)
            print(f"{key} (set): {value}")
            return value

        elif key_type == 'zset':
            value = self.client.zrange(key, 0, -1, withscores=True)
            print(f"{key} (sorted set): {value}")
            return value

        else:
            print(f"{key} has unknown type '{key_type}' or does not exist.")
            return None

    def set_variable(self, key, value):
        """Set the value of a variable"""
        self.client.set(key, value)
        print(f"Set '{key}' to '{value[:30]}...' (truncated)" if len(str(value)) > 30 else f"Set '{key}' to '{value}'.")
        return True

    def list_variables(self):
        """List all keys stored in Redis"""
        keys = self.client.keys('*')
        if keys:
            print("Stored variables:")
            for key in keys:
                print(f"- {key}")
            return keys
        else:
            print("No keys found.")
            return []

    def delete_variable(self, key):
        """Delete a variable from Redis
        
        Args:
            key (str): The key to delete
            
        Returns:
            bool: True if the key was deleted, False otherwise
        """
        try:
            result = self.client.delete(key)
            if result > 0:
                print(f"✅ Deleted '{key}' from Redis")
                return True
            else:
                print(f"⚠️ Key '{key}' not found in Redis")
                return False
        except Exception as e:
            print(f"❌ Error deleting key '{key}': {e}")
            return False


def main():
    load_dotenv()  # Load environment variables
    
    parser = argparse.ArgumentParser(description="Interact with Redis variables.")
    parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'), help="Set a variable to a specified value.")
    parser.add_argument('--get', metavar='KEY', help="Get the value of a specified variable.")
    parser.add_argument('--list', action='store_true', help="List all variables.")
    parser.add_argument('--delete', metavar='KEY', help="Delete a variable from Redis.")
    parser.add_argument('--host', help="Redis host (default: from REDIS_HOST env var or localhost)")
    parser.add_argument('--port', type=int, help="Redis port (default: from REDIS_PORT env var or 6379)")
    parser.add_argument('--db', type=int, help="Redis database (default: from REDIS_DB env var or 0)")
    parser.add_argument('--password', help="Redis password (default: from REDIS_PASSWORD env var)")

    args = parser.parse_args()
    redis_client = RedisClient(
        host=args.host,
        port=args.port,
        db=args.db,
        password=args.password
    )

    if args.set:
        key, value = args.set
        redis_client.set_variable(key, value)
    elif args.get:
        redis_client.get_variable(args.get)
    elif args.list:
        redis_client.list_variables()
    elif args.delete:
        redis_client.delete_variable(args.delete)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

