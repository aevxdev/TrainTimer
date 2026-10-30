"""Draws release/TrainTimer-thumbnail.png (1024x1024), same look as the PPES and HideoutBackport thumbnails.

Usage: python -I tools/thumbnail.py
"""
import math
import pathlib

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
S = 4  # supersampling
W = 1024 * S
BG = (17, 17, 17)
ORANGE = (242, 170, 60)
CREAM = (239, 235, 224)
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_SEMI = "C:/Windows/Fonts/seguisb.ttf"


def p(v):
    return v * S


def main():
    img = Image.new("RGB", (W, W), BG)
    d = ImageDraw.Draw(img)

    # clockwise countdown arc with an arrow head, like a timer running down
    cx, cy, r, stroke = p(512), p(400), p(228), p(26)
    gap_start, gap_end = 292, 248  # the arc runs clockwise from gap_start round to gap_end
    d.arc([cx - r, cy - r, cx + r, cy + r], start=gap_start, end=gap_end + 360, fill=ORANGE, width=stroke)
    a = math.radians(gap_start)
    x, y = cx + (r - stroke / 2) * math.cos(a), cy + (r - stroke / 2) * math.sin(a)
    d.ellipse([x - stroke / 2, y - stroke / 2, x + stroke / 2, y + stroke / 2], fill=ORANGE)
    a = math.radians(gap_end)
    tip_base = (cx + (r - stroke / 2) * math.cos(a), cy + (r - stroke / 2) * math.sin(a))
    tangent = (-math.sin(a), math.cos(a))  # direction of travel when going clockwise
    normal = (math.cos(a), math.sin(a))
    head_len, head_half = p(84), p(50)
    tip_base = (tip_base[0] - tangent[0] * p(6), tip_base[1] - tangent[1] * p(6))  # overlap the arc end so no gap shows
    tip = (tip_base[0] + tangent[0] * head_len, tip_base[1] + tangent[1] * head_len)
    left = (tip_base[0] + normal[0] * head_half, tip_base[1] + normal[1] * head_half)
    right = (tip_base[0] - normal[0] * head_half, tip_base[1] - normal[1] * head_half)
    d.polygon([tip, left, right], fill=ORANGE)

    # front of a locomotive on its rails
    line = p(22)
    x0, y0, x1, y1 = p(402), p(282), p(622), p(498)
    d.rounded_rectangle([x0, y0, x1, y1], radius=p(40), outline=CREAM, width=line)
    d.rounded_rectangle([p(442), p(318), p(582), p(392)], radius=p(14), outline=CREAM, width=p(18))
    d.line([p(512), p(318), p(512), p(392)], fill=CREAM, width=p(18))
    for hx in (p(458), p(566)):
        r_light = p(17)
        d.ellipse([hx - r_light, p(444) - r_light, hx + r_light, p(444) + r_light], fill=ORANGE)
    d.line([p(470), p(498), p(442), p(546)], fill=CREAM, width=line)
    d.line([p(554), p(498), p(582), p(546)], fill=CREAM, width=line)
    d.rounded_rectangle([p(400), p(540), p(624), p(560)], radius=p(10), fill=CREAM)

    # title and subtitle are drawn on their own layer and centred by their visible ink, since glyph boxes
    # include side bearings that push text off centre
    def paste_centred(layer, y_top):
        box = layer.getbbox()
        piece = layer.crop(box)
        img.paste(piece, (int(W / 2 - piece.width / 2), int(y_top)), piece)

    def line_layer(parts, spacing):
        probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        width = sum(probe.textlength(ch, font=f) for ch, f, _ in parts) + spacing * (len(parts) - 1)
        layer = Image.new("RGBA", (int(width) + p(40), p(300)), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        x = p(20)
        for ch, font, colour in parts:
            ld.text((x, p(150)), ch, font=font, fill=colour, anchor="lm")
            x += ld.textlength(ch, font=font) + spacing
        return layer

    title_font = ImageFont.truetype(FONT_BOLD, p(170))
    title_layer = line_layer([(ch, title_font, CREAM) for ch in "TRAIN"], 0)
    sub_font = ImageFont.truetype(FONT_SEMI, p(64))
    sub_layer = line_layer([(ch, sub_font, ORANGE) for ch in "TIMER"], p(64) * 0.9)

    # one gap between icon, title and subtitle, chosen so the top and bottom margins match
    icon_box = ImageChops.difference(img, Image.new("RGB", img.size, BG)).getbbox()  # the background is not black
    title_h = title_layer.getbbox()[3] - title_layer.getbbox()[1]
    sub_h = sub_layer.getbbox()[3] - sub_layer.getbbox()[1]
    gap = (W - icon_box[1] - icon_box[3] - title_h - sub_h) / 2
    title_top = icon_box[3] + gap
    paste_centred(title_layer, title_top)
    paste_centred(sub_layer, title_top + title_h + gap)

    out = ROOT / "release" / "TrainTimer-thumbnail.png"
    out.parent.mkdir(exist_ok=True)
    img.resize((1024, 1024), Image.LANCZOS).save(out, optimize=True)
    print(out)


if __name__ == "__main__":
    main()
