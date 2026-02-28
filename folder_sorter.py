import os
import shutil
from pathlib import Path
import re

def sort_images_by_name(source_folder, file_extensions=None):
    """
    Sort files in source_folder into subfolders based on their base names.
    Handles cases like "lusaka 2010.jpg" and "lusaka 2011.jpg" by creating
    a main "lusaka" folder with year subfolders.
    For non-image files, creates extension-based folders (e.g., PDF, DOC, etc.)
    
    Args:
        source_folder (str): Path to folder containing files
        file_extensions (list): List of file extensions to process (None = all files)
    """
    if file_extensions is None:
        # Process all common file types
        file_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp',
                          '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                          '.txt', '.csv', '.zip', '.rar', '.mp4', '.avi', '.mov']
    
    source_path = Path(source_folder)
    
    if not source_path.exists():
        print(f"Error: Source folder '{source_folder}' does not exist.")
        return
    
    if not source_path.is_dir():
        print(f"Error: '{source_folder}' is not a directory.")
        return
    
    print(f"Processing files in: {source_path}")
    
    # Get all files in the source folder
    all_files = []
    for ext in file_extensions:
        all_files.extend(source_path.glob(f"*{ext}"))
        all_files.extend(source_path.glob(f"*{ext.upper()}"))
    
    if not all_files:
        print("No files found in the source folder.")
        return
    
    print(f"Found {len(all_files)} files")
    
    # Group files by their main name and type
    file_groups = {}
    
    for file_path in all_files:
        # Extract base name without extension
        filename = file_path.stem
        file_ext = file_path.suffix.lower()
        
        # Determine if this is an image file
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        is_image = file_ext in image_extensions
        
        if is_image:
            # For images, extract the first word as the main town name
            parts = filename.split()
            if len(parts) >= 2:
                main_name = parts[0]  # First word is the town name
                
                # Look for a 4-digit year in any part
                year = None
                for part in parts[1:]:
                    # Check if this part contains underscores (like 1978_251216_121853_1-12)
                    if '_' in part:
                        # Split by underscores and look for a year
                        sub_parts = part.split('_')
                        for sub_part in sub_parts:
                            if sub_part.isdigit() and len(sub_part) == 4 and 1900 <= int(sub_part) <= 2100:
                                year = sub_part
                                break
                    # Also check if the part itself is a year
                    elif part.isdigit() and len(part) == 4 and 1900 <= int(part) <= 2100:
                        year = part
                    
                    if year:
                        break
                
                # Use year as subfolder if found, otherwise use remaining parts
                if year:
                    subfolder_name = year
                else:
                    # If no year found, use everything after the town name
                    subfolder_name = '_'.join(parts[1:]) if len(parts) > 1 else None
            else:
                # If only one word, use it as main name with no subfolder
                main_name = filename
                subfolder_name = None
            
            # Group by main name
            if main_name not in file_groups:
                file_groups[main_name] = []
            file_groups[main_name].append((file_path, subfolder_name, 'image'))
        else:
            # For non-images, group by extension
            ext_folder = file_ext[1:].upper()  # Remove dot and uppercase (e.g., '.pdf' -> 'PDF')
            if ext_folder not in file_groups:
                file_groups[ext_folder] = []
            
            # Try to extract town name for subfolder organization
            parts = filename.split()
            if len(parts) >= 2:
                town_name = parts[0]
                subfolder_name = '_'.join(parts[1:])
            else:
                town_name = filename
                subfolder_name = None
            
            file_groups[ext_folder].append((file_path, subfolder_name, 'document', town_name))
    
    # Process each group
    moved_count = 0
    
    for group_name, files in file_groups.items():
        for file_info in files:
            if len(file_info) == 3:  # Image files
                file_path, subfolder_name, file_type = file_info
                
                if subfolder_name:
                    # Create main folder and year subfolder
                    main_folder_path = source_path / group_name
                    subfolder_path = main_folder_path / subfolder_name
                    
                    # Create directories if they don't exist
                    main_folder_path.mkdir(exist_ok=True)
                    subfolder_path.mkdir(exist_ok=True)
                    
                    # Destination path for the file
                    dest_path = subfolder_path / file_path.name
                    
                    print(f"Moved: {file_path.name} -> {group_name}/{subfolder_name}/")
                else:
                    # Create main folder only
                    main_folder_path = source_path / group_name
                    main_folder_path.mkdir(exist_ok=True)
                    dest_path = main_folder_path / file_path.name
                    
                    print(f"Moved: {file_path.name} -> {group_name}/")
                    
            else:  # Document files (PDF, etc.)
                file_path, subfolder_name, file_type, town_name = file_info
                
                # Create extension folder
                ext_folder_path = source_path / group_name
                ext_folder_path.mkdir(exist_ok=True)
                
                if subfolder_name and town_name:
                    # Create town subfolder within extension folder
                    town_folder_path = ext_folder_path / town_name
                    town_folder_path.mkdir(exist_ok=True)
                    
                    # Create date subfolder within town folder
                    date_folder_path = town_folder_path / subfolder_name
                    date_folder_path.mkdir(exist_ok=True)
                    dest_path = date_folder_path / file_path.name
                    
                    print(f"Moved: {file_path.name} -> {group_name}/{town_name}/{subfolder_name}/")
                else:
                    # Just put in extension folder
                    dest_path = ext_folder_path / file_path.name
                    print(f"Moved: {file_path.name} -> {group_name}/")
            
            # Move the file
            try:
                shutil.move(str(file_path), str(dest_path))
                moved_count += 1
            except Exception as e:
                print(f"Error moving {file_path.name}: {e}")
    
    print(f"\nSorting complete! Moved {moved_count} files into {len(file_groups)} main folders.")

def main():
    # Get user input for source folder
    source_folder = input("Enter the path to the folder containing images: ").strip()
    
    # Remove quotes if user added them
    if source_folder.startswith('"') and source_folder.endswith('"'):
        source_folder = source_folder[1:-1]
    elif source_folder.startswith("'") and source_folder.endswith("'"):
        source_folder = source_folder[1:-1]
    
    # Sort the images
    sort_images_by_name(source_folder)

if __name__ == "__main__":
    main()