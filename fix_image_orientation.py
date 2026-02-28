import os
import shutil
import sys
from PIL import Image, ExifTags
from pathlib import Path

def fix_image_orientation(source_folder):
    """
    Fix image orientation based on EXIF data in all subfolders.
    This will rotate images to their correct orientation.
    """
    source_path = Path(source_folder)
    
    if not source_path.exists():
        print(f"Error: Source folder '{source_folder}' does not exist.")
        return
    
    print(f"Fixing image orientations in: {source_path}")
    
    # Supported image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    
    fixed_count = 0
    skipped_count = 0
    error_count = 0
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(source_path):
        for filename in files:
            file_path = Path(root) / filename
            
            # Check if it's an image file
            if file_path.suffix.lower() in image_extensions:
                try:
                    # Open image and check EXIF data
                    with Image.open(file_path) as img:
                        # Get EXIF data
                        exif_data = img._getexif()
                        
                        if exif_data is not None:
                            # Look for orientation tag
                            orientation_tag = None
                            for tag, value in ExifTags.TAGS.items():
                                if value == 'Orientation':
                                    orientation_tag = tag
                                    break
                            
                            if orientation_tag and orientation_tag in exif_data:
                                orientation = exif_data[orientation_tag]
                                
                                # Define rotation based on orientation
                                rotation_angles = {
                                    1: 0,    # Normal
                                    2: 0,    # Flipped horizontally
                                    3: 180,  # Rotated 180 degrees
                                    4: 0,    # Flipped vertically
                                    5: 0,    # Flipped horizontally then rotated 90 CCW
                                    6: 270,  # Rotated 90 degrees CW
                                    7: 0,    # Flipped horizontally then rotated 90 CW
                                    8: 90    # Rotated 90 degrees CCW
                                }
                                
                                if orientation in rotation_angles and rotation_angles[orientation] != 0:
                                    # Rotate the image
                                    rotated_img = img.rotate(rotation_angles[orientation], expand=True)
                                    
                                    # Save the rotated image (overwrite original)
                                    rotated_img.save(file_path, quality=95)
                                    print(f"Fixed orientation: {file_path.relative_to(source_path)} (was {orientation}, rotated {rotation_angles[orientation]}°)")
                                    fixed_count += 1
                                else:
                                    skipped_count += 1
                            else:
                                skipped_count += 1
                        else:
                            skipped_count += 1
                            
                except Exception as e:
                    print(f"Error processing {file_path.name}: {e}")
                    error_count += 1
    
    print(f"\nOrientation fixing complete!")
    print(f"✅ Fixed: {fixed_count} images")
    print(f"⏭️  Skipped: {skipped_count} images (no rotation needed or no EXIF data)")
    print(f"❌ Errors: {error_count} images")

def main():
    # Check if path provided as command line argument
    if len(sys.argv) > 1:
        source_folder = sys.argv[1]
        print(f"Using command line path: {source_folder}")
        fix_image_orientation(source_folder)
    else:
        source_folder = input("Enter the path to the folder to fix orientations: ").strip()
        
        # Remove quotes if user added them
        if source_folder.startswith('"') and source_folder.endswith('"'):
            source_folder = source_folder[1:-1]
        elif source_folder.startswith("'") and source_folder.endswith("'"):
            source_folder = source_folder[1:-1]
        
        # Ask for confirmation before proceeding
        print(f"\n⚠️  This will modify image files in place!")
        print(f"📁 Target folder: {source_folder}")
        confirm = input("Do you want to continue? (y/N): ").strip().lower()
        
        if confirm in ['y', 'yes']:
            fix_image_orientation(source_folder)
        else:
            print("Operation cancelled.")

if __name__ == "__main__":
    main()
