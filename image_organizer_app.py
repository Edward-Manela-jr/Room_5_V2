#!/usr/bin/env python3
"""
Image Organizer App - Windows GUI Application
A comprehensive tool for organizing and fixing image collections
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk, ExifTags
from pathlib import Path
import datetime

# Import our existing modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class ImageOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Organizer Pro")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Variables
        self.source_folder = ""
        self.is_processing = False
        
        # Setup UI
        self.setup_ui()
        self.setup_styles()
        
    def setup_styles(self):
        """Modern styling"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 10, 'bold'))
        
    def setup_ui(self):
        """Main UI setup"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Folder Organization
        self.org_tab = ttk.Frame(notebook)
        notebook.add(self.org_tab, text='📁 Folder Organization')
        self.setup_org_tab()
        
        # Tab 2: Image Rotation
        self.rotate_tab = ttk.Frame(notebook)
        notebook.add(self.rotate_tab, text='🔄 Image Rotation')
        self.setup_rotate_tab()
        
        # Tab 3: Interactive Fix
        self.interactive_tab = ttk.Frame(notebook)
        notebook.add(self.interactive_tab, text='👁️ Interactive Fix')
        self.setup_interactive_tab()
        
        # Tab 4: Settings
        self.settings_tab = ttk.Frame(notebook)
        notebook.add(self.settings_tab, text='⚙️ Settings')
        self.setup_settings_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_org_tab(self):
        """Folder organization tab"""
        # Main frame
        main_frame = ttk.Frame(self.org_tab, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="📁 Folder Organization", style='Title.TLabel')
        title.pack(pady=(0, 20))
        
        # Folder selection
        folder_frame = ttk.LabelFrame(main_frame, text="Select Folder", padding="10")
        folder_frame.pack(fill='x', pady=(0, 20))
        
        self.folder_var = tk.StringVar()
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_var, width=70)
        folder_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(folder_frame, text="Browse", command=self.browse_folder)
        browse_btn.pack(side='right')
        
        # Operations
        ops_frame = ttk.LabelFrame(main_frame, text="Operations", padding="10")
        ops_frame.pack(fill='x', pady=(0, 20))
        
        btn_frame = ttk.Frame(ops_frame)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="📂 Organize Images", command=self.organize_images).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="↩️ Undo Organization", command=self.undo_organization).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🧹 Clean Empty Folders", command=self.clean_folders).pack(side='left', padx=5)
        
        # Info
        info_frame = ttk.LabelFrame(main_frame, text="Information", padding="10")
        info_frame.pack(fill='both', expand=True)
        
        info_text = """
📂 Organize Images: Sort images into town/year folders
   - Images: Town/Year/ structure
   - Documents: Extension/Town/ structure

↩️ Undo Organization: Move all files back to main folder

🧹 Clean Empty Folders: Remove all empty directories
        """
        
        info_label = ttk.Label(info_frame, text=info_text.strip(), justify='left')
        info_label.pack()
        
    def setup_rotate_tab(self):
        """Image rotation tab"""
        main_frame = ttk.Frame(self.rotate_tab, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="🔄 Image Rotation", style='Title.TLabel')
        title.pack(pady=(0, 20))
        
        # Folder selection
        folder_frame = ttk.LabelFrame(main_frame, text="Select Folder", padding="10")
        folder_frame.pack(fill='x', pady=(0, 20))
        
        self.rotate_folder_var = tk.StringVar()
        folder_entry = ttk.Entry(folder_frame, textvariable=self.rotate_folder_var, width=70)
        folder_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(folder_frame, text="Browse", command=self.browse_rotate_folder)
        browse_btn.pack(side='right')
        
        # Operations
        ops_frame = ttk.LabelFrame(main_frame, text="Rotation Options", padding="10")
        ops_frame.pack(fill='x', pady=(0, 20))
        
        btn_frame = ttk.Frame(ops_frame)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="🔧 Fix EXIF Orientation", command=self.fix_exif_rotation).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="📐 Fix All Rotations", command=self.fix_all_rotations).pack(side='left', padx=5)
        
        # Info
        info_frame = ttk.LabelFrame(main_frame, text="Information", padding="10")
        info_frame.pack(fill='both', expand=True)
        
        info_text = """
🔧 Fix EXIF Orientation: Fix images based on EXIF data
   - Only fixes images with EXIF orientation tags
   - Preserves image quality
   - Handles common orientation values (1-8)

📐 Fix All Rotations: Convert all portrait to landscape
   - Rotates portrait images to landscape orientation
   - Useful for bulk orientation correction
   - May need manual review for perfect results
        """
        
        info_label = ttk.Label(info_frame, text=info_text.strip(), justify='left')
        info_label.pack()
        
    def setup_interactive_tab(self):
        """Interactive fix tab"""
        main_frame = ttk.Frame(self.interactive_tab, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="👁️ Interactive Fix", style='Title.TLabel')
        title.pack(pady=(0, 20))
        
        # Folder selection
        folder_frame = ttk.LabelFrame(main_frame, text="Select Folder", padding="10")
        folder_frame.pack(fill='x', pady=(0, 20))
        
        self.interactive_folder_var = tk.StringVar()
        folder_entry = ttk.Entry(folder_frame, textvariable=self.interactive_folder_var, width=70)
        folder_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(folder_frame, text="Browse", command=self.browse_interactive_folder)
        browse_btn.pack(side='right')
        
        # Operations
        ops_frame = ttk.LabelFrame(main_frame, text="Interactive Review", padding="10")
        ops_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Button(ops_frame, text="👁️ Start Interactive Review", command=self.start_interactive_review).pack()
        
        # Info
        info_frame = ttk.LabelFrame(main_frame, text="Information", padding="10")
        info_frame.pack(fill='both', expand=True)
        
        info_text = """
👁️ Start Interactive Review: Manual image rotation review
   - Opens each portrait image in default viewer
   - You choose the correct rotation direction
   - Options: 0°, 90°, 180°, 270°, skip, or quit
   - Perfect for precise orientation control

⚠️  Note: This process opens your default image viewer
   You'll need to switch between the app and viewer
        """
        
        info_label = ttk.Label(info_frame, text=info_text.strip(), justify='left')
        info_label.pack()
        
    def setup_settings_tab(self):
        """Settings tab"""
        main_frame = ttk.Frame(self.settings_tab, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="⚙️ Settings", style='Title.TLabel')
        title.pack(pady=(0, 20))
        
        # Info
        info_frame = ttk.LabelFrame(main_frame, text="About", padding="10")
        info_frame.pack(fill='x', pady=(0, 20))
        
        about_text = """
Image Organizer Pro v1.0

A comprehensive tool for organizing and fixing image collections.

Features:
• Automatic folder organization by town and year
• EXIF-based orientation correction
• Bulk portrait-to-landscape conversion
• Interactive manual review
• Support for multiple image formats

Created by: Edward Manela Jr
GitHub: https://github.com/Edward-Manela-jr/Room_5
        """
        
        about_label = ttk.Label(info_frame, text=about_text.strip(), justify='left')
        about_label.pack()
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.pack(fill='both', expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.pack(fill='both', expand=True)
        
        # Clear log button
        ttk.Button(log_frame, text="Clear Log", command=self.clear_log).pack(pady=(10, 0))
        
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_log(self):
        """Clear the log"""
        self.log_text.delete(1.0, tk.END)
        
    def browse_folder(self):
        """Browse for folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)
            
    def browse_rotate_folder(self):
        """Browse for rotation folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.rotate_folder_var.set(folder)
            
    def browse_interactive_folder(self):
        """Browse for interactive folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.interactive_folder_var.set(folder)
            
    def organize_images(self):
        """Run folder organization"""
        folder = self.folder_var.get()
        if not folder or not Path(folder).exists():
            messagebox.showerror("Error", "Please select a valid folder")
            return
            
        if self.is_processing:
            messagebox.showwarning("Warning", "Another operation is in progress")
            return
            
        self.is_processing = True
        self.status_var.set("Organizing images...")
        
        def run_org():
            try:
                # Import and run folder sorter
                import folder_sorter
                self.log_message(f"Starting organization of: {folder}")
                folder_sorter.sort_images_by_name(folder)
                self.log_message("Organization complete!")
                messagebox.showinfo("Success", "Image organization completed!")
            except Exception as e:
                self.log_message(f"Error: {e}")
                messagebox.showerror("Error", f"Organization failed: {e}")
            finally:
                self.is_processing = False
                self.status_var.set("Ready")
                
        threading.Thread(target=run_org, daemon=True).start()
        
    def undo_organization(self):
        """Run undo organization"""
        folder = self.folder_var.get()
        if not folder or not Path(folder).exists():
            messagebox.showerror("Error", "Please select a valid folder")
            return
            
        if self.is_processing:
            messagebox.showwarning("Warning", "Another operation is in progress")
            return
            
        self.is_processing = True
        self.status_var.set("Undoing organization...")
        
        def run_undo():
            try:
                import undo_sort
                self.log_message(f"Starting undo of: {folder}")
                undo_sort.undo_sort(folder)
                self.log_message("Undo complete!")
                messagebox.showinfo("Success", "Undo completed!")
            except Exception as e:
                self.log_message(f"Error: {e}")
                messagebox.showerror("Error", f"Undo failed: {e}")
            finally:
                self.is_processing = False
                self.status_var.set("Ready")
                
        threading.Thread(target=run_undo, daemon=True).start()
        
    def clean_folders(self):
        """Clean empty folders"""
        folder = self.folder_var.get()
        if not folder or not Path(folder).exists():
            messagebox.showerror("Error", "Please select a valid folder")
            return
            
        if self.is_processing:
            messagebox.showwarning("Warning", "Another operation is in progress")
            return
            
        self.is_processing = True
        self.status_var.set("Cleaning empty folders...")
        
        def run_clean():
            try:
                import clean_empty_folders
                self.log_message(f"Cleaning empty folders in: {folder}")
                clean_empty_folders.remove_empty_folders(folder)
                self.log_message("Cleanup complete!")
                messagebox.showinfo("Success", "Empty folders cleaned!")
            except Exception as e:
                self.log_message(f"Error: {e}")
                messagebox.showerror("Error", f"Cleanup failed: {e}")
            finally:
                self.is_processing = False
                self.status_var.set("Ready")
                
        threading.Thread(target=run_clean, daemon=True).start()
        
    def fix_exif_rotation(self):
        """Fix EXIF rotation"""
        folder = self.rotate_folder_var.get()
        if not folder or not Path(folder).exists():
            messagebox.showerror("Error", "Please select a valid folder")
            return
            
        if self.is_processing:
            messagebox.showwarning("Warning", "Another operation is in progress")
            return
            
        self.is_processing = True
        self.status_var.set("Fixing EXIF orientation...")
        
        def run_fix():
            try:
                import fix_image_orientation
                self.log_message(f"Fixing EXIF orientation in: {folder}")
                fix_image_orientation.fix_image_orientation(folder)
                self.log_message("EXIF fix complete!")
                messagebox.showinfo("Success", "EXIF orientation fixed!")
            except Exception as e:
                self.log_message(f"Error: {e}")
                messagebox.showerror("Error", f"EXIF fix failed: {e}")
            finally:
                self.is_processing = False
                self.status_var.set("Ready")
                
        threading.Thread(target=run_fix, daemon=True).start()
        
    def fix_all_rotations(self):
        """Fix all rotations"""
        folder = self.rotate_folder_var.get()
        if not folder or not Path(folder).exists():
            messagebox.showerror("Error", "Please select a valid folder")
            return
            
        if self.is_processing:
            messagebox.showwarning("Warning", "Another operation is in progress")
            return
            
        self.is_processing = True
        self.status_var.set("Fixing all rotations...")
        
        def run_fix():
            try:
                import fix_all_rotations
                self.log_message(f"Fixing all rotations in: {folder}")
                fix_all_rotations.detect_and_fix_rotation(folder, auto_fix=True)
                self.log_message("All rotations fixed!")
                messagebox.showinfo("Success", "All rotations fixed!")
            except Exception as e:
                self.log_message(f"Error: {e}")
                messagebox.showerror("Error", f"Rotation fix failed: {e}")
            finally:
                self.is_processing = False
                self.status_var.set("Ready")
                
        threading.Thread(target=run_fix, daemon=True).start()
        
    def start_interactive_review(self):
        """Start interactive review"""
        folder = self.interactive_folder_var.get()
        if not folder or not Path(folder).exists():
            messagebox.showerror("Error", "Please select a valid folder")
            return
            
        if self.is_processing:
            messagebox.showwarning("Warning", "Another operation is in progress")
            return
            
        self.is_processing = True
        self.status_var.set("Starting interactive review...")
        
        def run_interactive():
            try:
                import interactive_rotation_cli
                self.log_message(f"Starting interactive review in: {folder}")
                messagebox.showinfo("Info", "Interactive review will start in a new window.\nFollow the instructions in the terminal.")
                interactive_rotation_cli.interactive_rotation_fix(folder)
                self.log_message("Interactive review complete!")
            except Exception as e:
                self.log_message(f"Error: {e}")
                messagebox.showerror("Error", f"Interactive review failed: {e}")
            finally:
                self.is_processing = False
                self.status_var.set("Ready")
                
        threading.Thread(target=run_interactive, daemon=True).start()

def main():
    """Main entry point"""
    root = tk.Tk()
    app = ImageOrganizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
