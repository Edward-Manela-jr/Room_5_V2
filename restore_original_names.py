import os
import re
from pathlib import Path

def restore_original_names(folder):
    """Restore original names from station format back to 1.jpg, 2.jpg, etc."""
    folder = Path(folder)
    
    # Get all files and sort them (they should be in month order)
    files = sorted(folder.glob("*.*"))
    
    if len(files) != 12:
        print(f"❌ Error: Expected 12 files, found {len(files)}")
        return
    
    # Map month numbers to original names (1-12)
    month_mapping = {
        '01': '1.jpg',
        '02': '2.jpg', 
        '03': '3.jpg',
        '04': '4.jpg',
        '05': '5.jpg',
        '06': '6.jpg',
        '07': '7.jpg',
        '08': '8.jpg',
        '09': '9.jpg',
        '10': '10.jpg',
        '11': '11.jpg',
        '12': '12.jpg'
    }
    
    for file_path in files:
        # Extract month from filename like "CHIPEPO01-MOZ304A-2002013106.jpg"
        match = re.search(r'-(\d{4})(\d{2})\d{2}\d{2}\.', file_path.name)
        
        if match:
            year = match.group(1)
            month = match.group(2)
            
            if month in month_mapping:
                new_name = month_mapping[month]
                new_path = folder / new_name
                
                # Rename back to original
                file_path.rename(new_path)
                print(f"Restored: {file_path.name} → {new_name}")
            else:
                print(f"⚠️  Could not determine month for: {file_path.name}")
        else:
            print(f"⚠️  Could not parse filename: {file_path.name}")
    
    print("\n✅ DONE — All files restored to original names!")

# Use the same folder as your rename.py
FOLDER = "/home/edward-manela-jr/Documents/ZMD/Applications/files/ALL/Chipepo/Chipepo 2002"

print("Restoring original names...")
restore_original_names(FOLDER)
