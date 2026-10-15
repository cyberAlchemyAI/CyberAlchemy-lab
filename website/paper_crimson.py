"""Apply the approved Paper and crimson edition before final search generation."""
from html import escape
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urljoin, urlsplit, unquote

from reading_paths import apply as reading_paths
from company_brain_migration import apply as consolidate, HOME_TARGETS, fragment_links, update_sidebar, finalize_ledger
from diagram_presentation import apply_visual_fixes, wrap_map_titles

LAB = 'governance-lab-series'
ASSETS = LAB + '/assets/paper-crimson/'


def relative(page, destination):
    return os.path.relpath(destination, page.parent).replace(os.sep, '/')


def home(stage):
    lab = stage / LAB
    old = (lab / 'index.html').read_text()
    main = re.search(r'<main\b[^>]*id="lab-home"[^>]*>(.*?)</main>', old, re.S)
    if not main:
        raise ValueError('The source homepage is required for content reconciliation.')
    announcement = re.search(r'<aside class="hack-home-announcement".*?</aside>', main[1], re.S)
    raw = (lab / 'templates/paper-home.html.in').read_text()
    head = old.split('</head>', 1)[0]
    dependencies = re.findall(r'<link\b[^>]*rel="stylesheet"[^>]*>|<script\b[^>]*src="[^"]+"[^>]*></script>', head)
    metadata = re.findall(r'<meta\b[^>]*property="og:[^"]+"[^>]*>|<link\b[^>]*rel="canonical"[^>]*>', head)
    dependencies = [item for item in dependencies if any(name in item for name in ['kep/design-system.css', 'hackathon-', 'hackathon-status.js'])]
    raw = raw.replace('<head>', '<head>\n' + '\n'.join(dependencies + metadata), 1)
    event = re.search(r'<script type="application/json" id="event-config">.*?</script>', old, re.S)
    if event:
        raw = raw.replace('<body class="paper-home">', '<body class="paper-home">' + event[0], 1)
    raw = raw.replace('<main id="main">', '<main id="main">' + (announcement[0] if announcement else ''), 1)
    aliases = []
    for identity, (destination, label) in HOME_TARGETS.items():
        if destination.startswith('#'):
            target = destination[1:]
            raw = re.sub(r'(<(?:section|h1|h2)\b[^>]*id="' + re.escape(target) + r'"[^>]*>)',
                         lambda m: '<span class="fragment-alias" id="' + identity + '" data-migrated-to="' + destination + '" aria-hidden="true"></span>' + m[0], raw, count=1)
        else:
            aliases.append(identity)
    raw = raw.replace('<main id="main">', '<main id="main">' + fragment_links({key: HOME_TARGETS[key] for key in aliases}), 1)
    raw = raw.replace('</head>', '<link rel="stylesheet" href="assets/paper-crimson/migration.css"><script src="assets/paper-crimson/migrated-fragments.js" defer></script></head>', 1)
    (lab / 'index.html').write_text(raw)


def apply(stage):
    stage = Path(stage)
    reading_paths(stage)
    consolidate(stage)
    home(stage)
    finalize_ledger(stage)
    manifest_file = stage / LAB / 'research/documentation-manifest.json'
    manifest = json.loads(manifest_file.read_text())
    paths = sorted(p.name for p in (stage / LAB).glob('path-*.html'))
    manifest['html_files'] = list(dict.fromkeys(manifest['html_files'] + paths))
    for binding in manifest['bindings']:
        if 'start-here.html' in binding['affected_pages'] and 'company-brain.html' not in binding['affected_pages']:
            binding['affected_pages'] = sorted(binding['affected_pages'] + ['company-brain.html'])
    manifest['visual_edition'] = {'name': 'Paper & crimson', 'reading_paths': paths,
                                'conceptual_introduction': 'company-brain.html', 'migration_receipt': 'research/company-brain-migration.json'}
    manifest_file.write_text(json.dumps(manifest, indent=2) + '\n')
    for asset_name in ['system-map-agent.svg', 'system-map-overview.svg']:
        asset = stage / LAB / 'assets' / asset_name
        asset.write_text(wrap_map_titles(asset.read_text()))
    for page in stage.rglob('*.html'):
        name = page.relative_to(stage)
        if 'research/sources/' in name.as_posix() or 'templates/' in name.parts:
            continue
        raw = page.read_text()
        raw = update_sidebar(raw, relative(name, LAB + '/company-brain.html'), name == Path(LAB + '/company-brain.html'))
        if '<head' not in raw or '<body' not in raw:
            continue
        favicon = relative(name, ASSETS + 'favicon.svg')
        raw = apply_visual_fixes(raw, name.as_posix(), favicon, 0).replace('preview-diagram-tools', 'diagram-view-tools')
        if name == Path(LAB + '/index.html'):
            page.write_text(raw)
            continue
        raw = re.sub(r'<html\b', '<html data-site-design="paper"', raw, count=1)
        def body(match):
            attrs = match[1]
            if 'class="' in attrs:
                attrs = re.sub(r'class="([^"]*)"', r'class="\1 site-document"', attrs, count=1)
            else:
                attrs += ' class="site-document"'
            return '<body' + attrs + '>'
        raw = re.sub(r'<body([^>]*)>', body, raw, count=1)
        boot, css, js = [relative(name, ASSETS + asset) for asset in ['theme-boot.js', 'appearance.css', 'appearance.js']]
        raw = raw.replace('</head>', f'<script src="{boot}"></script><link rel="stylesheet" href="{css}"><script src="{js}" defer></script></head>', 1)
        if 'data-reading-path-page=' in raw:
            href = relative(name, ASSETS + 'reading-path.js')
            raw = raw.replace('</head>', f'<script src="{href}" defer></script></head>', 1)
        if not re.search(r'http-equiv=["\']refresh', raw, re.I) and 'class="topbar' not in raw:
            destination = relative(name, LAB + '/index.html')
            guide = relative(name, LAB + '/start-here.html')
            logo = relative(name, ASSETS + 'logo.svg')
            header = f'<header class="topbar"><div class="topbar-inner"><a class="brand" href="{destination}"><img src="{logo}" alt="CyberAlchemy Lab" width="176" height="41"></a><nav aria-label="Main navigation"><a href="{destination}">The Lab</a><a href="{guide}">Guide</a></nav></div></header>'
            raw = raw.replace('site-document"', 'site-document site-standalone"', 1)
            raw = re.sub(r'(<body[^>]*>)', lambda m: m[1] + header, raw, count=1)
        if name.parent == Path(LAB) and name.name.startswith('path-'):
            config = json.loads((Path(__file__).parent / 'site.json').read_text())
            canonical = urljoin(config['public_url'].rstrip('/') + '/', name.as_posix()) if config.get('public_url') else name.name
            raw = re.sub(r'<link\b[^>]*rel="canonical"[^>]*>', f'<link rel="canonical" href="{escape(canonical, quote=True)}">', raw)
            raw = re.sub(r'<meta property="og:url"[^>]*>', f'<meta property="og:url" content="{escape(canonical, quote=True)}">', raw)
        page.write_text(raw)
    print('Applied approved Paper and crimson appearance, six guided reading paths, and consolidated company-brain content with legacy link compatibility.')


def finalize(stage):
    """Version dynamic payloads and refresh fingerprints after head-only edits."""
    stage = Path(stage)
    lab = stage / LAB
    search_file = lab / 'research/site-search-index.json'
    search = json.loads(search_file.read_text())
    for name, delivery in [('site-search-index', search['delivery']), ('site-search-quick', search['quick_delivery'])]:
        script = lab / 'assets' / (name + '.js')
        fallback = lab / 'assets' / delivery['fallback']
        digest = hashlib.sha256(fallback.read_bytes()).hexdigest()[:12]
        script.write_text(script.read_text().replace('"' + fallback.name + '"', '"' + fallback.name + '?v=' + digest + '"'))
        delivery['script_bytes'] = script.stat().st_size
    controller = lab / 'assets/site-search.js'
    code = controller.read_text().replace("file==='site-search-index.js'", "file.split('?')[0]==='site-search-index.js'")
    for name in ['site-search-index', 'site-search-quick']:
        digest = hashlib.sha256((lab / 'assets' / (name + '.js')).read_bytes()).hexdigest()[:12]
        code = code.replace("payload('" + name + ".js',", "payload('" + name + '.js?v=' + digest + "',")
    controller.write_text(code)
    digests = {}
    def version(match, page):
        href = match[2]
        parsed = urlsplit(href)
        if parsed.scheme or parsed.netloc or not parsed.path.endswith(('.css', '.js', '.svg')):
            return match[0]
        target = (page.parent / unquote(parsed.path)).resolve()
        if not target.is_relative_to(stage.resolve()) or not target.is_file():
            return match[0]
        if target not in digests:
            digests[target] = hashlib.sha256(target.read_bytes()).hexdigest()[:12]
        return match[1] + parsed.path + '?v=' + digests[target] + '"'
    manifest = json.loads((lab / 'research/documentation-manifest.json').read_text())
    names = manifest['html_files'] + ['research/reader-study.html', '../robot-learning-series/robot-learning-series.html']
    for name in names:
        page = lab / name
        raw = page.read_text()
        # Anchor destinations retain their exact original URLs.
        raw = re.sub(r'(<(?:script|link)\b[^>]*?(?:src|href)=")([^"]+)"', lambda m: version(m, page), raw)
        page.write_text(raw)
    search['index_sha256'] = hashlib.sha256((lab / 'assets/site-search-index.js').read_bytes()).hexdigest()
    for name in search['source_html_sha256']:
        search['source_html_sha256'][name] = hashlib.sha256((lab / name).read_bytes()).hexdigest()
    search_file.write_text(json.dumps(search, indent=2) + '\n')
    editorial_file = lab / 'research/editorial-edition.json'
    editorial = json.loads(editorial_file.read_text())
    for name, row in editorial['pages'].items():
        row['sha256'] = hashlib.sha256((stage / name).read_bytes()).hexdigest()
    editorial['visual_edition'] = 'Paper & crimson; unique content consolidated; existing routes and fragments retained.'
    editorial_file.write_text(json.dumps(editorial, indent=2) + '\n')
    print('Versioned local appearance/search assets and refreshed final page fingerprints.')


if __name__ == '__main__':
    (finalize if '--finalize' in sys.argv else apply)(Path(sys.argv[1]).resolve())
