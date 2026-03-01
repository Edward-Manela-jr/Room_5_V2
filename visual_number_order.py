#!/usr/bin/env python3
"""
Visual Number Ordering System
Click numbers 1-12 in the order they appear in images
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import calendar

class VisualNumberOrder:
    def __init__(self, folder_path, station, year, obs_time="06"):
        self.folder_path = Path(folder_path)
        self.station = station
        self.year = year
        self.obs_time = obs_time
        self.selected_order = []
        self.number_buttons = {}
        self.selected_colors = {}
        
    def create_selection_window(self, parent_callback=None):
        """Create visual number selection window"""
        window = tk.Toplevel()
        window.title("Visual Number Ordering")
        window.geometry("600x500")
        window.resizable(False, False)
        
        # Title
        title_label = tk.Label(window, text="Click numbers in the order they appear in images", 
                             font=('Arial', 14, 'bold'))
        title_label.pack(pady=20)
        
        # Info frame
        info_frame = tk.Frame(window)
        info_frame.pack(pady=10)
        
        tk.Label(info_frame, text=f"Folder: {self.folder_path.name}", font=('Arial', 10)).pack()
        tk.Label(info_frame, text=f"Station: {self.station} | Year: {self.year} | Time: {self.obs_time}", 
                font=('Arial', 10)).pack()
        
        # Selected order display
        order_frame = tk.Frame(window)
        order_frame.pack(pady=20)
        
        tk.Label(order_frame, text="Selected Order:", font=('Arial', 12, 'bold')).pack()
        
        self.order_display = tk.Label(order_frame, text="No numbers selected yet", 
                                     font=('Arial', 11), fg="blue", width=40, height=2, 
                                     relief=tk.SUNKEN, anchor='w')
        self.order_display.pack(pady=10)
        
        # Number buttons grid
        buttons_frame = tk.Frame(window)
        buttons_frame.pack(pady=20)
        
        # Create 3x4 grid of number buttons
        for i in range(1, 13):
            row = (i - 1) // 4
            col = (i - 1) % 4
            
            btn = tk.Button(buttons_frame, text=str(i), font=('Arial', 16, 'bold'),
                          width=8, height=3, bg='lightgray',
                          command=lambda num=i: self.select_number(num))
            btn.grid(row=row, column=col, padx=5, pady=5)
            self.number_buttons[num] = btn
        
        # Control buttons
        control_frame = tk.Frame(window)
        control_frame.pack(pady=20)
        
        tk.Button(control_frame, text="Clear Selection", command=self.clear_selection,
                 font=('Arial', 10), width=15).pack(side='left', padx=5)
        
        tk.Button(control_frame, text="Apply Ordering", command=lambda: self.apply_ordering(window, parent_callback),
                 font=('Arial', 10, 'bold'), width=15, bg='lightgreen').pack(side='left', padx=5)
        
        tk.Button(control_frame, text="Cancel", command=window.destroy,
                 font=('Arial', 10), width=15).pack(side='left', padx=5)
        
        # Instructions
        instructions = tk.Frame(window)
        instructions.pack(pady=10, padx=20, fill='x')
        
        inst_text = """Instructions:
1. Open your image viewer with the selected folder
2. Look at the first image and determine its month
3. Click the corresponding number button
4. Continue for all images in order
5. Numbers will highlight as you select them
6. Click 'Apply Ordering' when done"""
        
        tk.Label(instructions, text=inst_text, justify='left', font=('Arial', 9)).pack()
        
        return window
    
    def select_number(self, number):
        """Select a number and update the order"""
        if number not in self.selected_order:
            self.selected_order.append(number)
            self.update_display()
            self.highlight_button(number)
    
    def highlight_button(self, number):
        """Highlight a selected button"""
        colors = ['lightblue', 'lightgreen', 'yellow', 'orange', 'pink', 
                 'lightcoral', 'lavender', 'wheat', 'lightcyan', 
                 'mistyrose', 'honeydew', 'mintcream']
        
        color_index = len(self.selected_order) - 1
        color = colors[color_index % len(colors)]
        
        self.number_buttons[number].config(bg=color)
        self.selected_colors[number] = color
    
    def update_display(self):
        """Update the selected order display"""
        if self.selected_order:
            order_text = " → ".join([str(num) for num in self.selected_order])
            self.order_display.config(text=order_text)
        else:
            self.order_display.config(text="No numbers selected yet")
    
    def clear_selection(self):
        """Clear all selections"""
        self.selected_order = []
        self.update_display()
        
        # Reset all button colors
        for btn in self.number_buttons.values():
            btn.config(bg='lightgray')
    
    def apply_ordering(self, window, parent_callback=None):
        """Apply the visual ordering to rename files"""
        if not self.selected_order:
            messagebox.showerror("Error", "No numbers selected!")
            return
        
        # Get images in folder
        images = sorted(self.folder_path.glob("*.*"), key=lambda x: x.name.lower())
        
        if len(images) != len(self.selected_order):
            messagebox.showerror("Error", 
                               f"Mismatch: {len(images)} images vs {len(self.selected_order)} numbers selected")
            return
        
        # Apply renaming
        results = []
        try:
            for img_path, month in zip(images, self.selected_order):
                # Build new name
                new_name = f"{self.station}-{self.year}{month:02d}{calendar.monthrange(self.year, month)[1]:02d}{self.obs_time}{img_path.suffix}"
                new_path = self.folder_path / new_name
                
                # Rename file
                img_path.rename(new_path)
                results.append(f"{img_path.name} → {new_name}")
            
            messagebox.showinfo("Success", "Visual ordering applied successfully!")
            if parent_callback:
                parent_callback(results)
            window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply ordering: {e}")

def main():
    """Standalone test"""
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python visual_number_order.py <folder> <station> <year> [obs_time]")
        return
    
    folder = sys.argv[1]
    station = sys.argv[2]
    year = int(sys.argv[3])
    obs_time = sys.argv[4] if len(sys.argv) > 4 else "06"
    
    def callback(results):
        print("Results:")
        for result in results:
            print(f"  {result}")
    
    orderer = VisualNumberOrder(folder, station, year, obs_time)
    window = orderer.create_selection_window(callback)
    window.mainloop()

if __name__ == "__main__":
    main()
