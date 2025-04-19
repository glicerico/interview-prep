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
   # For Redis in Docker using host network:
   REDIS_HOST=127.0.0.1
   REDIS_PORT=6379
   REDIS_PASSWORD=your_password_if_needed
   ```

3. If you're running this code in a separate container:
   - Make sure it's on the same Docker network as the Redis container
   - Use the Redis service name as the host (e.g., `hrsdk-redis-1`) or use host networking

4. Test your Redis connection:
   ```bash
   python src/docker_redis_test.py
   ```

## Usage

Follow the instructions in `src/README.md` for using the interview preparation tools.
