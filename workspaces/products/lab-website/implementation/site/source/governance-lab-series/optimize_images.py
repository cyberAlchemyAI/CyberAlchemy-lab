"""Produce delivery variants while retaining the original illustration."""
from pathlib import Path
import json
from PIL import Image

root = Path(__file__).resolve().parent
source = root / 'assets/project-workbench.png'
original = Image.open(source).convert('RGB')
variants = []
for width in (640, 1280):
    image = original.resize((width, round(original.height * width / original.width)), Image.Resampling.LANCZOS)
    output = root / f'assets/project-workbench-{width}.webp'
    image.save(output, 'WEBP', quality=86, method=6)
    variants.append({'path': output.relative_to(root).as_posix(), 'width': width, 'height': image.height, 'bytes': output.stat().st_size})
(root / 'research/image-delivery.json').write_text(json.dumps({'original': 'assets/project-workbench.png', 'original_bytes': source.stat().st_size, 'variants': variants}, indent=2) + '\n')
print(json.dumps(variants))
