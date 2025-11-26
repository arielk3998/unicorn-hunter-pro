"""
Create a unicorn icon for The Unicorn Hunter
Downloads unicorn emoji and converts to ICO format
"""
from PIL import Image, ImageDraw, ImageFont
import requests
from pathlib import Path
import io

def create_unicorn_icon():
    """Create unicorn.ico from OpenMoji or fallback to emoji rendering"""
    assets_dir = Path(__file__).parent.parent / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    icon_path = assets_dir / "unicorn.ico"
    
    # Try to download OpenMoji unicorn
    try:
        print("Downloading unicorn from OpenMoji...")
        url = "https://raw.githubusercontent.com/hfg-gmuend/openmoji/master/color/618x618/1F984.png"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Load image
        img = Image.open(io.BytesIO(response.content))
        
    except Exception as e:
        print(f"Could not download OpenMoji: {e}")
        print("Creating fallback unicorn icon...")
        
        # Create a simple unicorn icon with gradient background
        img = Image.new('RGBA', (256, 256), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw gradient background
        for i in range(256):
            color = (
                int(233 + (255 - 233) * i / 256),  # Red gradient
                int(69 + (105 - 69) * i / 256),    # Green gradient  
                int(96 + (180 - 96) * i / 256),    # Blue gradient
                255
            )
            draw.rectangle([0, i, 256, i+1], fill=color)
        
        # Draw unicorn emoji using system font
        try:
            # Try to use a large emoji font
            font_size = 180
            try:
                font = ImageFont.truetype("seguiemj.ttf", font_size)  # Windows emoji font
            except:
                try:
                    font = ImageFont.truetype("AppleColorEmoji.ttf", font_size)  # macOS
                except:
                    font = ImageFont.load_default()
            
            # Draw the unicorn emoji centered
            unicorn = "🦄"
            bbox = draw.textbbox((0, 0), unicorn, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (256 - text_width) // 2
            y = (256 - text_height) // 2 - 20
            
            draw.text((x, y), unicorn, font=font, embedded_color=True)
            
        except Exception as e:
            print(f"Could not draw emoji: {e}")
            # Draw simple text fallback
            draw.text((50, 100), "UNICORN", fill='white')
            draw.text((50, 130), "HUNTER", fill='white')
    
    # Resize to multiple icon sizes and save as ICO
    print(f"Creating icon with multiple sizes...")
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    icons = []
    
    for size in sizes:
        resized = img.resize(size, Image.Resampling.LANCZOS)
        icons.append(resized)
    
    # Save as ICO with multiple sizes
    icons[0].save(
        icon_path,
        format='ICO',
        sizes=[icon.size for icon in icons],
        append_images=icons[1:]
    )
    
    print(f"✅ Created: {icon_path}")
    print(f"   Icon attribution: Unicorn emoji © OpenMoji – CC BY-SA 4.0")
    
    return icon_path

if __name__ == "__main__":
    create_unicorn_icon()
