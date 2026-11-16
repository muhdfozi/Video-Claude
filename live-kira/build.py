"""Build index.html from src/template.html by inlining the ProfPoji logo."""
import pathlib
here = pathlib.Path(__file__).parent
logo = (here / "../branding/logo/sulaman/sulaman-horizontal-white.svg").read_text()
logo = logo.replace("<svg ", '<svg class="logo" role="img" aria-label="ProfPoji" ', 1)
(here / "index.html").write_text((here / "src/template.html").read_text().replace("<!--LOGO-->", logo))
