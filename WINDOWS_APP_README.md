# Image Organizer Pro - Windows Application

A professional Windows application for organizing and fixing image collections.

## 🚀 Features

### 📁 Folder Organization
- **Automatic sorting** by town name and year
- **Smart year extraction** from complex filenames
- **Document handling** by file extension
- **Undo functionality** to reverse changes
- **Clean empty folders** option

### 🔄 Image Rotation
- **EXIF-based correction** for camera orientation
- **Bulk portrait-to-landscape** conversion
- **Interactive manual review** for perfect results
- **High-quality processing** with 95% JPEG quality

### 👁️ Interactive Review
- **Manual rotation control** for each image
- **Default viewer integration** for easy review
- **Progress tracking** and skip options
- **Perfect for precise orientation control**

## 📦 Installation

### Option 1: Download Installer (Recommended)
1. Download `ImageOrganizerProSetup.exe` from releases
2. Run the installer
3. Follow the installation wizard
4. Launch from Start Menu or desktop

### Option 2: Portable Version
1. Download `ImageOrganizerPro.exe`
2. Place in any folder
3. Double-click to run

## 🎯 Usage

### Quick Start
1. **Launch** Image Organizer Pro
2. **Select folder** with your images
3. **Choose operation**:
   - 📂 Organize Images
   - 🔄 Fix Rotations
   - 👁️ Interactive Review
4. **Click Start** and wait for completion

### Detailed Workflow

#### 1. Folder Organization
```
Input: Folder with mixed images
Output: Organized structure
├── TownName/Year/
├── Extension/TownName/
└── Documents/
```

#### 2. Rotation Fix
```
Step 1: Fix EXIF Orientation (automatic)
Step 2: Fix All Rotations (portrait → landscape)
Step 3: Interactive Review (manual fine-tuning)
```

#### 3. Interactive Review
```
1. Opens each portrait image
2. You choose rotation:
   - 0°: Keep as is
   - 90°: Rotate clockwise
   - 180°: Flip upside down
   - 270°: Rotate counter-clockwise
   - Skip: Move to next
   - Quit: Exit review
```

## 🔧 Technical Details

### Supported Formats
- **Images**: JPG, JPEG, PNG, GIF, BMP, TIFF, WEBP
- **Documents**: PDF, DOC, DOCX, TXT, CSV (organized by extension)

### File Naming Patterns
```
✅ Supported: "TownName 2023_251216_121853_1-12.jpg"
✅ Supported: "Kabwe 1985 photo.jpg"
✅ Supported: "Livingstone 2020-01-15 image.png"
❌ Not supported: "IMG_1234.jpg" (no town name)
```

### Performance
- **Processes 2,300+ images** in minutes
- **Multi-threaded** operations
- **Memory efficient** processing
- **Progress tracking** throughout

## 🛠️ Development

### Building from Source
```bash
# Install requirements
pip install pyinstaller pillow

# Build executable
python build_windows_app.py

# Create installer (requires Inno Setup)
# Open installer_script.iss in Inno Setup
# Build the installer
```

### Requirements
- Python 3.8+
- PIL/Pillow
- tkinter (included with Python)
- PyInstaller (for building)
- Inno Setup (for installer)

## 📄 License

MIT License - see LICENSE.txt for details.

## 🤝 Support

- **GitHub**: https://github.com/Edward-Manela-jr/Room_5
- **Issues**: Report bugs on GitHub Issues
- **Features**: Request features on GitHub Discussions

## 📊 Version History

### v1.0.0 (2026-02-28)
- Initial release
- Folder organization by town/year
- EXIF and bulk rotation fixes
- Interactive manual review
- Windows GUI application
- Professional installer

---

**Created by Edward Manela Jr**  
*Professional image organization solution*
