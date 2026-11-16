"""Generate ProfPoji logo SVGs (text converted to outlines, no font dependency)."""
import math, os, sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONT_DIR = sys.argv[1]
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)

NAVY = "#0A1A33"
RED = "#E10600"
WHITE = "#FFFFFF"

_fonts = {}


def text_path(font, text, size, x, y, tracking=0.0, anchor="start"):
    if font not in _fonts:
        _fonts[font] = TTFont(os.path.join(FONT_DIR, font))
    f = _fonts[font]
    gs, cmap, upm = f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm
    s = size / upm
    width = sum(gs[cmap[ord(c)]].width * s for c in text) + tracking * (len(text) - 1)
    if anchor == "middle":
        x -= width / 2
    elif anchor == "end":
        x -= width
    pen = SVGPathPen(gs)
    cx = 0
    for c in text:
        g = cmap[ord(c)]
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x + cx, y)))
        cx += gs[g].width * s + tracking
    return pen.getCommands(), width


VARIANT = "key"
APP_T = {"cap": "translate(78 74) scale(1.6)", "shield": "translate(70 40) scale(1.75)"}


def icon(main=NAVY, accent=RED, cutout=WHITE, variant=None):
    """P monogram with speedometer bowl. Variants: cap, clean, tie, key, shield."""
    variant = variant or VARIANT
    if variant == "shield":
        shield = "M100,4 L190,30 V118 Q190,196 100,236 Q10,196 10,118 V30 Z"
        inner = icon(cutout, accent, main, "clean").replace('<g transform="skewX(-9) translate(18 0)">', '<g>', 1)
        return (f'<g transform="translate(22 8) scale(0.86) skewX(-6)"><path d="{shield}" fill="{main}"/>'
                f'<path d="M10,30 L100,4 L190,30" fill="none" stroke="{accent}" stroke-width="8" stroke-linejoin="round"/>'
                f'<g transform="translate(24 30) scale(0.82)">{inner}</g></g>')
    cx, cy, ro, ri = 100, 122, 58, 40
    parts = []
    # speed streaks
    for i, (y, l) in enumerate([(112, 30), (128, 22), (144, 14)]):
        parts.append(f'<rect x="{26 - l - 6}" y="{y}" width="{l}" height="7" rx="3.5" fill="{accent}"/>')
    # stem + bowl (even-odd hole)
    bowl = (f"M52,64 H{cx} A{ro},{ro} 0 0 1 {cx},{cy + ro} H52 Z "
            f"M54,{cy - ri} V{cy + ri} H{cx} A{ri},{ri} 0 0 0 {cx},{cy - ri} Z")
    parts.append(f'<path d="{bowl}" fill="{main}" fill-rule="evenodd"/>')
    if variant == "tie":
        parts.append(f'<path d="M26,62 H58 L52,92 H32 Z" fill="{accent}"/>')
        parts.append(f'<path d="M32,96 H52 L62,178 L42,210 L22,178 Z" fill="{accent}"/>')
        parts.append(f'<path d="M30,112 L54,104 M27,140 L57,128 M24,168 L60,154" stroke="{main}" stroke-opacity=".35" stroke-width="5"/>')
    elif variant == "key":
        # key blade with cut teeth on the left, rounded tip
        parts.append(f'<path d="M30,64 H54 V204 Q54,214 44,214 H40 V202 H30 V190 H40 V180 H30 V168 H40 V158 H30 Z" fill="{main}"/>')
        parts.append(f'<rect x="45" y="150" width="4" height="56" rx="2" fill="{cutout}" opacity=".9"/>')
        # keyring hole + red ring
        parts.append(f'<circle cx="42" cy="82" r="6.5" fill="{cutout}"/>')
        parts.append(f'<circle cx="24" cy="70" r="14" fill="none" stroke="{accent}" stroke-width="4.5"/>')
    else:
        parts.append(f'<rect x="30" y="64" width="24" height="142" fill="{main}"/>')
    # gauge ticks inside hole
    for k in range(9):
        a = math.radians(-215 + k * (250 / 8))
        r1, r2 = (ri - 13, ri - 5) if k % 2 == 0 else (ri - 10, ri - 5)
        x1, y1 = cx + r1 * math.cos(a), cy + r1 * math.sin(a)
        x2, y2 = cx + r2 * math.cos(a), cy + r2 * math.sin(a)
        col = accent if k >= 7 else main
        parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                     f'stroke="{col}" stroke-width="3.6" stroke-linecap="round"/>')
    # needle pointing high
    a = math.radians(-35)
    tipx, tipy = cx + 30 * math.cos(a), cy + 30 * math.sin(a)
    px, py = 4.5 * math.cos(a + math.pi / 2), 4.5 * math.sin(a + math.pi / 2)
    parts.append(f'<path d="M{cx + px:.1f},{cy + py:.1f} L{tipx:.1f},{tipy:.1f} L{cx - px:.1f},{cy - py:.1f} Z" fill="{accent}"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="{main}"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="2.6" fill="{cutout}"/>')
    # graduation cap sitting on the P
    cap = []
    cap.append(f'<path d="M48,44 L96,44 L94,62 Q72,70 50,62 Z" fill="{main}"/>')  # skull cap
    cap.append(f'<path d="M8,36 L72,14 L136,36 L72,58 Z" fill="{main}" stroke="{cutout}" stroke-width="3" stroke-linejoin="round"/>')
    cap.append(f'<circle cx="72" cy="36" r="4" fill="{accent}"/>')
    cap.append(f'<path d="M72,36 L126,44 L126,70" fill="none" stroke="{accent}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')
    cap.append(f'<path d="M120,68 L132,68 L134,86 L118,86 Z" fill="{accent}"/>')
    if variant == "cap":
        parts.append(f'<g transform="rotate(-8 72 36)">{"".join(cap)}</g>')
    return f'<g transform="skewX(-9) translate(18 0)">{"".join(parts)}</g>'


def wordmark(x, y, size, c1=NAVY, c2=RED):
    d1, w1 = text_path("Russo_One.ttf", "PROF", size, x, y)
    d2, w2 = text_path("Russo_One.ttf", "POJI", size, x + w1 + size * 0.04, y)
    return (f'<path d="{d1}" fill="{c1}"/><path d="{d2}" fill="{c2}"/>', w1 + w2 + size * 0.04)


def tagline(x, y, size, width, color, text="YOUR PROFESSIONAL RECOND ADVISOR"):
    # fit tracking so tagline spans `width`
    _, w0 = text_path("Saira_Condensed_wght_500.ttf", text, size, 0, 0)
    tr = (width - w0) / (len(text) - 1)
    d, _ = text_path("Saira_Condensed_wght_500.ttf", text, size, x, y, tracking=tr)
    return f'<path d="{d}" fill="{color}"/>'


def svg(w, h, body, bg=None):
    bgr = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{bgr}{body}</svg>'


def horizontal(main=NAVY, accent=RED, cutout=WHITE, sub=None, bg=None):
    sub = sub or main
    X0 = 200
    wm, ww = wordmark(X0, 128, 96, main, accent)
    tl = tagline(X0 + 4, 172, 27, ww - 8, sub)
    hash_d, _ = text_path("Saira_Condensed_wght_800.ttf", "#trustedSAever", 24, X0 + ww, 210, tracking=1, anchor="end")
    rule = f'<rect x="{X0 + 4}" y="190" width="{ww - 210}" height="3" fill="{accent}"/>'
    body = (f'<g transform="translate(10 6)">{icon(main, accent, cutout)}</g>'
            f'<g transform="skewX(-9) translate(34 0)">{wm}</g>{tl}{rule}<path d="{hash_d}" fill="{accent}"/>')
    W = int(X0 + ww + 40)
    return svg(W, 232, body, bg), W


def stacked(main=NAVY, accent=RED, cutout=WHITE, sub=None, bg=None):
    sub = sub or main
    W = 560
    _, ww = wordmark(0, 0, 96, main, accent)
    wm, _ = wordmark((W - ww) / 2 + 36, 338, 96, main, accent)
    tl = tagline((W - ww) / 2 + 4, 384, 27, ww - 8, sub)
    hd, _ = text_path("Saira_Condensed_wght_800.ttf", "#trustedSAever", 28, W / 2, 432, tracking=1, anchor="middle")
    body = (f'<g transform="translate({W / 2 - 112} 18) scale(1.15)">{icon(main, accent, cutout)}</g>'
            f'<g transform="skewX(-9)">{wm}</g>{tl}<path d="{hd}" fill="{accent}"/>')
    return svg(W, 460, body, bg)


def write(name, content):
    with open(os.path.join(OUT, name), "w") as f:
        f.write(content)


if len(sys.argv) > 3:
    VARIANT = sys.argv[3]
h, hw = horizontal()
write("logo-horizontal.svg", h)
write("logo-horizontal-dark.svg", horizontal(WHITE, RED, NAVY, "#C9D3E3", NAVY)[0])
write("logo-horizontal-white.svg", horizontal(WHITE, RED, NAVY, "#C9D3E3")[0])
write("logo-stacked.svg", stacked())
write("logo-stacked-white.svg", stacked(WHITE, RED, NAVY, "#C9D3E3"))
write("icon.svg", svg(220, 220, f'<g transform="translate(0 4)">{icon()}</g>'))
write("icon-white.svg", svg(220, 220, f'<g transform="translate(0 4)">{icon(WHITE, RED, NAVY)}</g>'))
write("icon-app.svg", svg(512, 512, f'<rect width="512" height="512" rx="112" fill="{NAVY}"/>'
                         f'<g transform="{APP_T.get(VARIANT, "translate(96 34) scale(1.6)")}">{icon(WHITE, RED, NAVY)}</g>'))
print("ok", hw)
