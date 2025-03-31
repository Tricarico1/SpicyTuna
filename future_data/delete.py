import os
import glob

def cleanup_json_files():
    """Delete all JSON files in the future_data directory."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create pattern for JSON files in the future_data directory
    json_pattern = os.path.join(script_dir, "*.json")
    
    # Find all JSON files
    json_files = glob.glob(json_pattern)
    
    # Delete each file
    for file_path in json_files:
        try:
            os.remove(file_path)
            print(f"Deleted: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"Error deleting {os.path.basename(file_path)}: {e}")
    
    print("Cleanup complete.")

if __name__ == "__main__":
    cleanup_json_files() 