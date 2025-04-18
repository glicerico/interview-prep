# interview-prep
Scripts to help with interview preparation

## Docker Environment Setup

To connect to Redis running in a Docker container:

1. Create a `.env` file based on `.env.example`:
   ```
   cp .env.example .env
   ```

2. Edit the `.env` file to set your Redis connection parameters:
   ```
   REDIS_HOST=redis  # Use the service name from docker-compose
   REDIS_PORT=6379
   REDIS_PASSWORD=your_password_if_needed
   ```

3. If you're running this code in a separate container:
   - Make sure it's on the same Docker network as the Redis container
   - Use the Redis service name as the host (e.g., `redis`)

4. If you're running this code on the host machine:
   - Set `REDIS_HOST` to the IP address where Docker is running (often `localhost` or `127.0.0.1`)
   - Make sure the Redis port is mapped to the host (e.g., `-p 6379:6379` in your Redis container)

## Usage

Follow the instructions in `src/README.md` for using the interview preparation tools.
