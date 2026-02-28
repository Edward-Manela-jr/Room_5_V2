import os
import shutil
from pathlib import Path

def undo_sort(source_folder):
    """
    Move all images from subfolders back to the main folder.
    """
    source_path = Path(source_folder)
    
    if not source_path.exists():
        print(f"Error: Source folder '{source_folder}' does not exist.")
        return
    
    print(f"Undoing sort in: {source_path}")
    
    moved_count = 0
    
    # Get all subdirectories
    for item in source_path.iterdir():
        if item.is_dir():
            # Look for images in this subdirectory and its subdirectories
            for image_file in item.rglob('*'):
                if image_file.is_file() and image_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
                    # Move image back to main folder
                    dest_path = source_path / image_file.name
                    
                    # Handle naming conflicts
                    counter = 1
                    original_dest = dest_path
                    while dest_path.exists():
                        stem = original_dest.stem
                        suffix = original_dest.suffix
                        dest_path = source_path / f"{stem}_{counter}{suffix}"
                        counter += 1
                    
                    try:
                        shutil.move(str(image_file), str(dest_path))
                        print(f"Moved back: {image_file.name}")
                        moved_count += 1
                    except Exception as e:
                        print(f"Error moving {image_file.name}: {e}")
    
    # Remove empty directories
    for item in sorted(source_path.iterdir(), key=lambda x: x.stat().st_size, reverse=True):
        if item.is_dir():
            try:
                item.rmdir()
                print(f"Removed empty directory: {item.name}")
            except OSError:
                # Directory not empty, skip
                pass
    
    print(f"\nUndo complete! Moved {moved_count} files back to main folder.")

def main():
    source_folder = input("Enter the path to the folder to undo: ").strip()
    
    # Remove quotes if user added them
    if source_folder.startswith('"') and source_folder.endswith('"'):
        source_folder = source_folder[1:-1]
    elif source_folder.startswith("'") and source_folder.endswith("'"):
        source_folder = source_folder[1:-1]
    
    undo_sort(source_folder)

if __name__ == "__main__":
    main()
