"""Detect presenter face centre (normalised) at 4 fps -> faces.json. Used to aim punch-in zooms."""
import cv2, json, subprocess, sys, numpy as np
src, out = sys.argv[1], sys.argv[2]
W, H, FPS = 540, 960, 4
casc = [cv2.CascadeClassifier(cv2.data.haarcascades + n) for n in
        ("haarcascade_frontalface_default.xml", "haarcascade_profileface.xml")]
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", f"fps={FPS},scale={W}:{H}", "-f", "rawvideo",
                      "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
res, i = [], 0
while True:
    b = p.stdout.read(W * H)
    if len(b) < W * H: break
    g = cv2.equalizeHist(np.frombuffer(b, np.uint8).reshape(H, W))
    best = None
    for c in casc:
        for img, flip in ((g, False), (cv2.flip(g, 1), True)):
            for (x, y, w, h) in c.detectMultiScale(img, 1.1, 6, minSize=(28, 28)):
                if flip: x = W - x - w
                if y + h / 2 > H * 0.7: continue           # ignore detections low in frame
                if best is None or w > best[2]: best = (x, y, w, h)
            if c is casc[0]: break                      # frontal: no flip needed
    if best:
        x, y, w, h = best
        res.append([round(i / FPS, 2), round((x + w / 2) / W, 3), round((y + h / 2) / H, 3), round(h / H, 3)])
    i += 1
json.dump(res, open(out, "w"))
print(len(res), "detections of", i, "frames")
