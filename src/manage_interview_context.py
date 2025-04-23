#!/usr/bin/env python3
"""
Manage interview contexts for hrsdk characters.

This script allows users to:
1. List available interview contexts stored as text files
2. Select a context to load into Redis for an upcoming interview
3. Create a new context if needed

The selected context is loaded into Redis under the key 'interview_context'
that the robot's template system expects.
"""

import os
import sys
import argparse
import platform
from pathlib import Path
from redis_client import RedisClient
from prepare_guest_prompt import prepare_guest_prompt

# Directory to store interview context files
CONTEXTS_DIR = Path("interview_contexts")

# ASCII art header
HEADER_ART = r"""
 _   _ ____  ____  ____  _  __   _____ _   _ _____ _____ ______     _____ _____ _ _ _ 
| | | |  _ \/ ___||  _ \| |/ /  |_   _| \ | |_   _| ____|  _ \ \   / /_ _| ____| | | |
| |_| | |_) \___ \| | | | ' /     | | |  \| | | | |  _| | |_) \ \ / / | ||  _| | | | |
|  _  |  _ < ___) | |_| | . \    _| |_| |\  | | | | |___|  _ < \ V /  | || |___|_|_|_|
|_| |_|_| \_\____/|____/|_|\_\  |_____|_| \_| |_| |_____|_| \_\ \_/  |___|_____(_|_|_)
                                                                                       
"""

def clear_screen():
    """Clear the terminal screen"""
    os.system("clear")

def print_header():
    """Print the ASCII art header and a separator line"""
    print(HEADER_ART)
    print("INTERVIEW CONTEXT MANAGER")
    print("=" * 80)
    print()

def ensure_contexts_dir():
    """Ensure the contexts directory exists"""
    CONTEXTS_DIR.mkdir(exist_ok=True)
    return CONTEXTS_DIR


def list_available_contexts():
    """List all available interview contexts"""
    contexts_dir = ensure_contexts_dir()
    context_files = list(contexts_dir.glob("*.txt"))
    
    if not context_files:
        print("No interview contexts found.")
        return []
    
    print("\nAvailable interview contexts:")
    contexts = []
    
    for i, file_path in enumerate(sorted(context_files), 1):
        # Extract guest name from filename (remove .txt extension)
        guest_name = file_path.stem.replace('_', ' ').title()
        contexts.append((i, guest_name, file_path))
        print(f"{i}. {guest_name}")
    
    return contexts


def get_or_create_session_id(redis_client):
    """
    Get the current session ID from Redis or create a new one if it doesn't exist.
    
    Args:
        redis_client: An instance of RedisClient
        
    Returns:
        str: The session ID
    """
    # Try to get existing session ID
    session_id = redis_client.client.get('default.current_session')
    
    if not session_id:
        # If no session ID exists, create a new one
        import uuid
        session_id = uuid.uuid4().hex
        redis_client.set_variable('default.current_session', session_id)
        print(f"Created new session ID: {session_id}")
    else:
        # Handle both string and bytes types
        if isinstance(session_id, bytes):
            session_id = session_id.decode('utf-8')
        print(f"Using existing session ID: {session_id}")
    
    return session_id


def get_redis_key(base_key, redis_client=None):
    """
    Format a Redis key with the current session ID prefix.
    
    Args:
        base_key (str): The base key name
        redis_client (RedisClient, optional): Redis client instance. If None, a new one is created.
        
    Returns:
        str: The formatted key with session ID prefix
    """
    if redis_client is None:
        redis_client = RedisClient()
    
    session_id = get_or_create_session_id(redis_client)
    return f"default.{session_id}.{base_key}"


def load_context_to_redis(context_path):
    """Load the selected context into Redis with session ID prefix"""
    try:
        # Create Redis client with configurable connection parameters
        redis_client = RedisClient()
        
        with open(context_path, 'r', encoding='utf-8') as f:
            context_content = f.read()
        
        # Try to store in Redis under the key that the robot expects
        try:
            # Get the formatted Redis key with session ID
            redis_key = get_redis_key('interview_context', redis_client)
            
            # Store the context with the session-prefixed key
            redis_client.set_variable(redis_key, context_content)
            print(f"\n✅ Loaded interview context into Redis as '{redis_key}'")
            
            # Print connection info for debugging
            print(f"\nConnected to Redis at {redis_client.host}:{redis_client.port} (DB: {redis_client.db})")
            
            # Print a preview
            preview = context_content[:200] + "..." if len(context_content) > 200 else context_content
            print(f"\nPreview:\n{preview}")
            
        except Exception as e:
            print(f"\n⚠️ Could not connect to Redis: {e}")
            print("The interview context was not loaded into Redis.")
            print("Please make sure hrsdk's Redis container is running and try again.")
            print("\nThe context file is still available at:")
            print(f"  {context_path}")
            
    except FileNotFoundError:
        print(f"\n❌ Error: Context file not found: {context_path}")
    except Exception as e:
        print(f"\n❌ Error loading context: {e}")


def create_new_context():
    """Create a new interview context"""
    print("\n📝 Creating a new interview context")
    
    guest_name = input("Enter guest name: ").strip()
    if not guest_name:
        print("Guest name cannot be empty.")
        return False
    
    focus_areas = input("Enter focus areas (comma-separated): ").strip()
    if not focus_areas:
        print("Focus areas cannot be empty.")
        return False
    
    # Create a filename-safe version of the guest name
    safe_name = guest_name.lower().replace(' ', '_')
    contexts_dir = ensure_contexts_dir()
    output_file = contexts_dir / f"{safe_name}.txt"
    
    # Prepare the guest prompt and save it to the file
    print(f"\nPreparing interview context for {guest_name}...")
    prepare_guest_prompt(
        guest_name=guest_name,
        focus_areas=focus_areas,
        output_file=str(output_file)
    )
    
    print(f"\n✅ Created new interview context: {output_file}")
    
    # Ask if the user wants to load this context into Redis
    load_now = input("\nLoad this context into Redis for the upcoming interview? (y/n): ").lower()
    if load_now.startswith('y'):
        load_context_to_redis(output_file)
    
    return True


def main():
    """Main function to manage interview contexts"""
    parser = argparse.ArgumentParser(description="Manage interview contexts for robots")
    parser.add_argument("--list", action="store_true", help="List available contexts")
    parser.add_argument("--load", type=int, help="Load a specific context by number")
    parser.add_argument("--new", action="store_true", help="Create a new context")
    
    args = parser.parse_args()
    
    # If no arguments provided, run in interactive mode
    if len(sys.argv) == 1:
        
        while True:
            clear_screen()
            print_header()

            print("\nWhat would you like to do?")
            print("1. List available interview contexts")
            print("2. Save an existing context into Redis")
            print("3. Create a new context")
            print("4. Exit")
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            # Clear screen and reprint header for better UI experience
            clear_screen()
            print_header()
            
            if choice == '1':
                print("📋 LISTING AVAILABLE CONTEXTS")
                print("-" * 40)
                list_available_contexts()
                input("\nPress Enter to return to the main menu...")
            
            elif choice == '2':
                print("💾 LOADING CONTEXT INTO REDIS")
                print("-" * 40)
                contexts = list_available_contexts()
                if not contexts:
                    input("\nPress Enter to return to the main menu...")
                    continue
                
                selection = input("\nEnter the number of the context to load (or 0 to cancel): ").strip()
                try:
                    selection = int(selection)
                    if selection == 0:
                        continue
                    
                    if 1 <= selection <= len(contexts):
                        _, guest_name, file_path = contexts[selection-1]
                        print(f"\nLoading context for {guest_name}...")
                        load_context_to_redis(file_path)
                        input("\nPress Enter to return to the main menu...")
                    else:
                        print("Invalid selection.")
                        input("\nPress Enter to return to the main menu...")
                except ValueError:
                    print("Please enter a valid number.")
                    input("\nPress Enter to return to the main menu...")
            
            elif choice == '3':
                print("📝 CREATING NEW CONTEXT")
                print("-" * 40)
                create_new_context()
                input("\nPress Enter to return to the main menu...")
            
            elif choice == '4':
                clear_screen()
                print_header()
                print("Goodbye! 👋")
                break
            
            else:
                print(f"❌ Invalid choice: '{choice}'")
                print("Please enter a number between 1 and 4.")
                input("\nPress Enter to return to the main menu...")
    
    # Handle command-line arguments
    else:
        if args.list:
            clear_screen()
            print_header()
            list_available_contexts()
        
        elif args.load is not None:
            clear_screen()
            print_header()
            contexts = list_available_contexts()
            if contexts and 1 <= args.load <= len(contexts):
                _, guest_name, file_path = contexts[args.load-1]
                print(f"Loading context for {guest_name}...")
                load_context_to_redis(file_path)
            else:
                print("Invalid context number.")
                return 1
        
        elif args.new:
            clear_screen()
            print_header()
            create_new_context()
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
