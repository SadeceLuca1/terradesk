"""
TerraDesk - Logo Generator
Creates logo.png, logo256.png and icon.ico procedurally using Pillow.
Run: python scripts/make_logo.py
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow", "-q"])
    from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(len(c1)))

def make_logo(w=512, h=512):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = w // 2, h // 2

    # Background circle - sky gradient
    for r in range(min(cx, cy), 0, -1):
        t = 1 - r / min(cx, cy)
        col = lerp_color((30, 80, 160), (90, 170, 240), t)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (255,))

    # Ground diamond
    tile_w, tile_h = int(w * 0.72), int(h * 0.36)
    gx, gy = cx, int(cy * 1.05)
    ground_pts = [
        (gx,               gy - tile_h // 2),
        (gx + tile_w // 2, gy),
        (gx,               gy + tile_h // 2),
        (gx - tile_w // 2, gy),
    ]
    d.polygon(ground_pts, fill=(90, 165, 60, 255))
    side_h = int(h * 0.09)
    d.polygon([
        (gx - tile_w // 2, gy),
        (gx,               gy + tile_h // 2),
        (gx,               gy + tile_h // 2 + side_h),
        (gx - tile_w // 2, gy + side_h),
    ], fill=(55, 115, 35, 255))
    d.polygon([
        (gx,               gy + tile_h // 2),
        (gx + tile_w // 2, gy),
        (gx + tile_w // 2, gy + side_h),
        (gx,               gy + tile_h // 2 + side_h),
    ], fill=(40, 90, 25, 255))

    # House
    hx, hy = cx, int(cy * 0.82)
    hw2, hh2 = int(w * 0.17), int(h * 0.17)
    wall_h = int(h * 0.22)
    # Left wall
    d.polygon([
        (hx - hw2, hy), (hx, hy + hh2),
        (hx, hy + hh2 + wall_h), (hx - hw2, hy + wall_h),
    ], fill=(210, 190, 155, 255))
    # Right wall
    d.polygon([
        (hx, hy + hh2), (hx + hw2, hy),
        (hx + hw2, hy + wall_h), (hx, hy + hh2 + wall_h),
    ], fill=(170, 148, 110, 255))
    # Roof top
    d.polygon([
        (hx,       hy - hh2 - wall_h),
        (hx + hw2, hy - wall_h),
        (hx,       hy + hh2 - wall_h),
        (hx - hw2, hy - wall_h),
    ], fill=(190, 60, 50, 255))
    # Roof front face
    d.polygon([
        (hx - hw2, hy - wall_h),
        (hx,       hy - hh2 - wall_h),
        (hx,       hy + hh2 - wall_h),
        (hx - hw2, hy + wall_h),
    ], fill=(145, 40, 32, 255))
    # Chimney
    chx = hx + int(hw2 * 0.2)
    chy = hy - hh2 - wall_h - int(h * 0.09)
    d.rectangle([chx, chy, chx + int(w*0.04), chy + int(h*0.09)], fill=(80, 80, 90, 255))
    # Glowing window
    wx = hx - hw2 + int(hw2 * 0.4)
    wy = hy + int(wall_h * 0.3)
    ww, wh = int(w * 0.06), int(h * 0.07)
    d.rectangle([wx, wy, wx + ww, wy + wh], fill=(255, 230, 100, 255))
    d.rectangle([wx, wy, wx + ww, wy + wh], outline=(180, 130, 50, 255), width=2)

    # Small tree
    tx, ty = int(cx + tile_w * 0.28), int(cy * 1.0)
    trunk_h = int(h * 0.09)
    trunk_w = int(w * 0.025)
    d.rectangle([tx - trunk_w//2, ty - trunk_h, tx + trunk_w//2, ty], fill=(100, 70, 40, 255))
    for i in range(3):
        cr = int(w * (0.07 - i * 0.012))
        d.ellipse([tx - cr, ty - trunk_h - cr + i*4, tx + cr, ty - trunk_h + cr + i*4],
                  fill=(55 + i*8, 155 + i*5, 50, 255))

    # Text
    font_size = int(h * 0.09)
    font = None
    for fname in ["arialbd.ttf", "Arial Bold.ttf", "calibrib.ttf", "verdanab.ttf"]:
        try:
            font = ImageFont.truetype(fname, font_size)
            break
        except Exception:
            pass
    if font is None:
        font = ImageFont.load_default()

    text = "TerraDesk"
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    tx2 = cx - tw // 2
    ty2 = int(h * 0.83)
    d.text((tx2 + 2, ty2 + 2), text, font=font, fill=(0, 0, 0, 160))
    d.text((tx2, ty2), text, font=font, fill=(255, 255, 255, 255))

    return img


if __name__ == "__main__":
    out_dir = ROOT

    logo = make_logo(512, 512)
    logo_path = os.path.join(out_dir, "logo.png")
    logo.save(logo_path, "PNG")
    print("logo.png     OK  ({} KB)".format(os.path.getsize(logo_path)//1024))

    logo256 = logo.resize((256, 256), Image.LANCZOS)
    p256 = os.path.join(out_dir, "logo256.png")
    logo256.save(p256, "PNG")
    print("logo256.png  OK  ({} KB)".format(os.path.getsize(p256)//1024))

    # Build multi-size .ico
    sizes = [16, 24, 32, 48, 64, 128, 256]
    frames = [logo.resize((s, s), Image.LANCZOS) for s in sizes]
    ico_path = os.path.join(out_dir, "icon.ico")
    frames[0].save(ico_path, format="ICO",
                   sizes=[(s, s) for s in sizes],
                   append_images=frames[1:])
    print("icon.ico     OK  ({} KB)".format(os.path.getsize(ico_path)//1024))
    print("\nAll done!")
