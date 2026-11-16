"""Build the phone 'Kira Layak' page.

Car data, formulas and image matching are taken from live-kira/src/template.html
so both pages always share the same stock list and prices.
Outputs:
  kira-gaji/index.html      (artifact preview; host adds the HTML skeleton)
  netlify-gaji/index.html   (standalone site for Netlify) + cars/ + icons
"""
import pathlib, re, shutil

here = pathlib.Path(__file__).parent
root = here.parent
live = (root / "live-kira/src/template.html").read_text()


def between(start, end):
    i = live.index(start)
    j = live.index(end, i)
    return live[i:j]


data = "\n".join([
    between("const SAMPLE_STOCK", "const store"),
    between("function parseStock", "/* speedometer gauge"),
    between("function gauge", "function render"),
    re.search(r"function esc\(s\).*\n", live).group(0),
])

logo = (root / "branding/logo/sulaman/sulaman-horizontal-white.svg").read_text()
logo = logo.replace("<svg ", '<svg class="logo" role="img" aria-label="ProfPoji" ', 1)
page = (here / "src/template.html").read_text().replace("<!--LOGO-->", logo).replace("/*@DATA@*/", data)
(here / "index.html").write_text(page)

split = page.index('<div class="wrap">')
head, body = page[:split], page[split:]
doc = f"""<!doctype html>
<html lang="ms">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0A1A33">
<meta name="description" content="Masukkan gaji bersih, terus nampak kereta recond yang anda layak berserta anggaran bulanan. Prof Poji, your professional recond advisor.">
<meta property="og:title" content="Gaji anda layak kereta apa? | Prof Poji">
<meta property="og:description" content="Kalkulator gaji layak kereta recond. Anggaran bulanan terus.">
<link rel="icon" href="icon.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<style>:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}body{{margin:0}}</style>
{head}</head>
<body>
{body}
</body>
</html>
"""
out = root / "netlify-gaji"
(out / "cars").mkdir(parents=True, exist_ok=True)
(out / "index.html").write_text(doc)
for f in (root / "live-kira/cars").glob("*.webp"):
    shutil.copy(f, out / "cars" / f.name)
for f in ("icon.png", "apple-touch-icon.png"):
    shutil.copy(root / "netlify-live" / f, out / f)
