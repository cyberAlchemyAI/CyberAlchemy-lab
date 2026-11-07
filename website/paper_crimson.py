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
from diagram_reading import apply_diagram_reading

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
        raw = apply_diagram_reading(raw, name.as_posix(), relative(name, LAB + '/assets/diagram-reading.css').removesuffix('diagram-reading.css'))
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
        # A static link keeps the repository discoverable with scripts disabled.
        if 'class="topbar-inner"' in raw:
            raw = re.sub(r'(<div class="topbar-inner">.*?</a>)',
                         lambda match: match[1] + '<a class="github-cta" href="https://github.com/cyberAlchemyAI/CyberAlchemy-lab" aria-label="Star CyberAlchemy Lab on GitHub"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false"><path d="M12 .75a11.25 11.25 0 0 0-3.558 21.923c.563.104.77-.244.77-.542 0-.267-.01-.975-.015-1.914-3.13.68-3.79-1.51-3.79-1.51-.512-1.3-1.25-1.646-1.25-1.646-1.022-.699.077-.685.077-.685 1.13.08 1.725 1.16 1.725 1.16 1.005 1.724 2.637 1.226 3.28.938.103-.73.393-1.227.715-1.51-2.5-.285-5.13-1.25-5.13-5.565 0-1.23.44-2.235 1.16-3.022-.116-.285-.503-1.43.11-2.98 0 0 .945-.303 3.095 1.155a10.8 10.8 0 0 1 5.625 0c2.15-1.458 3.094-1.155 3.094-1.155.613 1.55.227 2.695.111 2.98.72.787 1.158 1.792 1.158 3.022 0 4.327-2.633 5.277-5.142 5.555.404.35.765 1.042.765 2.1 0 1.516-.014 2.738-.014 3.11 0 .3.203.65.774.54A11.25 11.25 0 0 0 12 .75Z"/></svg><span><span class="github-cta-verb">Star on </span>GitHub</span></a>', raw, count=1, flags=re.S)
        # A native keyboard fallback for code panes; the enhancement removes
        # unnecessary stops when a pane fits its available space.
        def code_focus(match):
            attrs = match[1]
            if re.search(r'\btabindex\s*=', attrs, re.I):
                return match[0]
            return '<pre' + attrs + ' tabindex="0" data-code-scroll="true">'
        raw = re.sub(r'<pre\b([^>]*)>', code_focus, raw)
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
