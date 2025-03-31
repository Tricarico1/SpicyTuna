import os
import glob

def cleanup_data_files():
    """Delete all data_*.txt files in the current directory"""
    files = glob.glob("data_*.txt")
    for file in files:
        try:
            os.remove(file)
            print(f"Deleted: {file}")
        except Exception as e:
            print(f"Error deleting {file}: {e}") 