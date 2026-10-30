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

    # stopwatch dial with its crown and side button
    cx, cy, r, stroke = p(512), p(445), p(228), p(26)  # the middle of the train, rail included
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ORANGE, width=stroke)
    top = cy - r
    d.rounded_rectangle([cx - p(14), top - p(40), cx + p(14), top + p(12)], radius=p(6), fill=ORANGE)
    d.rounded_rectangle([cx - p(44), top - p(70), cx + p(44), top - p(38)], radius=p(12), fill=ORANGE)
    b = math.radians(-45)
    bx, by = cx + (r + p(10)) * math.cos(b), cy + (r + p(10)) * math.sin(b)
    button = Image.new("RGBA", (p(90), p(90)), (0, 0, 0, 0))
    ImageDraw.Draw(button).rounded_rectangle([p(25), p(30), p(65), p(60)], radius=p(8), fill=ORANGE)
    button = button.rotate(-45, resample=Image.BICUBIC)
    img.paste(button, (int(bx - p(45)), int(by - p(45))), button)

    # armored locomotive head on: chamfered armor plate, vision slits, one headlight, buffer beam, rails
    line = p(20)
    # the outline starts mid-edge so the closing joint is straight and leaves no notch at a corner
    body = [(p(512), p(520)), (p(396), p(520)), (p(396), p(350)), (p(436), p(306)), (p(588), p(306)), (p(628), p(350)), (p(628), p(520))]
    d.line(body + [body[0]], fill=CREAM, width=line, joint="curve")
    for sx in ((p(448), p(500)), (p(524), p(576))):
        d.rounded_rectangle([sx[0], p(346), sx[1], p(366)], radius=p(8), fill=CREAM)
    d.line([p(396), p(404), p(628), p(404)], fill=CREAM, width=p(14))
    for rx in (p(424), p(468), p(556), p(600)):
        d.ellipse([rx - p(8), p(432) - p(8), rx + p(8), p(432) + p(8)], fill=CREAM)
    d.ellipse([p(512) - p(24), p(458) - p(24), p(512) + p(24), p(458) + p(24)], fill=ORANGE)
    d.rounded_rectangle([p(380), p(516), p(644), p(540)], radius=p(8), fill=CREAM)
    for wx in (p(436), p(588)):
        d.ellipse([wx - p(22), p(540) - p(22), wx + p(22), p(540) + p(22)], fill=CREAM)
    d.rounded_rectangle([p(372), p(570), p(652), p(584)], radius=p(7), fill=CREAM)

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
