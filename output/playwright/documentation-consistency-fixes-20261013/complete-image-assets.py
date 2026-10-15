"""Package already-generated illustrations at existing declared URLs.

No source image is edited, and an asset supplied concurrently is never overwritten.
"""
from pathlib import Path
import hashlib
import json
import os
import tempfile
from PIL import Image

base=Path('/mnt/c/Users/vlad_/.codex/generated_images/01a132c9-ec50-7082-892a-fff2c7c5eca9')
assets=Path('website/source/governance-lab-series/assets/hackathon-ideas')
assets.mkdir(parents=True,exist_ok=True)
inputs={
    'agent-company':'exec-84ec9e77-2a04-4228-8b71-6d7a334f72eb.png',
    'forkable-city':'exec-0eae3b9d-c5c6-4ee4-8e2c-d14413d4c02a.png',
    'rewriting-playbook':'exec-08dc6a78-7870-419c-bc89-541d0215b8d7.png',
    'machine-beliefs':'exec-5e5b2e4b-98d3-4c57-9e2b-f9daab5fb0bd.png',
    'tool-invention':'exec-eb808bf9-c91e-45cd-9595-6425bb234ffd.png',
    'musical-ecosystem':'exec-a20cdfaf-f7d9-4894-99d5-acd64c22087d.png',
}
rows=[]
for slug,name in inputs.items():
    source=base/name
    target=assets/(slug+'.webp')
    if target.exists():
        rows.append({'asset':str(target),'action':'preserved-existing'})
        continue
    with Image.open(source) as image:
        dimensions=image.size
        with tempfile.NamedTemporaryFile(dir=assets,suffix='.tmp',delete=False) as temporary:
            temporary_path=Path(temporary.name)
        try:
            image.save(temporary_path,format='WEBP',quality=88,method=6)
            temporary_path.chmod(0o644)
            try:
                os.link(temporary_path,target)
                action='created-from-supplied-image'
            except FileExistsError:
                action='preserved-concurrent-asset'
        finally:
            temporary_path.unlink()
    rows.append({'asset':str(target),'action':action,'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'dimensions':dimensions,'asset_sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
Path('output/playwright/documentation-consistency-fixes-20261013/image-dependency-receipt.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps([{'asset':r['asset'],'action':r['action']}for r in rows],indent=2))
