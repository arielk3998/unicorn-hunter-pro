"""
Generate a custom app icon for Resume Toolkit
Uses PIL (Pillow) to create a modern, gradient icon
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_app_icon():
    """Create a modern gradient icon with 'RT' text"""
    
    # Create assets directory
    assets_dir = Path(__file__).parent / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Icon sizes for .ico file
    sizes = [256, 128, 64, 48, 32, 16]
    images = []
    
    for size in sizes:
        # Create image with gradient background
        img = Image.new('RGB', (size, size), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw gradient background (blue to purple)
        for y in range(size):
            # Gradient from #4F46E5 (indigo) to #7C3AED (purple)
            r = int(79 + (124 - 79) * (y / size))
            g = int(70 + (58 - 70) * (y / size))
            b = int(229 + (237 - 229) * (y / size))
            draw.rectangle([(0, y), (size, y+1)], fill=(r, g, b))
        
        # Draw rounded rectangle overlay
        margin = int(size * 0.1)
        corner_radius = int(size * 0.15)
        
        # Create a mask for rounded corners
        mask = Image.new('L', (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle(
            [(margin, margin), (size - margin, size - margin)],
            radius=corner_radius,
            fill=255
        )
        
        # Apply mask
        overlay = Image.new('RGBA', (size, size), (79, 70, 229, 255))
        img = img.convert('RGBA')
        img.paste(overlay, mask=mask)
        
        # Add "RT" text
        try:
            # Try to use a nice font
            font_size = int(size * 0.45)
            font = ImageFont.truetype("segoeui.ttf", font_size)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        text = "RT"
        
        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center text
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - int(size * 0.05)
        
        # Draw text shadow
        shadow_offset = max(1, int(size * 0.02))
        draw.text((x + shadow_offset, y + shadow_offset), text, 
                 fill=(0, 0, 0, 128), font=font)
        
        # Draw main text
        draw.text((x, y), text, fill='white', font=font)
        
        images.append(img)
    
    # Save as .ico file
    icon_path = assets_dir / "app_icon.ico"
    images[0].save(icon_path, format='ICO', sizes=[(img.width, img.height) for img in images])
    
    # Also save PNG for reference
    png_path = assets_dir / "app_icon.png"
    images[0].save(png_path, format='PNG')
    
    print(f"✅ Icon created: {icon_path}")
    print(f"📸 PNG preview: {png_path}")
    
    return icon_path

if __name__ == "__main__":
    create_app_icon()
