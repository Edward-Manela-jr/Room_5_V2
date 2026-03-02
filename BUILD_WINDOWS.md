# Building Image Organizer Pro for Windows

This guide explains how to build the Windows executable and create an installer using Inno Setup.

## Prerequisites

- Windows 10/11
- Python 3.8 or higher
- Inno Setup 6.x (for creating the installer)

## Step 1: Build the Windows Executable

### Option A: Using the Build Script (Recommended)

1. Open a command prompt in the `Room_5` directory:
   ```
   cd Room_5
   ```

2. Run the build script:
   ```
   python build_windows_app.py
   ```

3. The script will:
   - Install required packages (pyinstaller, pillow)
   - Create the spec file
   - Create version info
   - Build the executable

4. When complete, you'll find:
   - `dist/ImageOrganizerPro.exe` - The standalone executable
   - `installer_script.iss` - The Inno Setup script

### Option B: Manual Build

1. Install dependencies:
   ```
   pip install pyinstaller pillow
   ```

2. Run PyInstaller:
   ```
   pyinstaller --clean --onefile --windowed image_organizer.spec
   ```

3. The executable will be in `dist/ImageOrganizerPro.exe`

## Step 2: Create Installer with Inno Setup

### Download and Install Inno Setup

1. Download Inno Setup from: https://jrsoftware.org/isinfo.php
2. Run the installer and follow the prompts

### Build the Installer

1. Open Inno Setup Compiler
2. Click **File** → **Open**
3. Navigate to `Room_5/installer_script.iss` and open it
4. Click **Build** → **Compile** (or press F9)
5. Wait for compilation to complete

### Locate the Installer

The installer will be created in:
```
Room_5/installer/ImageOrganizerProSetup.exe
```

## Project Structure

After building, your directory should contain:

```
Room_5/
├── dist/
│   └── ImageOrganizerPro.exe       # Built executable
├── installer/
│   └── ImageOrganizerProSetup.exe  # Installer (after Inno Setup)
├── image_organizer.spec             # PyInstaller spec
├── installer_script.iss             # Inno Setup script
├── version_info.txt                 # Windows version info
├── LICENSE.txt                      # License file
└── README.md                        # Application readme
```

## Troubleshooting

### PyInstaller Issues
- Make sure all Python dependencies are installed
- Run `pip install -r requirements.txt` if a requirements file exists

### Inno Setup Issues
- Ensure Inno Setup is installed correctly
- Check that `dist/ImageOrganizerPro.exe` exists before building
- Verify the path in the `[Files]` section of `installer_script.iss`

### Common Errors
- **"dist\ImageOrganizerPro.exe not found"**: Run the build script first
- **Icon not showing**: Add `icon.ico` to the Room_5 directory and update the spec file
