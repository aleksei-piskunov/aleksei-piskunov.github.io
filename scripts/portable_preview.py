"""Make a portable HTML preview from Jekyll's _site output (standard library only)."""
import os
from pathlib import Path
import re
import shutil

root = Path(__file__).resolve().parents[1]
source = root / "_site"
destination = root / "preview"
destination.mkdir(exist_ok=True)
for item in source.rglob("*"):
    if not item.is_file() or item.name.startswith("_qa-"):
        continue
    relative = item.relative_to(source)
    target = destination / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if item.suffix != ".html":
        shutil.copy2(item, target)
        continue
    def local_link(match):
        attribute, url = match.groups()
        path, separator, anchor = url.partition("#")
        path = path.lstrip("/")
        if not path or path.endswith("/"):
            path += "index.html"
        adjusted = os.path.relpath(destination / path, target.parent)
        return f'{attribute}="{adjusted}{separator}{anchor}"'
    # Embed the current styles: file previews must not reuse a cached older CSS file.
    html = item.read_text()
    html = re.sub(r'<link rel="stylesheet" href="[^"]*assets/style\.css">',
                  lambda _: '<style>\n' + (source / 'assets/style.css').read_text() + '\n</style>', html)
    html = re.sub(r'(href|src)="(/(?!/)[^"]*)"', local_link, html)
    target.write_text(html)
print(f"Portable preview: {destination / 'index.html'}")
