"""
Generate animated bot avatar GIF
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import os

# Settings
SIZE = 512
CENTER = SIZE // 2
FRAMES = 30
DURATION = 100  # ms per frame

def create_frame(frame_num, total_frames):
    """Create a single frame of the animation"""
    # Create image with transparency
    img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Animation progress (0 to 1)
    progress = frame_num / total_frames
    pulse = (math.sin(progress * 2 * math.pi) + 1) / 2  # 0 to 1 pulse
    
    # Background circle with gradient effect
    for i in range(256, 0, -2):
        alpha = int(255 * (i / 256))
        r = int(102 + (118 - 102) * (i / 256))
        g = int(126 + (75 - 126) * (i / 256))
        b = int(234 + (162 - 234) * (i / 256))
        radius = int((SIZE // 2 - 10) * (i / 256))
        draw.ellipse([
            CENTER - radius, CENTER - radius,
            CENTER + radius, CENTER + radius
        ], fill=(r, g, b, alpha))
    
    # Inner dark circle
    inner_radius = int(SIZE * 0.38)
    draw.ellipse([
        CENTER - inner_radius, CENTER - inner_radius,
        CENTER + inner_radius, CENTER + inner_radius
    ], fill=(26, 26, 46, 255))
    
    # Glow effect based on pulse
    glow_intensity = int(30 + 20 * pulse)
    for i in range(glow_intensity, 0, -1):
        alpha = int(100 * (i / glow_intensity) * pulse)
        glow_r = inner_radius + i * 2
        draw.ellipse([
            CENTER - glow_r, CENTER - glow_r,
            CENTER + glow_r, CENTER + glow_r
        ], outline=(0, 212, 255, alpha), width=1)
    
    # Eyes
    eye_size = 35
    eye_radius = 10
    eye_y = CENTER - 30
    eye_spacing = 45
    
    # Eye glow
    glow_size = int(eye_size + 10 + 5 * pulse)
    for eye_x in [CENTER - eye_spacing, CENTER + eye_spacing]:
        # Glow
        for i in range(15, 0, -1):
            alpha = int(150 * (i / 15) * (0.7 + 0.3 * pulse))
            draw.rounded_rectangle([
                eye_x - eye_size - i, eye_y - eye_size - i,
                eye_x + eye_size + i, eye_y + eye_size + i
            ], radius=eye_radius + i, fill=(0, 212, 255, alpha))
        
        # Eye base
        draw.rounded_rectangle([
            eye_x - eye_size, eye_y - eye_size,
            eye_x + eye_size, eye_y + eye_size
        ], radius=eye_radius, fill=(0, 212, 255, 255))
        
        # Eye highlight
        highlight_offset = 8
        draw.ellipse([
            eye_x - eye_size + highlight_offset, eye_y - eye_size + highlight_offset,
            eye_x - eye_size + highlight_offset + 15, eye_y - eye_size + highlight_offset + 15
        ], fill=(255, 255, 255, 200))
    
    # Mouth
    mouth_width = 60
    mouth_height = 4
    mouth_y = CENTER + 40
    
    # Mouth glow
    for i in range(10, 0, -1):
        alpha = int(100 * (i / 10))
        draw.rounded_rectangle([
            CENTER - mouth_width - i, mouth_y - mouth_height - i,
            CENTER + mouth_width + i, mouth_y + mouth_height + i
        ], radius=mouth_height + i, fill=(0, 212, 255, alpha))
    
    draw.rounded_rectangle([
        CENTER - mouth_width, mouth_y - mouth_height,
        CENTER + mouth_width, mouth_y + mouth_height
    ], radius=mouth_height, fill=(0, 212, 255, 255))
    
    # Antenna
    antenna_x = CENTER
    antenna_top = CENTER - inner_radius - 20
    antenna_bottom = CENTER - inner_radius + 30
    
    # Antenna line
    draw.line([antenna_x, antenna_bottom, antenna_x, antenna_top], 
              fill=(102, 126, 234, 255), width=6)
    
    # Antenna ball with pulse
    ball_size = int(10 + 4 * pulse)
    for i in range(15, 0, -1):
        alpha = int(150 * (i / 15) * pulse)
        draw.ellipse([
            antenna_x - ball_size - i, antenna_top - ball_size - i,
            antenna_x + ball_size + i, antenna_top + ball_size + i
        ], fill=(0, 212, 255, alpha))
    
    draw.ellipse([
        antenna_x - ball_size, antenna_top - ball_size,
        antenna_x + ball_size, antenna_top + ball_size
    ], fill=(0, 212, 255, 255))
    
    # Floating particles
    for i in range(5):
        angle = (progress * 2 * math.pi) + (i * 2 * math.pi / 5)
        particle_distance = inner_radius * 0.7
        particle_x = CENTER + int(particle_distance * math.cos(angle))
        particle_y = CENTER + int(particle_distance * math.sin(angle))
        particle_size = int(3 + 2 * math.sin(progress * 4 * math.pi + i))
        particle_alpha = int(150 + 100 * math.sin(progress * 4 * math.pi + i))
        
        draw.ellipse([
            particle_x - particle_size, particle_y - particle_size,
            particle_x + particle_size, particle_y + particle_size
        ], fill=(0, 212, 255, particle_alpha))
    
    # AI text
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 50)
    except:
        font = ImageFont.load_default()
    
    text = "AI"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = CENTER - text_width // 2
    text_y = CENTER + 70
    
    # Text glow
    for i in range(10, 0, -1):
        alpha = int(80 * (i / 10))
        draw.text((text_x, text_y), text, font=font, fill=(0, 212, 255, alpha))
    
    # Gradient text effect
    draw.text((text_x, text_y), text, font=font, fill=(0, 212, 255, 255))
    
    return img

def main():
    print("🎨 در حال ساخت GIF متحرک...")
    
    frames = []
    for i in range(FRAMES):
        print(f"   فریم {i+1}/{FRAMES}")
        frame = create_frame(i, FRAMES)
        frames.append(frame)
    
    # Save as GIF
    output_path = "/Users/omid/Downloads/Omid_Shojaei/bot python/bot_avatar.gif"
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=DURATION,
        loop=0,
        optimize=True
    )
    
    print(f"\n✅ GIF ذخیره شد:")
    print(f"   📁 {output_path}")
    print(f"   📐 سایز: {SIZE}x{SIZE} پیکسل")
    print(f"   🎞️ فریم‌ها: {FRAMES}")
    
if __name__ == "__main__":
    main()

