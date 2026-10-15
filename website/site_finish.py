"""Final structural metadata, after prose adoption and before search indexing."""
from html import escape, unescape
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parent
LAB = 'governance-lab-series'


def apply(stage):
    lab = stage / LAB
    from reference_pages import split
    records = split(stage)
    manifest_path = lab / 'research/documentation-manifest.json'
    manifest = json.loads(manifest_path.read_text())
    # This inspection metadata is needed by offline tooling and Markdown import.
    # Include it even though browsers load the separate route script.
    manifest['reference_pages_manifest'] = 'research/reference-pages.json'
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    config = json.loads((ROOT / 'site.json').read_text())
    public = config.get('public_url', '')
    if public and (urlsplit(public).scheme not in {'http', 'https'} or not urlsplit(public).netloc):
        raise ValueError('public_url must be an explicit absolute HTTP(S) website base URL.')
    names = manifest['html_files'] + ['research/reader-study.html', '../robot-learning-series/robot-learning-series.html']
    for name in names:
        page = lab / name
        if not page.is_file():
            continue
        raw = page.read_text(encoding='utf-8')
        if 'http-equiv="refresh"' in raw:
            continue
        title=re.search(r'<title>(.*?)</title>',raw,re.S)
        if title:
            raw=re.sub(r'<meta property="og:title"[^>]*>',f'<meta property="og:title" content="{escape(unescape(title[1]),quote=True)}">',raw)
        canonical = urljoin(public.rstrip('/') + '/', page.relative_to(stage).as_posix()) if public else page.name
        raw = re.sub(r'<link\b[^>]*rel="canonical"[^>]*>\s*', '', raw)
        extra = f'<link rel="canonical" href="{escape(canonical, quote=True)}">\n'
        if public:
            extra += f'<meta property="og:url" content="{escape(canonical, quote=True)}">\n'
        raw = raw.replace('</head>', extra + '</head>', 1)
        page.write_text(raw, encoding='utf-8')
    # The original alias was retained through prose preservation. Its delivered
    # form is now a redirect with working deep links and a no-JS fallback.
    destination = 'governance-lab-reference.html'
    redirect = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CyberAlchemy Lab guide</title><link rel="canonical" href="{destination}"><link rel="icon" type="image/svg+xml" href="assets/kep/cyberalchemy-lab-logo-light-v2.svg"><script>location.replace({json.dumps(destination)}+location.search+location.hash);</script><noscript><meta http-equiv="refresh" content="1; url={destination}"></noscript></head><body><main><h1>The Lab guide has moved</h1><p><a id="destination" href="{destination}">Open the guide</a></p><script>document.getElementById('destination').href={json.dumps(destination)}+location.search+location.hash;</script></main></body></html>\n'''
    (lab / 'governance-lab-series.html').write_text(redirect, encoding='utf-8')
    receipt_path = lab / 'research/editorial-edition.json'
    receipt = json.loads(receipt_path.read_text())
    for name, row in receipt['pages'].items():
        row['sha256'] = hashlib.sha256((stage / name).read_bytes()).hexdigest()
    receipt['structural_finish'] = 'Portable canonical metadata and legacy guide redirect. Protected wording unchanged.'
    receipt['reference_pages'] = records['records']
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
    print('Prepared canonical routes and final editorial page fingerprints.')


if __name__ == '__main__':
    apply(Path(sys.argv[1]).resolve())
