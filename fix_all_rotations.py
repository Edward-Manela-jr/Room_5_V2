import os
import sys
from PIL import Image, ExifTags
from pathlib import Path

def detect_and_fix_rotation(source_folder, auto_fix=False):
    """
    Detect and fix image rotations including those without EXIF data.
    This script will analyze image dimensions and suggest rotations.
    """
    source_path = Path(source_folder)
    
    if not source_path.exists():
        print(f"Error: Source folder '{source_folder}' does not exist.")
        return
    
    print(f"Analyzing image rotations in: {source_path}")
    
    # Supported image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    
    portrait_images = []
    landscape_images = []
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
                    with Image.open(file_path) as img:
                        width, height = img.size
                        
                        # Check if image is in portrait (taller than wide)
                        if height > width:
                            portrait_images.append((file_path, width, height))
                            
                            # Try to fix EXIF first
                            exif_data = img._getexif()
                            needs_rotation = True
                            
                            if exif_data is not None:
                                # Check EXIF orientation
                                orientation_tag = None
                                for tag, value in ExifTags.TAGS.items():
                                    if value == 'Orientation':
                                        orientation_tag = tag
                                        break
                                
                                if orientation_tag and orientation_tag in exif_data:
                                    orientation = exif_data[orientation_tag]
                                    if orientation == 1:  # Already correct
                                        needs_rotation = False
                            
                            if needs_rotation and auto_fix:
                                # Rotate 90 degrees clockwise to make it landscape
                                rotated_img = img.rotate(-90, expand=True)
                                rotated_img.save(file_path, quality=95)
                                print(f"Fixed rotation: {file_path.relative_to(source_path)} ({width}x{height} -> {height}x{width})")
                                fixed_count += 1
                            elif needs_rotation:
                                print(f"Portrait image found: {file_path.relative_to(source_path)} ({width}x{height})")
                        else:
                            landscape_images.append((file_path, width, height))
                            skipped_count += 1
                            
                except Exception as e:
                    print(f"Error processing {file_path.name}: {e}")
                    error_count += 1
    
    print(f"\nAnalysis complete!")
    print(f"📊 Portrait images: {len(portrait_images)}")
    print(f"📊 Landscape images: {len(landscape_images)}")
    print(f"✅ Fixed: {fixed_count} images")
    print(f"⏭️  Skipped: {skipped_count} images")
    print(f"❌ Errors: {error_count} images")
    
    if portrait_images and not auto_fix:
        print(f"\n📋 Portrait images that may need rotation:")
        for file_path, width, height in portrait_images[:10]:  # Show first 10
            print(f"  📷 {file_path.relative_to(source_path)} ({width}x{height})")
        
        if len(portrait_images) > 10:
            print(f"  ... and {len(portrait_images) - 10} more")
    
    return portrait_images

def main():
    # Check if path provided as command line argument
    if len(sys.argv) > 1:
        source_folder = sys.argv[1]
        auto_fix = len(sys.argv) > 2 and sys.argv[2] == '--fix'
        
        print(f"Using command line path: {source_folder}")
        if auto_fix:
            print("🔧 Auto-fix mode enabled")
        else:
            print("🔍 Analysis mode only")
        
        portrait_images = detect_and_fix_rotation(source_folder, auto_fix)
        
        if portrait_images and not auto_fix:
            print(f"\n💡 To fix these portrait images, run:")
            print(f"   python3 fix_all_rotations.py \"{source_folder}\" --fix")
    else:
        source_folder = input("Enter the path to the folder to analyze: ").strip()
        
        # Remove quotes if user added them
        if source_folder.startswith('"') and source_folder.endswith('"'):
            source_folder = source_folder[1:-1]
        elif source_folder.startswith("'") and source_folder.endswith("'"):
            source_folder = source_folder[1:-1]
        
        # Ask for mode
        mode = input("Choose mode:\n1. Analyze only\n2. Analyze and fix\nEnter choice (1/2): ").strip()
        
        auto_fix = mode == '2'
        
        if auto_fix:
            print(f"\n⚠️  This will rotate portrait images to landscape!")
            print(f"📁 Target folder: {source_folder}")
            confirm = input("Do you want to continue? (y/N): ").strip().lower()
            
            if confirm not in ['y', 'yes']:
                print("Operation cancelled.")
                return
        
        detect_and_fix_rotation(source_folder, auto_fix)

if __name__ == "__main__":
    main()
