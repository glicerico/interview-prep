#!/usr/bin/env python3
"""
Manage interview contexts for the Desi robot.

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
from pathlib import Path
from redis_client import RedisClient
from prepare_guest_prompt import prepare_guest_prompt

# Directory to store interview context files
CONTEXTS_DIR = Path("interview_contexts")


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


def load_context_to_redis(context_path):
    """Load the selected context into Redis"""
    try:
        redis_client = RedisClient()
        
        with open(context_path, 'r', encoding='utf-8') as f:
            context_content = f.read()
        
        # Try to store in Redis under the key that the robot expects
        try:
            redis_client.set_variable('interview_context', context_content)
            print(f"\n✅ Loaded interview context into Redis as 'interview_context'")
            
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
    parser = argparse.ArgumentParser(description="Manage interview contexts for the Desi robot")
    parser.add_argument("--list", action="store_true", help="List available contexts")
    parser.add_argument("--load", type=int, help="Load a specific context by number")
    parser.add_argument("--new", action="store_true", help="Create a new context")
    
    args = parser.parse_args()
    
    # If no arguments provided, run in interactive mode
    if len(sys.argv) == 1:
        print("🤖 Desi Interview Context Manager")
        
        while True:
            print("\nWhat would you like to do?")
            print("1. List available interview contexts")
            print("2. Save an existing context into Redis")
            print("3. Create a new context")
            print("4. Exit")
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                list_available_contexts()
            
            elif choice == '2':
                contexts = list_available_contexts()
                if not contexts:
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
                    else:
                        print("Invalid selection.")
                except ValueError:
                    print("Please enter a valid number.")
            
            elif choice == '3':
                create_new_context()
            
            elif choice == '4':
                print("Goodbye! 👋")
                break
            
            else:
                print("Invalid choice. Please enter a number between 1 and 4.")
    
    # Handle command-line arguments
    else:
        if args.list:
            list_available_contexts()
        
        elif args.load is not None:
            contexts = list_available_contexts()
            if contexts and 1 <= args.load <= len(contexts):
                _, guest_name, file_path = contexts[args.load-1]
                print(f"Loading context for {guest_name}...")
                load_context_to_redis(file_path)
            else:
                print("Invalid context number.")
                return 1
        
        elif args.new:
            create_new_context()
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 