#!/usr/bin/env python3
"""
Build script for Linux Image Organizer App
Creates a standalone executable and optional desktop integration
Run on Linux or WSL
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_requirements():
    """Install required packages for building"""
    requirements = [
        'pyinstaller',
        'pillow',
    ]
    
    print("📦 Installing build requirements...")
    for req in requirements:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', req], 
                         check=True, capture_output=True)
            print(f"✅ Installed {req}")
        except subprocess.CalledProcessError:
            print(f"⚠️  Could not install {req} (may already be installed)")

def create_spec_file():
    """Create PyInstaller spec file for Linux"""
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['image_organizer_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('folder_sorter.py', '.'),
        ('undo_sort.py', '.'),
        ('clean_empty_folders.py', '.'),
        ('fix_image_orientation.py', '.'),
        ('fix_all_rotations.py', '.'),
        ('interactive_rotation_cli.py', '.'),
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ExifTags',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ImageOrganizerPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)
"""
    
    with open('image_organizer_linux.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content.strip())
    
    print("✅ Created PyInstaller spec file for Linux")

def create_desktop_entry():
    """Create .desktop file for Linux integration"""
    desktop_content = """
[Desktop Entry]
Version=1.0
Type=Application
Name=Image Organizer Pro
Comment=Professional image organization and correction tool
Exec=ImageOrganizerPro
Icon=image-organizer
Categories=Graphics;Utility;
Terminal=false
"""
    
    with open('image-organizer.desktop', 'w', encoding='utf-8') as f:
        f.write(desktop_content.strip())
    
    print("✅ Created desktop entry file")

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable with PyInstaller...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            'image_organizer_linux.spec'
        ], check=True, capture_output=True, text=True)
        
        print("✅ Executable built successfully!")
        print(f"📁 Output: dist/ImageOrganizerPro")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    
    return True

def make_executable():
    """Make the executable actually executable"""
    exe_path = 'dist/ImageOrganizerPro'
    if os.path.exists(exe_path):
        os.chmod(exe_path, 0o755)
        print("✅ Made executable file runnable")
    else:
        print(f"⚠️  Could not find {exe_path}")

def create_appimage_hint():
    """Create instructions for building AppImage"""
    hint_content = """
# How to Create a Linux AppImage

1. Install appimagetool:
   https://github.com/AppImage/AppImageKit/releases

2. Create AppDir structure:
   mkdir -p AppDir/usr/bin
   mkdir -p AppDir/usr/share/applications
   mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps

3. Copy files:
   cp dist/ImageOrganizerPro AppDir/usr/bin/
   cp image-organizer.desktop AppDir/usr/share/applications/
   # Add a 256x256 PNG icon if available

4. Create AppImage:
   ./appimagetool AppDir ImageOrganizerPro-x86_64.AppImage

5. Make it executable:
   chmod +x ImageOrganizerPro-x86_64.AppImage

6. Run it:
   ./ImageOrganizerPro-x86_64.AppImage
"""
    
    with open('CREATE_APPIMAGE.txt', 'w', encoding='utf-8') as f:
        f.write(hint_content.strip())
    
    print("✅ Created AppImage creation instructions")

def main():
    """Main build process"""
    print("🚀 Building Image Organizer Pro for Linux...")
    
    # Check if we're on Linux
    if sys.platform not in ["linux", "linux2"]:
        print("⚠️  Warning: This build script is designed for Linux")
        print("   It may work on macOS, but testing should be done on Linux")
        print("   For Windows, use build_windows_app.py")
    
    # Install requirements
    install_requirements()
    
    # Create necessary files
    create_spec_file()
    create_desktop_entry()
    
    # Build executable
    if build_executable():
        make_executable()
        create_appimage_hint()
        
        print("\n🎉 Build completed successfully!")
        print("\n📦 Distribution files created:")
        print("   📁 dist/ImageOrganizerPro - Main executable")
        print("   📄 image-organizer.desktop - Desktop entry")
        
        print("\n📋 Next steps:")
        print("   1. Test the executable: ./dist/ImageOrganizerPro")
        print("   2. (Optional) Create AppImage:")
        print("      - See CREATE_APPIMAGE.txt for instructions")
        print("   3. (Optional) Install system-wide:")
        print("      sudo cp dist/ImageOrganizerPro /usr/local/bin/")
        print("      sudo cp image-organizer.desktop /usr/share/applications/")
        
    else:
        print("\n❌ Build failed. Check the error messages above.")

if __name__ == "__main__":
    main()
