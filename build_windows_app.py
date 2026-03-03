#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build script for Windows Image Organizer App
Creates a standalone executable and installer
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Fix Windows console encoding for emoji output
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def install_requirements():
    """Install required packages for building"""
    requirements = [
        'pyinstaller',
        'pillow',
        'tkinter'  # Usually comes with Python
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
    """Create PyInstaller spec file"""
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
        ('month_selector.py', '.'),
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
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
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
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)
"""
    
    with open('image_organizer.spec', 'w') as f:
        f.write(spec_content.strip())
    
    print("✅ Created PyInstaller spec file")

def create_version_info():
    """Create version info file for Windows"""
    version_info = """
# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx

VSVersionInfo(
  ffi=FixedFileInfo(
# filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
# Set not needed items to zero 0.
filevers=(1,0,0,0),
prodvers=(1,0,0,0),
# Contains a bitmask that specifies the valid bits 'flags'r
mask=0x3f,
# Contains a bitmask that specifies the Boolean attributes of the file.
flags=0x0,
# The operating system for which this file was designed.
# 0x4 - NT and there is no need to change it.
OS=0x4,
# The general type of file.
# 0x1 - the file is an application.
fileType=0x1,
# The function of the file.
# 0x0 - the function is not defined for this fileType
subtype=0x0,
# Creation date and time stamp.
date=(0, 0)
  ),
  kids=[
StringFileInfo(
  [
  StringTable(
    u'040904B0',
    [StringStruct(u'CompanyName', u'Edward Manela Jr'),
    StringStruct(u'FileDescription', u'Image Organizer Pro - Professional Image Organization Tool'),
    StringStruct(u'FileVersion', u'1.0.0'),
    StringStruct(u'InternalName', u'ImageOrganizerPro'),
    StringStruct(u'LegalCopyright', u'Copyright (c) 2026 Edward Manela Jr'),
    StringStruct(u'OriginalFilename', u'ImageOrganizerPro.exe'),
    StringStruct(u'ProductName', u'Image Organizer Pro'),
    StringStruct(u'ProductVersion', u'1.0.0')])
  ]), 
VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    
    with open('version_info.txt', 'w') as f:
        f.write(version_info.strip())
    
    print("✅ Created version info file")

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable with PyInstaller...")
    
    try:
        # Run PyInstaller - use the spec file only, no additional flags
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller', 
            '--clean', 
            'image_organizer.spec'
        ], check=True, capture_output=True, text=True)
        
        print("✅ Executable built successfully!")
        print(f"📁 Output: dist/ImageOrganizerPro.exe")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    
    return True

def create_installer_script():
    """Create Inno Setup installer script"""
    installer_script = """
[Setup]
AppName=Image Organizer Pro
AppVersion=1.0.0
AppPublisher=Edward Manela Jr
AppPublisherURL=https://github.com/Edward-Manela-jr/Room_5
AppSupportURL=https://github.com/Edward-Manela-jr/Room_5
AppUpdatesURL=https://github.com/Edward-Manela-jr/Room_5
DefaultDirName={pf}\\Image Organizer Pro
DefaultGroupName=Image Organizer Pro
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=installer
OutputBaseFilename=ImageOrganizerProSetup
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\\ImageOrganizerPro.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\\Image Organizer Pro"; Filename: "{app}\\ImageOrganizerPro.exe"
Name: "{commondesktop}\\Image Organizer Pro"; Filename: "{app}\\ImageOrganizerPro.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\\ImageOrganizerPro.exe"; Description: "{cm:LaunchProgram}"; Flags: nowait postinstall skipifsilent
"""
    
    with open('installer_script.iss', 'w') as f:
        f.write(installer_script.strip())
    
    print("✅ Created Inno Setup installer script")

def create_license():
    """Create license file"""
    license_text = """
Image Organizer Pro - License Agreement

Copyright (c) 2026 Edward Manela Jr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    
    with open('LICENSE.txt', 'w') as f:
        f.write(license_text.strip())
    
    print("✅ Created license file")

def main():
    """Main build process"""
    print("🚀 Building Image Organizer Pro for Windows...")
    
    # Check if we're on Windows
    if sys.platform != "win32":
        print("⚠️  Warning: This build script is designed for Windows")
        print("   You can still build, but testing should be done on Windows")
    
    # Install requirements
    install_requirements()
    
    # Create necessary files
    create_spec_file()
    create_version_info()
    create_license()
    create_installer_script()
    
    # Build executable
    if build_executable():
        print("\n🎉 Build completed successfully!")
        print("\n📦 Distribution files created:")
        print("   📁 dist/ImageOrganizerPro.exe - Main executable")
        print("   📄 installer_script.iss - Inno Setup script")
        print("   📄 LICENSE.txt - License file")
        
        print("\n📋 Next steps:")
        print("   1. Test the executable: dist/ImageOrganizerPro.exe")
        print("   2. Create installer using Inno Setup:")
        print("      - Download Inno Setup from https://jrsoftware.org/isinfo.php")
        print("      - Open installer_script.iss")
        print("      - Build the installer")
        print("   3. Distribute the installer file")
        
    else:
        print("\n❌ Build failed. Check the error messages above.")

if __name__ == "__main__":
    main()
