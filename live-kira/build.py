"""Build index.html from src/template.html by inlining the ProfPoji logo."""
import pathlib
here = pathlib.Path(__file__).parent
logo = (here / "../branding/logo/sulaman/sulaman-horizontal-white.svg").read_text()
logo = logo.replace("<svg ", '<svg class="logo" role="img" aria-label="ProfPoji" ', 1)
(here / "index.html").write_text((here / "src/template.html").read_text().replace("<!--LOGO-->", logo))

# Standalone copy for Netlify (full HTML document; the artifact host adds this skeleton itself)
page = (here / "index.html").read_text()
split = page.index('<div class="app"')
head, body = page[:split], page[split:]
doc = f"""<!doctype html>
<html lang="ms">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0A1A33">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Live Kira">
<link rel="icon" href="icon.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<style>:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}body{{margin:0}}</style>
{head}</head>
<body>
{body}
</body>
</html>
"""
out = here / "../netlify-live/index.html"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(doc)
