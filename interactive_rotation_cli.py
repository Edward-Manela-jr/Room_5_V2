import os
import sys
import subprocess
from PIL import Image, ExifTags
from pathlib import Path

def open_image_viewer(file_path):
    """Open image with system default viewer"""
    try:
        if sys.platform == "win32":
            os.startfile(file_path)
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["open", str(file_path)])
        else:  # Linux
            subprocess.run(["xdg-open", str(file_path)])
        return True
    except:
        return False

def interactive_rotation_fix(source_folder):
    """
    Interactive command-line tool for fixing image rotations.
    Shows each portrait image and lets user choose rotation.
    """
    source_path = Path(source_folder)
    
    if not source_path.exists():
        print(f"Error: Source folder '{source_folder}' does not exist.")
        return
    
    print(f"🔍 Scanning for portrait images in: {source_path}")
    
    # Find all portrait images
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    portrait_files = []
    
    for root, dirs, files in os.walk(source_path):
        for filename in files:
            file_path = Path(root) / filename
            if file_path.suffix.lower() in image_extensions:
                try:
                    with Image.open(file_path) as img:
                        width, height = img.size
                        if height > width:  # Portrait
                            portrait_files.append(file_path)
                except:
                    continue
    
    if not portrait_files:
        print("✅ No portrait images found!")
        return
    
    print(f"📊 Found {len(portrait_files)} portrait images to review")
    print("\n🎯 Instructions:")
    print("  1. Each image will open in your default image viewer")
    print("  2. Look at the image and decide how to rotate it")
    print("  3. Choose rotation option:")
    print("     - 0: Keep as is (no rotation)")
    print("     - 1: Rotate 90° clockwise")
    print("     - 2: Rotate 180°")
    print("     - 3: Rotate 270° clockwise (90° counter-clockwise)")
    print("     - s: Skip this image")
    print("     - q: Quit (remaining images will be skipped)")
    print("\n⚡ Starting review...\n")
    
    fixed_count = 0
    skipped_count = 0
    
    for i, file_path in enumerate(portrait_files):
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                relative_path = file_path.relative_to(source_path)
                
                print(f"📷 Image {i+1}/{len(portrait_files)}: {relative_path} ({width}x{height})")
                
                # Open image in default viewer
                if not open_image_viewer(file_path):
                    print(f"⚠️  Could not open image viewer. Please manually open: {file_path}")
                
                # Get user input
                while True:
                    choice = input("Choose rotation (0/1/2/3/s/q): ").strip().lower()
                    
                    if choice in ['0', '1', '2', '3']:
                        degrees = {'0': 0, '1': 270, '2': 180, '3': 90}[choice]
                        
                        if degrees != 0:
                            rotated_img = img.rotate(-degrees, expand=True)  # Negative for clockwise
                            rotated_img.save(file_path, quality=95)
                            print(f"✅ Rotated by {degrees}°")
                            fixed_count += 1
                        else:
                            print("✅ Kept as is")
                        
                        break
                        
                    elif choice == 's':
                        print("⏭️  Skipped")
                        skipped_count += 1
                        break
                        
                    elif choice == 'q':
                        print("🛑 Quitting - remaining images will be skipped")
                        print(f"\n📊 Final Results:")
                        print(f"✅ Fixed: {fixed_count} images")
                        print(f"⏭️  Skipped: {skipped_count + (len(portrait_files) - i - 1)} images")
                        return
                        
                    else:
                        print("❌ Invalid choice. Please enter 0, 1, 2, 3, s, or q")
                
                print()  # Empty line for readability
                
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {e}")
            continue
    
    print(f"\n🎉 Review complete!")
    print(f"📊 Final Results:")
    print(f"✅ Fixed: {fixed_count} images")
    print(f"⏭️  Skipped: {skipped_count} images")

def main():
    if len(sys.argv) > 1:
        source_folder = sys.argv[1]
        interactive_rotation_fix(source_folder)
    else:
        source_folder = input("Enter the path to the folder with portrait images: ").strip()
        
        # Remove quotes if user added them
        if source_folder.startswith('"') and source_folder.endswith('"'):
            source_folder = source_folder[1:-1]
        elif source_folder.startswith("'") and source_folder.endswith("'"):
            source_folder = source_folder[1:-1]
        
        interactive_rotation_fix(source_folder)

if __name__ == "__main__":
    main()
