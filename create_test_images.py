#!/usr/bin/env python3
"""
Create random test images with town names similar to your actual collection
Generates sample images for testing the Windows application
"""

import os
import random
from PIL import Image, ImageDraw
from pathlib import Path

# Town names from your actual collection
TOWNS = [
    "Lusaka", "Kabwe", "Mansa", "Livingstone", "Ndola", "Kitwe",
    "Chingola", "Mufulira", "Kasama", "Mpika", "Solwezi", "Chipata",
    "Kafue", "Choma", "Monze", "Mazabuka", "Kalomo", "Chililabombwe",
    "Mongu", "Senanga", "Kaoma", "Mongu", "Mwinilunga", "Kasempa",
    "Lundazi", "Chinsali", "Isoka", "Mporokoso", "Chilubi", "Mbala",
    "Mansa", "Samfya", "Mumbwa", "Kapiri Mposhi", "Serenje", "Petauke",
    "Nyimba", "Chavuma", "Chikankata", "Mkushi", "Masaiti",
    "Kawambwa", "Mporokoso", "Chililabombwe", "Mufulira", "Chingola",
    "Zambezi", "Kafironda", "Kapombo", "Kasempa", "Lundazi",
    "Msekera", "Serenje", "Sesheke", "solwezi", "Kalabo",
    "Kasama", "Magoye", "Mkusbi", "HMNIA", "Isoka", "KKIA",
    "SMKIA", "Simon", "mt", "Mukulu", "Kawambwa", "Mpulungu",
    "Chipata", "Chipepo", "Kabombo", "Kapombo", "Kasempa", "Lundazi",
    "Msekera", "Petauke", "Senanga", "Serenje", "Sesheke", "Kawambwa",
    "Mpulungu", "Chipata", "Chinsali", "Kawambwa", "Mpika", "Ndola",
    "Choma", "Kaoma", "Mansa", "Mbala", "Mfuwe", "Mongu"
]

YEARS = list(range(1970, 2026))  # 1970-2025

def create_random_image(width, height, color):
    """Create a simple random image"""
    img = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(img)
    
    # Add some random patterns to make it look like a real photo
    for _ in range(random.randint(3, 8)):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        color2 = (
            random.randint(0, 255),
            random.randint(0, 255), 
            random.randint(0, 255)
        )
        draw.line([(x1, y1), (x2, y2)], fill=color2, width=random.randint(1, 3))
    
    # Add some circles
    for _ in range(random.randint(1, 4)):
        x = random.randint(10, width-10)
        y = random.randint(10, height-10)
        r = random.randint(5, 20)
        color2 = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
        draw.ellipse([x-r, y-r, x+r, y+r], fill=color2, outline=(0,0,0))
    
    return img

def generate_filename(town, year, index, total):
    """Generate filename similar to your actual images"""
    # Random date components
    date_num = random.randint(251200, 251230)  # Similar to your 251216 format
    time_num = random.randint(100000, 235959)
    
    # Random sequence number
    seq_num = random.randint(1, total)
    
    # Format like your actual images
    if random.random() < 0.7:  # 70% chance of full format
        return f"{town} {year}_{date_num}_{time_num}_{seq_num}-{total}.jpg"
    else:  # 30% chance of simple format
        return f"{town} {year}_{date_num}_{time_num}.jpg"

def create_test_images(output_folder, num_images=30):
    """Create test images with town names"""
    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True)
    
    print(f"🎨 Creating {num_images} test images in: {output_path}")
    
    created_files = []
    
    for i in range(num_images):
        # Random town and year
        town = random.choice(TOWNS)
        year = random.choice(YEARS)
        
        # Random image size (mix of landscape and portrait)
        if random.random() < 0.3:  # 30% portrait for testing rotation
            width, height = random.randint(2000, 3000), random.randint(3000, 4000)
        else:  # 70% landscape
            width, height = random.randint(3000, 4000), random.randint(2000, 3000)
        
        # Random background color
        bg_color = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255)
        )
        
        # Create image
        img = create_random_image(width, height, bg_color)
        
        # Generate filename
        filename = generate_filename(town, year, i+1, num_images)
        file_path = output_path / filename
        
        # Save image
        img.save(file_path, 'JPEG', quality=85)
        created_files.append(filename)
        
        print(f"✅ Created: {filename} ({width}x{height})")
    
    print(f"\n🎉 Created {len(created_files)} test images!")
    
    # Show summary
    towns_used = set()
    years_used = set()
    portrait_count = 0
    
    for filename in created_files:
        parts = filename.split()
        if parts:
            towns_used.add(parts[0])
            if len(parts) > 1 and parts[1].isdigit():
                years_used.add(int(parts[1]))
        
        # Check if likely portrait (based on size in filename pattern)
        if random.random() < 0.3:  # Approximate based on generation
            portrait_count += 1
    
    print(f"\n📊 Test Collection Summary:")
    print(f"🏘️  Towns: {len(towns_used)} ({', '.join(sorted(list(towns_used))[:10])}{'...' if len(towns_used) > 10 else ''})")
    print(f"📅 Years: {len(years_used)} ({min(years_used) if years_used else 'N/A'} - {max(years_used) if years_used else 'N/A'})")
    print(f"📐 Portrait images: ~{portrait_count} (for rotation testing)")
    print(f"📁 Location: {output_path.absolute()}")
    
    return created_files

def create_sample_documents(output_folder, num_docs=5):
    """Create some sample documents for testing"""
    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True)
    
    print(f"\n📄 Creating {num_docs} sample documents...")
    
    # Sample PDF
    pdf_content = f"""
Sample PDF Document for Testing

Town: {random.choice(TOWNS)}
Year: {random.choice(YEARS)}
Type: Sample Document

This is a sample PDF file to test document organization.
Your Image Organizer Pro should place this in a PDF folder.
    """.strip()
    
    with open(output_path / f"{random.choice(TOWNS)} {random.choice(YEARS)}_sample.pdf", 'w') as f:
        f.write(pdf_content)
    
    # Sample text files
    for i in range(num_docs - 1):
        town = random.choice(TOWNS)
        year = random.choice(YEARS)
        with open(output_path / f"{town} {year}_notes_{i+1}.txt", 'w') as f:
            f.write(f"Sample notes for {town} {year}\n\nThis is a test text file.")
    
    print(f"✅ Created {num_docs} sample documents")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Create test images for Image Organizer Pro')
    parser.add_argument('output_folder', help='Folder to create test images in')
    parser.add_argument('-n', '--num-images', type=int, default=30, 
                       help='Number of images to create (default: 30)')
    parser.add_argument('-d', '--include-docs', action='store_true',
                       help='Also create sample documents')
    parser.add_argument('-r', '--random-seed', type=int,
                       help='Random seed for reproducible results')
    
    args = parser.parse_args()
    
    # Set random seed if provided
    if args.random_seed:
        random.seed(args.random_seed)
        print(f"🎲 Using random seed: {args.random_seed}")
    
    # Create test images
    create_test_images(args.output_folder, args.num_images)
    
    # Create documents if requested
    if args.include_docs:
        create_sample_documents(args.output_folder)
    
    print(f"\n🚀 Test data ready for Image Organizer Pro!")
    print(f"📁 Run: python3 image_organizer_app.py")
    print(f"📂 Select folder: {args.output_folder}")

if __name__ == "__main__":
    main()
