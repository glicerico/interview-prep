import redis
import argparse

class RedisClient:
    def __init__(self, host='localhost', port=6379, db=0):
        self.client = redis.Redis(host=host, port=port, db=db)

    def get_variable(self, key):
        """Get the value of a variable, handling different Redis types"""
        key_type = self.client.type(key).decode('utf-8')

        if key_type == 'string':
            value = self.client.get(key).decode('utf-8')
            print(f"{key} (string): {value}")

        elif key_type == 'hash':
            value = self.client.hgetall(key)
            decoded_value = {k.decode('utf-8'): v.decode('utf-8') for k, v in value.items()}
            print(f"{key} (hash): {decoded_value}")

        elif key_type == 'list':
            value = self.client.lrange(key, 0, -1)
            decoded_value = [item.decode('utf-8') for item in value]
            print(f"{key} (list): {decoded_value}")

        elif key_type == 'set':
            value = self.client.smembers(key)
            decoded_value = {item.decode('utf-8') for item in value}
            print(f"{key} (set): {decoded_value}")

        elif key_type == 'zset':
            value = self.client.zrange(key, 0, -1, withscores=True)
            decoded_value = [(item.decode('utf-8'), score) for item, score in value]
            print(f"{key} (sorted set): {decoded_value}")

        else:
            print(f"{key} has unknown type '{key_type}' or does not exist.")

    def set_variable(self, key, value):
        """Set the value of a variable"""
        self.client.set(key, value)
        print(f"Set '{key}' to '{value}'.")

    def list_variables(self):
        """List all keys stored in Redis"""
        keys = self.client.keys('*')
        if keys:
            print("Stored variables:")
            for key in keys:
                print(f"- {key.decode('utf-8')}")
        else:
            print("No keys found.")


def main():
    parser = argparse.ArgumentParser(description="Interact with Redis variables.")
    parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'), help="Set a variable to a specified value.")
    parser.add_argument('--get', metavar='KEY', help="Get the value of a specified variable.")
    parser.add_argument('--list', action='store_true', help="List all variables.")

    args = parser.parse_args()
    redis_client = RedisClient()

    if args.set:
        key, value = args.set
        redis_client.set_variable(key, value)
    elif args.get:
        redis_client.get_variable(args.get)
    elif args.list:
        redis_client.list_variables()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

