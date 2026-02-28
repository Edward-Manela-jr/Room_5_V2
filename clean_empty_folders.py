import os
from pathlib import Path

def remove_empty_folders(source_folder):
    """
    Remove all empty folders from the source directory.
    """
    source_path = Path(source_folder)
    
    if not source_path.exists():
        print(f"Error: Source folder '{source_folder}' does not exist.")
        return
    
    print(f"Cleaning empty folders in: {source_path}")
    
    removed_count = 0
    
    # Get all directories and sort them by depth (deepest first)
    all_dirs = []
    for root, dirs, files in os.walk(source_path):
        for dir_name in dirs:
            all_dirs.append(Path(root) / dir_name)
    
    # Sort by length of path (deepest first)
    all_dirs.sort(key=lambda x: len(str(x)), reverse=True)
    
    for dir_path in all_dirs:
        try:
            # Try to remove the directory (will only work if empty)
            dir_path.rmdir()
            print(f"Removed empty folder: {dir_path.name}")
            removed_count += 1
        except OSError:
            # Directory not empty, skip
            pass
    
    print(f"\nCleanup complete! Removed {removed_count} empty folders.")

def main():
    source_folder = input("Enter the path to clean: ").strip()
    
    # Remove quotes if user added them
    if source_folder.startswith('"') and source_folder.endswith('"'):
        source_folder = source_folder[1:-1]
    elif source_folder.startswith("'") and source_folder.endswith("'"):
        source_folder = source_folder[1:-1]
    
    remove_empty_folders(source_folder)

if __name__ == "__main__":
    main()
