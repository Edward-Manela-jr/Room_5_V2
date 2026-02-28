import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ExifTags
from pathlib import Path

class InteractiveRotationFix:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Image Rotation Fix")
        self.root.geometry("900x700")
        
        self.source_folder = ""
        self.portrait_files = []
        self.current_index = 0
        self.image_label = None
        self.status_label = None
        self.progress_label = None
        self.image_info_label = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Folder selection
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(folder_frame, text="Source Folder:").grid(row=0, column=0, padx=(0, 5))
        self.folder_var = tk.StringVar()
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_var, width=60)
        folder_entry.grid(row=0, column=1, padx=(0, 5))
        
        browse_btn = ttk.Button(folder_frame, text="Browse", command=self.browse_folder)
        browse_btn.grid(row=0, column=2, padx=(0, 5))
        
        scan_btn = ttk.Button(folder_frame, text="Scan for Portrait Images", command=self.scan_portrait_images)
        scan_btn.grid(row=0, column=3)
        
        # Progress info
        self.progress_label = ttk.Label(main_frame, text="No folder selected")
        self.progress_label.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
        # Image display area
        image_frame = ttk.LabelFrame(main_frame, text="Image Preview", padding="10")
        image_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.image_label = ttk.Label(image_frame, text="No image loaded")
        self.image_label.grid(row=0, column=0)
        
        # Image info
        self.image_info_label = ttk.Label(main_frame, text="")
        self.image_info_label.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        # Rotation buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Button(button_frame, text="↺ Rotate 90° CCW", command=lambda: self.rotate_image(90)).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Keep As Is", command=lambda: self.rotate_image(0)).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="↻ Rotate 90° CW", command=lambda: self.rotate_image(270)).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="↻ Rotate 180°", command=lambda: self.rotate_image(180)).grid(row=0, column=3, padx=5)
        
        # Navigation buttons
        nav_frame = ttk.Frame(main_frame)
        nav_frame.grid(row=5, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Button(nav_frame, text="← Previous", command=self.previous_image).grid(row=0, column=0, padx=5)
        ttk.Button(nav_frame, text="Next →", command=self.next_image).grid(row=0, column=1, padx=5)
        ttk.Button(nav_frame, text="Skip", command=self.skip_image).grid(row=0, column=2, padx=5)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.grid(row=6, column=0, columnspan=3)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)
            
    def scan_portrait_images(self):
        self.source_folder = self.folder_var.get()
        if not self.source_folder or not Path(self.source_folder).exists():
            messagebox.showerror("Error", "Please select a valid folder")
            return
            
        self.status_label.config(text="Scanning for portrait images...")
        self.root.update()
        
        # Find all portrait images
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        self.portrait_files = []
        
        for root, dirs, files in os.walk(self.source_folder):
            for filename in files:
                file_path = Path(root) / filename
                if file_path.suffix.lower() in image_extensions:
                    try:
                        with Image.open(file_path) as img:
                            width, height = img.size
                            if height > width:  # Portrait
                                self.portrait_files.append(file_path)
                    except:
                        continue
        
        if not self.portrait_files:
            messagebox.showinfo("Info", "No portrait images found")
            self.status_label.config(text="No portrait images found")
            return
            
        self.current_index = 0
        self.progress_label.config(text=f"Found {len(self.portrait_files)} portrait images")
        self.status_label.config(text="Ready to review images")
        self.load_current_image()
        
    def load_current_image(self):
        if not self.portrait_files or self.current_index >= len(self.portrait_files):
            self.show_completion()
            return
            
        file_path = self.portrait_files[self.current_index]
        
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                
                # Resize for display (max 600px height)
                max_height = 600
                if height > max_height:
                    ratio = max_height / height
                    new_width = int(width * ratio)
                    new_height = max_height
                    display_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                else:
                    display_img = img.copy()
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(display_img)
                self.image_label.config(image=photo, text="")
                self.image_label.image = photo  # Keep reference
                
                # Update info
                relative_path = file_path.relative_to(self.source_folder)
                self.image_info_label.config(
                    text=f"Image {self.current_index + 1}/{len(self.portrait_files)}: {relative_path} ({width}x{height})"
                )
                self.progress_label.config(
                    text=f"Progress: {self.current_index + 1}/{len(self.portrait_files)} portrait images"
                )
                
        except Exception as e:
            self.image_label.config(text=f"Error loading image: {e}")
            self.image_info_label.config(text=f"File: {file_path}")
            
    def rotate_image(self, degrees):
        if not self.portrait_files or self.current_index >= len(self.portrait_files):
            return
            
        file_path = self.portrait_files[self.current_index]
        
        try:
            with Image.open(file_path) as img:
                if degrees != 0:
                    rotated_img = img.rotate(-degrees, expand=True)  # Negative for clockwise
                    rotated_img.save(file_path, quality=95)
                    print(f"Rotated {file_path.name} by {degrees}°")
                
                self.next_image()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rotate image: {e}")
            
    def next_image(self):
        self.current_index += 1
        self.load_current_image()
        
    def previous_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_image()
            
    def skip_image(self):
        self.next_image()
        
    def show_completion(self):
        self.image_label.config(image="", text="✅ All portrait images reviewed!")
        self.image_info_label.config(text="")
        self.progress_label.config(text=f"Completed: {len(self.portrait_files)} portrait images")
        self.status_label.config(text="Review complete!")

def main():
    if len(sys.argv) > 1:
        # Command line mode - just scan and show count
        source_folder = sys.argv[1]
        print(f"Scanning {source_folder} for portrait images...")
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        portrait_files = []
        
        for root, dirs, files in os.walk(source_folder):
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
        
        print(f"Found {len(portrait_files)} portrait images")
        print("Run without command line arguments to use interactive mode")
        
    else:
        # Interactive mode
        root = tk.Tk()
        app = InteractiveRotationFix(root)
        root.mainloop()

if __name__ == "__main__":
    main()
