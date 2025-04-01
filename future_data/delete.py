import os
import glob

def cleanup_json_files():
    """Delete all JSON files in the current directory."""
    # Find all JSON files in the current directory
    json_pattern = os.path.join(os.getcwd(), "*.json")
    
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