"""
Infographic Renderer — vẽ ảnh tiếng Việt sắc nét bằng Pillow.
Layout: header + hero card (trái) + block cards (phải) + footer bar.
"""
import os
import math
import logging
import requests
from datetime import datetime
from config.config import PROJECT_ROOT

logger = logging.getLogger(__name__)

AIIMG_DIR = os.path.join(PROJECT_ROOT, "AIimg")
FONTS_DIR = os.path.join(PROJECT_ROOT, "fonts")

ACCENT_MAP = {
    "terracotta orange": (196, 98,  45),
    "clay blue":         (74,  124, 142),
    "sage green":        (100, 148, 104),
    "dusty purple":      (139, 123, 168),
}
BG       = (250, 247, 240)   # warm beige
CHARCOAL = (42,  38,  35)
WHITE    = (255, 255, 255)
CARD_BG  = (255, 253, 248)
MUTED    = (108, 102, 94)
BORDER   = (212, 206, 196)

_NOTO_URLS = {
    "NotoSans-Regular.ttf": (
        "https://github.com/googlefonts/noto-fonts/raw/main/"
        "hinted/ttf/NotoSans/NotoSans-Regular.ttf"
    ),
    "NotoSans-Bold.ttf": (
        "https://github.com/googlefonts/noto-fonts/raw/main/"
        "hinted/ttf/NotoSans/NotoSans-Bold.ttf"
    ),
}

_SYSTEM_FALLBACKS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/arial.ttf",
]


def _ensure_font(name: str) -> str:
    os.makedirs(FONTS_DIR, exist_ok=True)
    path = os.path.join(FONTS_DIR, name)
    if os.path.exists(path):
        return path
    url = _NOTO_URLS.get(name)
    if url:
        try:
            logger.info(f"⬇️  Downloading font {name}...")
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                with open(path, "wb") as f:
                    f.write(r.content)
                logger.info(f"✅ Font saved: {name}")
                return path
        except Exception as e:
            logger.warning(f"Font download failed ({name}): {e}")
    # fallback to system fonts
    for fp in _SYSTEM_FALLBACKS:
        if os.path.exists(fp):
            return fp
    return None


def _lighten(rgb, f=0.4):
    return tuple(min(255, int(c + (255 - c) * f)) for c in rgb)


def _darken(rgb, f=0.25):
    return tuple(max(0, int(c * (1 - f))) for c in rgb)


def _wrap_text(text, font, max_px, draw):
    """Chia text thành các dòng vừa max_px pixel."""
    words = str(text).split()
    lines, cur = [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        if draw.textlength(test, font=font) <= max_px:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [str(text)]


def render_infographic(
    headline: str,
    blocks: list,
    summary: str = "",
    cta: str = "",
    hashtags: list = None,
    accent_color_name: str = "terracotta orange",
    brand: str = "Genz Yêu Công Nghệ",
) -> str | None:
    """
    Vẽ infographic hoàn chỉnh với text tiếng Việt sắc nét.
    Trả về local file path hoặc None nếu lỗi.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        logger.error("❌ Pillow chưa cài: pip install Pillow")
        return None

    try:
        W, H  = 1200, 900
        PAD   = 44
        accent     = ACCENT_MAP.get(accent_color_name, ACCENT_MAP["terracotta orange"])
        a_light    = _lighten(accent, 0.45)
        a_dark     = _darken(accent, 0.30)

        reg_path  = _ensure_font("NotoSans-Regular.ttf")
        bold_path = _ensure_font("NotoSans-Bold.ttf")

        def _font(path, size):
            try:
                return ImageFont.truetype(path, size) if path else ImageFont.load_default()
            except Exception:
                return ImageFont.load_default()

        f_title  = _font(bold_path, 36)
        f_brand  = _font(reg_path,  15)
        f_num    = _font(bold_path, 20)
        f_btitle = _font(bold_path, 14)
        f_body   = _font(reg_path,  12)
        f_footer = _font(reg_path,  14)

        img  = Image.new("RGB", (W, H), BG)
        draw = ImageDraw.Draw(img)

        # ── HEADER ──────────────────────────────────────────────────────
        y = PAD
        title_lines = _wrap_text(headline or brand, f_title, W - PAD * 2, draw)
        for line in title_lines[:2]:
            draw.text((PAD, y), line, font=f_title, fill=CHARCOAL)
            y += 46

        draw.text((PAD, y), f"⚙  {brand}", font=f_brand, fill=accent)
        y += 26
        draw.rectangle([PAD, y, W - PAD, y + 2], fill=accent)
        y += 14

        header_bottom = y
        footer_top    = H - 60

        # ── HERO CARD (trái 36%) ─────────────────────────────────────────
        hx0 = PAD
        hx1 = int(W * 0.36)
        hy0 = header_bottom
        hy1 = footer_top - 10

        draw.rounded_rectangle([hx0, hy0, hx1, hy1], radius=22, fill=accent)

        cx = (hx0 + hx1) // 2
        cy = (hy0 + hy1) // 2

        # Geometric art
        draw.ellipse([cx - 85, cy - 115, cx + 85, cy + 55], fill=a_dark)
        tri = [(cx, cy - 90), (cx + 70, cy + 55), (cx - 70, cy + 55)]
        draw.polygon(tri, fill=a_light)
        for dx, dy, r, col in [
            (-58, 72, 22, a_light),
            (62,  60, 15, WHITE),
            (-8,  92, 10, a_light),
            (40, -78, 17, a_dark),
            (-52, -55, 12, WHITE),
            (68, -50,  9, a_light),
        ]:
            draw.ellipse([cx+dx-r, cy+dy-r, cx+dx+r, cy+dy+r], fill=col)
        for dx, dy in [(-62, -72), (58, -68)]:
            draw.rounded_rectangle(
                [cx+dx, cy+dy, cx+dx+18, cy+dy+18], radius=5, fill=WHITE
            )

        # Block count badge
        n_label = f"{len(blocks)} nội dung"
        draw.rounded_rectangle([hx0+14, hy1-46, hx0+104, hy1-16], radius=10, fill=a_dark)
        draw.text((hx0 + 59, hy1 - 31), n_label, font=f_brand, fill=WHITE, anchor="mm")

        # ── BLOCK CARDS (phải) ───────────────────────────────────────────
        rx0  = hx1 + 18
        rx1  = W - PAD
        cols = 2
        n    = max(len(blocks), 1)
        rows = math.ceil(n / cols)
        gap  = 10
        main_h = footer_top - header_bottom - 10
        cw   = (rx1 - rx0 - gap) // cols
        ch   = (main_h - gap * (rows - 1)) // rows

        for i, block in enumerate(blocks):
            col = i % cols
            row = i // cols
            bx0 = rx0 + col * (cw + gap)
            by0 = header_bottom + row * (ch + gap)
            bx1 = bx0 + cw
            by1 = by0 + ch

            draw.rounded_rectangle([bx0, by0, bx1, by1],
                                   radius=14, fill=CARD_BG,
                                   outline=BORDER, width=1)

            # Số thứ tự
            bsz = 30
            draw.rounded_rectangle(
                [bx0+10, by0+10, bx0+10+bsz, by0+10+bsz], radius=8, fill=accent
            )
            num_str = str(block.get("number", i + 1))[-2:].zfill(2)
            draw.text(
                (bx0 + 10 + bsz // 2, by0 + 10 + bsz // 2),
                num_str, font=f_num, fill=WHITE, anchor="mm"
            )

            # Icon + tiêu đề
            icon  = block.get("icon", "")
            title = block.get("title", "")
            label = f"{icon} {title}".strip() if icon else title
            tx, tw = bx0 + bsz + 18, bx1 - bx0 - bsz - 26
            ty = by0 + 12
            for tl in _wrap_text(label, f_btitle, tw, draw)[:2]:
                draw.text((tx, ty), tl, font=f_btitle, fill=CHARCOAL)
                ty += 18

            # Bullets
            by = by0 + bsz + 20
            for bullet in block.get("bullets", [])[:3]:
                if by + 15 > by1 - 6:
                    break
                bw = bx1 - bx0 - 20
                for bl in _wrap_text(f"• {bullet}", f_body, bw, draw)[:1]:
                    draw.text((bx0 + 12, by), bl, font=f_body, fill=MUTED)
                    by += 15

            # Metric
            metric = block.get("metric", "")
            if metric and by + 15 < by1 - 4:
                draw.text((bx0 + 12, by), metric[:55], font=f_body, fill=accent)

        # ── FOOTER BAR ──────────────────────────────────────────────────
        fy0 = footer_top
        fy1 = H - PAD + 12
        draw.rounded_rectangle([PAD, fy0, W - PAD, fy1], radius=12, fill=accent)
        footer_text = (summary or cta or "")[:115]
        if footer_text:
            draw.text(
                (PAD + 18, (fy0 + fy1) // 2),
                f"💡  {footer_text}",
                font=f_footer, fill=WHITE, anchor="lm"
            )

        # ── SAVE ────────────────────────────────────────────────────────
        os.makedirs(AIIMG_DIR, exist_ok=True)
        ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(AIIMG_DIR, f"{ts}_infographic.jpg")
        img.save(filepath, "JPEG", quality=95)
        logger.info(f"🖼  Infographic saved: AIimg/{os.path.basename(filepath)}")
        return filepath

    except Exception as e:
        logger.error(f"❌ Renderer error: {e}", exc_info=True)
        return None
