"""
video_gen.py - Generates animated educational videos using MoviePy + Pillow.

Subject-aware logic:
  - STEM (Math/Science): Displays formulas and key concepts with glowing text on dark background.
  - General: Creates smooth slide-based animations with key points and gradient backgrounds.
"""
import os
import uuid
import textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont

VIDEO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "video")

# ─────────────────── Helper: Frame generators ───────────────────

def _hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def _create_gradient_frame(width: int, height: int, color1: tuple, color2: tuple) -> np.ndarray:
    """Create a vertical gradient background frame as numpy array (H, W, 3) uint8."""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        t = y / height
        r = int(color1[0] * (1 - t) + color2[0] * t)
        g = int(color1[1] * (1 - t) + color2[1] * t)
        b = int(color1[2] * (1 - t) + color2[2] * t)
        frame[y, :] = [r, g, b]
    return frame


def _get_font(size: int):
    """Try to load a nice font, fall back to PIL default."""
    font_paths = [
        "C:/Windows/Fonts/calibrib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _get_font_regular(size: int):
    font_paths = [
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _pil_image_to_numpy(img: Image.Image) -> np.ndarray:
    return np.array(img.convert("RGB"))


def _draw_slide(
    width: int, height: int,
    title: str, body_lines: list,
    bg_color1: tuple, bg_color2: tuple,
    accent_color: tuple,
    slide_number: int, total_slides: int,
    alpha: float = 1.0
) -> np.ndarray:
    """Draw a complete slide frame as numpy array."""
    # Gradient background
    base = _create_gradient_frame(width, height, bg_color1, bg_color2)
    img = Image.fromarray(base, "RGB")
    draw = ImageDraw.Draw(img, "RGBA")

    # Decorative top bar
    bar_h = 6
    draw.rectangle([0, 0, width, bar_h], fill=(*accent_color, 255))

    # Subtle grid lines for STEM feel
    grid_color = (*accent_color, 15)
    for x in range(0, width, 60):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    for y in range(0, height, 60):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)

    # Logo / branding dot
    draw.ellipse([30, 25, 56, 51], fill=(*accent_color, 200))

    # Slide counter
    counter_font = _get_font(18)
    slide_text = f"{slide_number} / {total_slides}"
    draw.text((width - 70, 20), slide_text, font=counter_font, fill=(180, 180, 180, 200))

    # Title
    title_font = _get_font(48)
    wrapped_title = textwrap.fill(title, width=36)
    draw.text((60, 80), wrapped_title, font=title_font, fill=(255, 255, 255, 255))

    # Accent underline
    title_lines = wrapped_title.count("\n") + 1
    underline_y = 80 + title_lines * 58 + 8
    draw.rectangle([60, underline_y, 60 + 80, underline_y + 4], fill=(*accent_color, 255))

    # Body text
    body_font = _get_font_regular(30)
    y_pos = underline_y + 36
    for line in body_lines:
        # Bullet point
        draw.ellipse([62, y_pos + 10, 74, y_pos + 22], fill=(*accent_color, 220))
        wrapped = textwrap.fill(line, width=62)
        draw.text((90, y_pos), wrapped, font=body_font, fill=(220, 220, 240, 255))
        line_count = wrapped.count("\n") + 1
        y_pos += 42 * line_count + 10
        if y_pos > height - 80:
            break

    # Apply alpha (fade in/out)
    if alpha < 1.0:
        overlay = Image.new("RGBA", img.size, (0, 0, 0, int((1 - alpha) * 255)))
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay)
        img = img.convert("RGB")

    return _pil_image_to_numpy(img)


# ─────────────────── Main entry points ───────────────────

def generate_video(
    key_concepts: list,
    subject_tags: list,
    summary: str,
    filename: str = None,
    is_stem: bool = False,
    audio_path: str = None
) -> str:
    """
    Generate an animated educational MP4 video with audio.

    Args:
        key_concepts: List of {term, definition} dicts (5 items)
        subject_tags: List of subject tag strings
        summary: The document summary text
        filename: Output filename (without extension).
        is_stem: Whether this is a STEM document
        audio_path: Path to the absolute audio file

    Returns:
        Relative path like 'video/xyz.mp4'
    """
    from moviepy.editor import ImageSequenceClip, AudioFileClip

    os.makedirs(VIDEO_DIR, exist_ok=True)
    if not filename:
        filename = f"video_{uuid.uuid4().hex[:8]}"
    output_path = os.path.join(VIDEO_DIR, f"{filename}.mp4")

    W, H = 1280, 720
    FPS = 24
    
    # Calculate durations based on audio if available
    if audio_path and os.path.exists(audio_path):
        audio_clip = AudioFileClip(audio_path)
        total_audio_duration = audio_clip.duration
        num_slides = len(key_concepts) + 2
        # Distribute time across slides
        slide_duration = total_audio_duration / num_slides
        FADE_DURATION = 1.0
        HOLD_DURATION = max(0.5, slide_duration - (FADE_DURATION * 2))
    else:
        num_slides = len(key_concepts) + 2
        FADE_DURATION = 1.0
        HOLD_DURATION = 3.5
        audio_clip = None

    FADE_FRAMES = int(FADE_DURATION * FPS)
    HOLD_FRAMES = int(HOLD_DURATION * FPS)

    # Color schemes
    if is_stem:
        BG1 = (10, 15, 40); BG2 = (5, 30, 55); ACCENT = (0, 210, 180)
    else:
        BG1 = (25, 10, 55); BG2 = (40, 5, 70); ACCENT = (185, 14, 102)

    frames = []

    # ── Slide 0: Title slide ──
    tags_str = " · ".join(subject_tags[:4]) if subject_tags else "Knowledge"
    title_slide_lines = [f"Subject: {tags_str}", "Powered by Gemini AI"]
    for i in range(FADE_FRAMES + HOLD_FRAMES + FADE_FRAMES):
        if i < FADE_FRAMES: alpha = i / FADE_FRAMES
        elif i < FADE_FRAMES + HOLD_FRAMES: alpha = 1.0
        else: alpha = 1.0 - (i - FADE_FRAMES - HOLD_FRAMES) / FADE_FRAMES
        frames.append(_draw_slide(W, H, "AI Knowledge Helper", title_slide_lines, BG1, BG2, ACCENT, 1, num_slides, alpha))

    # ── Slides 1-5: Key concepts ──
    for idx, concept in enumerate(key_concepts[:5]):
        term = concept.get("term", f"Concept {idx + 1}")
        def_lines = textwrap.wrap(concept.get("definition", ""), width=65)[:4]
        for i in range(FADE_FRAMES + HOLD_FRAMES + FADE_FRAMES):
            if i < FADE_FRAMES: alpha = i / FADE_FRAMES
            elif i < FADE_FRAMES + HOLD_FRAMES: alpha = 1.0
            else: alpha = 1.0 - (i - FADE_FRAMES - HOLD_FRAMES) / FADE_FRAMES
            frames.append(_draw_slide(W, H, f"Key Concept: {term}", def_lines, BG1, BG2, ACCENT, idx + 2, num_slides, alpha))

    # ── Final slide: Summary ──
    summary_lines = textwrap.wrap(summary[:300], width=65)[:5]
    for i in range(FADE_FRAMES + HOLD_FRAMES + FADE_FRAMES):
        if i < FADE_FRAMES: alpha = i / FADE_FRAMES
        elif i < FADE_FRAMES + HOLD_FRAMES: alpha = 1.0
        else: alpha = 1.0 - (i - FADE_FRAMES - HOLD_FRAMES) / FADE_FRAMES
        frames.append(_draw_slide(W, H, "Document Summary", summary_lines, BG1, BG2, ACCENT, num_slides, num_slides, alpha))

    # Write video
    clip = ImageSequenceClip(frames, fps=FPS)
    if audio_clip:
        # Ensure video duration matches audio (subclip if video is longer, or just attach)
        clip = clip.set_audio(audio_clip)
        if clip.duration > audio_clip.duration:
            clip = clip.subclip(0, audio_clip.duration)
        
    clip.write_videofile(
        output_path,
        codec="libx264",
        audio=True if audio_clip else False,
        audio_codec="aac" if audio_clip else None,
        logger=None,
        ffmpeg_params=["-crf", "28", "-preset", "fast"]
    )
    
    if audio_clip:
        audio_clip.close()
    clip.close()

    return f"video/{filename}.mp4"
