"""Jana sticker kepala hos daripada gambar: buang latar (rembg), potong pada leher,
gred warna, bingkai putih gaya kertas.

  python3 tools/make_head.py gambar.jpg  X0 Y0 X1 Y1  [cutY]  [output_prefix]  [model: u2net_human_seg | birefnet-portrait]  [ellipse cx,cy,rx,ry]
  (X0..Y1 = kotak sekitar kepala dalam gambar asal; cutY = garis potong leher dalam kotak itu)
Output: assets/host/head.png + head.json (titik sambungan leher)
"""
import json, sys
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
from rembg import remove, new_session

src = sys.argv[1]; box = tuple(int(v) for v in sys.argv[2:6]); cut = int(sys.argv[6]) if len(sys.argv) > 6 else 500
out_prefix = sys.argv[7] if len(sys.argv) > 7 else "assets/host/head"
model = sys.argv[8] if len(sys.argv) > 8 else "u2net_human_seg"
ellipse = [float(v) for v in sys.argv[9].split(",")] if len(sys.argv) > 9 else None  # cx,cy,rx,ry (pecahan kotak)
im = ImageOps.exif_transpose(Image.open(src)).convert("RGB").crop(box)
cut_img = remove(im, session=new_session(model)).convert("RGBA")
a = np.array(cut_img).astype(float); H, W = a.shape[:2]
a[..., 3] *= np.clip((cut - np.arange(H)[:, None]) / 10, 0, 1)
if ellipse:
    ex, ey, erx, ery = ellipse[0] * W, ellipse[1] * H, ellipse[2] * W, ellipse[3] * H
    yy, xx = np.mgrid[0:H, 0:W]
    d = ((xx - ex) / erx) ** 2 + ((yy - ey) / ery) ** 2
    a[..., 3] *= np.clip((1.0 - d) * 12, 0, 1)
img = Image.fromarray(a.astype(np.uint8), "RGBA")
rgb = ImageEnhance.Color(ImageEnhance.Contrast(img.convert("RGB")).enhance(1.08)).enhance(1.12)
r, g, b = rgb.split(); r = r.point(lambda v: min(255, v * 1.03))
img = Image.merge("RGBA", (r, g, b, img.split()[3]))
pad = 24
big = Image.new("RGBA", (W + 2 * pad, H + 2 * pad), (0, 0, 0, 0))
al = Image.new("L", big.size, 0); al.paste(img.split()[3], (pad, pad))
outline = al.point(lambda v: 255 if v > 40 else 0).filter(ImageFilter.MaxFilter(19)).filter(ImageFilter.GaussianBlur(1.2))
st = Image.new("RGBA", big.size, (255, 248, 236, 0)); st.putalpha(outline)
big.alpha_composite(st); big.alpha_composite(img, (pad, pad))
out = big.crop(big.getbbox()); out.save(out_prefix + ".png")
arr = np.array(out)[..., 3]; bottom = np.where(arr.max(1) > 0)[0].max()
meta = {"w": out.size[0], "h": out.size[1], "neckX": int(np.where(arr[bottom - 20] > 0)[0].mean()), "neckY": int(bottom)}
json.dump(meta, open(out_prefix + ".json", "w")); print(meta)
