"""
Generate composite animated Developer Arcade showcase GIF for GitHub README.
Cycles through all 5 games with Titanium Hacker branding and metadata overlays.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageSequence

GAMES_CONFIG = [
    {
        "id": "packet-breaker",
        "num": "01",
        "name": "PACKET BREAKER",
        "category": "BRICK BREAKER // ARCADE PHYSICS",
        "gif": "docs/games/assets/previews/packet-breaker.gif"
    },
    {
        "id": "circuit-pinball",
        "num": "02",
        "name": "CIRCUIT PINBALL",
        "category": "PINBALL // REACTIVE CIRCUITS",
        "gif": "docs/games/assets/previews/circuit-pinball.gif"
    },
    {
        "id": "runtime-rush",
        "num": "03",
        "name": "RUNTIME RUSH",
        "category": "3D RUNNER // WEBGL ENGINE",
        "gif": "docs/games/assets/previews/runtime-rush.gif"
    },
    {
        "id": "firewall-defense",
        "num": "04",
        "name": "FIREWALL DEFENSE",
        "category": "TOWER DEFENSE // NETWORK TACTICS",
        "gif": "docs/games/assets/previews/firewall-defense.gif"
    },
    {
        "id": "stack-overflow",
        "num": "05",
        "name": "STACK OVERFLOW",
        "category": "PRECISION PHYSICS // TOWER PROTOCOL",
        "gif": "docs/games/assets/previews/stack-overflow.gif"
    }
]

WIDTH = 960
HEIGHT = 520

# Colors
C_BG = (7, 11, 12)
C_SURFACE = (12, 15, 16)
C_CARD = (20, 28, 33)
C_BORDER = (37, 49, 57)
C_ACCENT = (182, 255, 59)
C_TEXT = (238, 247, 239)
C_MUTED = (142, 173, 182)
C_DIM = (84, 107, 117)

def load_fonts():
    try:
        f_orbitron_bold = ImageFont.truetype('design/fonts/orbitron/Orbitron-Bold.ttf', 16)
        f_orbitron_title = ImageFont.truetype('design/fonts/orbitron/Orbitron-Black.ttf', 20)
    except Exception:
        f_orbitron_bold = ImageFont.load_default()
        f_orbitron_title = ImageFont.load_default()

    try:
        f_mono_bold = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 15)
        f_mono_sm = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 13)
    except Exception:
        f_mono_bold = ImageFont.load_default()
        f_mono_sm = ImageFont.load_default()

    return f_orbitron_title, f_orbitron_bold, f_mono_bold, f_mono_sm

def extract_frames(gif_path, max_frames=12):
    im = Image.open(gif_path)
    total_frames = im.n_frames
    step = max(1, total_frames // max_frames)
    frames = []
    
    for i in range(0, total_frames, step):
        im.seek(i)
        frame = im.convert('RGB')
        frames.append(frame)
        if len(frames) >= max_frames:
            break
    return frames

def build_showcase():
    f_orbitron_title, f_orbitron_bold, f_mono_bold, f_mono_sm = load_fonts()
    output_frames = []

    # Inner viewport dimensions
    vp_x = 24
    vp_y = 68
    vp_w = WIDTH - 48
    vp_h = HEIGHT - 128

    for g_idx, game in enumerate(GAMES_CONFIG):
        frames = extract_frames(game["gif"], max_frames=10)
        
        for f_idx, src_frame in enumerate(frames):
            canvas = Image.new('RGB', (WIDTH, HEIGHT), C_BG)
            draw = ImageDraw.Draw(canvas)

            # Outer rounded border
            draw.rounded_rectangle([6, 6, WIDTH - 6, HEIGHT - 6], radius=10, fill=C_SURFACE, outline=C_BORDER, width=1)
            
            # Corner accents
            draw.line([(6, 18), (6, 6), (18, 6)], fill=C_ACCENT, width=2)
            draw.line([(WIDTH - 18, 6), (WIDTH - 6, 6), (WIDTH - 6, 18)], fill=C_ACCENT, width=2)
            draw.line([(6, HEIGHT - 18), (6, HEIGHT - 6), (18, HEIGHT - 6)], fill=C_ACCENT, width=2)
            draw.line([(WIDTH - 18, HEIGHT - 6), (WIDTH - 6, HEIGHT - 6), (WIDTH - 6, HEIGHT - 18)], fill=C_ACCENT, width=2)

            # Header bar
            draw.text((24, 22), "naresh@github:~$", font=f_mono_bold, fill=C_ACCENT)
            draw.text((160, 22), "play --developer-arcade", font=f_mono_bold, fill=C_TEXT)
            
            status_text = "● SYSTEM ONLINE // 05 MODULES"
            draw.text((WIDTH - 280, 22), status_text, font=f_mono_bold, fill=C_MUTED)

            # Viewport border
            draw.rounded_rectangle([vp_x, vp_y, vp_x + vp_w, vp_y + vp_h], radius=6, fill=(0, 0, 0), outline=C_BORDER, width=1)

            # Resize & center source game frame into viewport
            src_w, src_h = src_frame.size
            ratio = min(vp_w / src_w, vp_h / src_h)
            new_w = int(src_w * ratio)
            new_h = int(src_h * ratio)
            resized = src_frame.resize((new_w, new_h), Image.Resampling.LANCZOS)

            offset_x = vp_x + (vp_w - new_w) // 2
            offset_y = vp_y + (vp_h - new_h) // 2
            canvas.paste(resized, (offset_x, offset_y))

            # Scanline pattern over viewport
            for y_sl in range(vp_y, vp_y + vp_h, 4):
                draw.line([(vp_x, y_sl), (vp_x + vp_w, y_sl)], fill=(0, 0, 0), width=1)

            # Overlay Badge on Viewport Top Left
            badge_x = vp_x + 14
            badge_y = vp_y + 14
            badge_w = 420
            badge_h = 32
            draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=4, fill=(12, 15, 16), outline=C_BORDER, width=1)
            draw.text((badge_x + 10, badge_y + 7), f"[{game['num']}/05]", font=f_orbitron_bold, fill=C_ACCENT)
            draw.text((badge_x + 85, badge_y + 7), game["name"], font=f_orbitron_bold, fill=C_TEXT)
            draw.text((badge_x + 230, badge_y + 9), f"// {game['category'].split('//')[0].strip()}", font=f_mono_sm, fill=C_MUTED)

            # Bottom Bar
            bot_y = HEIGHT - 46
            draw.line([(24, bot_y - 8), (WIDTH - 24, bot_y - 8)], fill=C_BORDER, width=1)
            
            # Module dots
            dot_start_x = 26
            for dot_idx in range(5):
                color = C_ACCENT if dot_idx == g_idx else C_BORDER
                draw.rectangle([dot_start_x + dot_idx * 16, bot_y + 4, dot_start_x + dot_idx * 16 + 8, bot_y + 12], fill=color)

            draw.text((dot_start_x + 95, bot_y + 2), f"MODULE {game['num']}: {game['name']} ACTIVE", font=f_mono_sm, fill=C_TEXT)

            cta_text = "CLICK TO LAUNCH DEVELOPER ARCADE ON GITHUB PAGES ↗"
            draw.text((WIDTH - 430, bot_y + 2), cta_text, font=f_mono_bold, fill=C_ACCENT)

            output_frames.append(canvas.convert('P', palette=Image.Palette.ADAPTIVE, colors=128))

    os.makedirs('assets/playground', exist_ok=True)
    out_path = 'assets/playground/arcade-showcase.gif'
    output_frames[0].save(
        out_path,
        save_all=True,
        append_images=output_frames[1:],
        duration=110,
        loop=0,
        optimize=True
    )
    print(f"Showcase generated: {out_path} ({os.path.getsize(out_path) / 1024 / 1024:.2f} MB, {len(output_frames)} frames)")

if __name__ == '__main__':
    build_showcase()

