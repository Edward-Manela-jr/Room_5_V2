# Image Organizer Pro - Software Research Project Documentation

---

## Project Title
**Image Organizer Pro: A Desktop Application for Automated Weather Station Image Management and Organization**

---

## Problem Statement

Weather station networks in developing regions often rely on manual processes to capture, organize, and rename photographic data from field stations. This manual approach presents several challenges:

1. **Inconsistent Naming Conventions**: Images are often saved with generic names (e.g., 1.jpg, 2.jpg) making it difficult to associate them with specific stations, dates, or months.

2. **Time-Consuming Organization**: Field researchers spend significant time manually sorting and renaming hundreds or thousands of images into proper folder structures.

3. **Data Integrity Risks**: Manual renaming is prone to errors, potentially leading to data loss or misinterpretation of historical weather data.

4. **Limited Preview Capabilities**: Existing tools lack specialized features like cropped previews and zoom functionality needed for efficient image review and month selection.

5. **Lack of Standardization**: Different stations may use different naming conventions, making it difficult to aggregate and analyze data across the network.

---

## Aim

To develop a standalone Windows desktop application that automates the organization, renaming, and management of weather station image collections, while providing an intuitive interface for reviewing images and selecting appropriate metadata such as month values.

---

## Objectives

### 1. Automate Image Organization
Develop algorithms that automatically sort images into hierarchical folder structures based on station codes, year, and other metadata, eliminating the need for manual file organization.

### 2. Implement Smart Renaming System
Create a flexible renaming system that converts generic filenames (e.g., 1.jpg) to standardized formats incorporating station identifiers, dates, and observation times (e.g., CHIPEPO01-2008013106.jpg).

### 3. Provide Interactive Review Interface
Build a user-friendly interface with features like cropped image previews and adjustable zoom (0.5x to 3.0x) to enable efficient manual review and correction of image metadata.

### 4. Enable Batch Processing Capabilities
Support bulk operations allowing users to process entire folders of images simultaneously, significantly reducing the time required for large-scale data management tasks.

---

## Technical Approach

### Technology Stack
- **Language**: Python 3.12
- **GUI Framework**: Tkinter (built-in Python GUI library)
- **Image Processing**: Pillow (PIL Fork)
- **Packaging**: PyInstaller (standalone .exe generation)
- **Installer**: Inno Setup

### Key Features Implemented
1. Folder Organization (Town/Year structure)
2. Image Rotation (EXIF-based and manual)
3. Station Alias Management
4. Interactive Fix Mode
5. Audio-Based Month Ordering
6. Visual Number Ordering
7. Month Selector with Cropped Previews
8. Zoom Slider (0.5x - 3.0x)
9. PIN-Based Authentication

---

## Expected Outcomes

1. A fully functional Windows executable that runs without requiring Python installation
2. Reduced image processing time by up to 80% compared to manual methods
3. Standardized file naming across all weather stations
4. Improved data integrity through automated quality checks
5. User-friendly interface requiring minimal training

---

## Conclusion

Image Organizer Pro addresses the critical need for automated image management in weather station networks. By combining intelligent organization algorithms with an interactive review interface, the application significantly improves the efficiency and reliability of field data management processes.

---

*Document prepared for Software Research Project submission*
*Author: Edward Manela Jr*
*Date: March 2026*
