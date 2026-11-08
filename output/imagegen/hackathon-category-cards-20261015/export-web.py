from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[3]
for name in ['studio-front-end','open-projects']:
    source=Path(__file__).parent/(name+'-v1.png')
    target=root/'website/source/governance-lab-series/assets/hackathon-categories'/(name+'-v1.webp')
    with Image.open(source) as image:
        assert image.size==(1536,1024)
        image.convert('RGB').save(target,'WEBP',quality=85,method=6)
    print(name,target.stat().st_size)
