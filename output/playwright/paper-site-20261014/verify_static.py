from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SITE = ROOT / 'output/website-experiments/telegraph-direction-20261014/dist'
CURRENT = ROOT / 'website/dist'


def run():
    before = json.loads((OUT / 'original-website-before.json').read_text())
    for row in before:
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    records = json.loads((CURRENT / 'governance-lab-series/research/reference-pages.json').read_text())['records']
    for record in records:
        path = Path('governance-lab-series') / record['href']
        pattern = r'<div class="record-body">.*?</article>'
        a = re.search(pattern, (CURRENT / path).read_text(), re.S)
        b = re.search(pattern, (SITE / path).read_text(), re.S)
        assert a and b and a[0] == b[0], path
    checked, broken = [], []

    class Links(HTMLParser):
        def __init__(self, page):
            super().__init__()
            self.page = page

        def handle_starttag(self, tag, attrs):
            for key, value in attrs:
                if key not in ('href', 'src') or not value:
                    continue
                url = urlsplit(value)
                if url.scheme or url.netloc or not url.path:
                    continue
                path = SITE / unquote(url.path.lstrip('/')) if value.startswith('/') else self.page.parent / unquote(url.path)
                checked.append(value)
                if not path.exists():
                    broken.append({'page': str(self.page.relative_to(SITE)), 'target': value})

    pages = list(SITE.rglob('*.html'))
    for page in pages:
        text = page.read_text()
        assert 'http://127.0.0.1:8767' not in text, page
        Links(page).feed(text)
    assert not broken, broken
    manifest = json.loads((SITE / 'release-manifest.json').read_text())
    for row in manifest['files']:
        assert hashlib.sha256((SITE / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    result = {'html_pages': len(pages), 'current_website_files_unchanged': len(before),
              'formal_record_reading_bodies_identical': len(records),
              'local_references_checked': len(checked), 'broken': broken,
              'preview_links_to_current_origin': 0, 'manifest_files_verified': len(manifest['files'])}
    (OUT / 'static-verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    run()
