"""Portable shell fixes applied before the editorial and search fingerprints."""
from html import escape, unescape
import ast
import json
import os
from pathlib import Path
import re
import sys

LAB = 'governance-lab-series'


def apply(stage):
    lab = stage / LAB
    manifest_path = lab / 'research/documentation-manifest.json'
    manifest = json.loads(manifest_path.read_text())
    names = manifest['html_files'] + ['research/reader-study.html', '../robot-learning-series/robot-learning-series.html']
    for name in names:
        page = lab / name
        if not page.is_file():
            continue
        raw = page.read_text(encoding='utf-8')
        relative = lambda path: Path(os.path.relpath(path, page.parent)).as_posix()
        home = relative(lab / 'index.html')
        if not re.search(r'rel=["\']icon["\']',raw):
            icon=relative(lab / 'assets/kep/cyberalchemy-lab-logo-light-v2.svg')
            raw=raw.replace('</head>',f'<link rel="icon" type="image/svg+xml" href="{icon}">\n</head>',1)
        # A brand link means home across all reading families.
        raw = re.sub(r'(<a\b[^>]*\bclass="(?:brand|research-brand)"[^>]*\bhref=")[^"]*',
                     lambda m: m[1] + home, raw)
        raw = re.sub(r'(<a\b[^>]*\bhref=")[^"]*("[^>]*\bclass="(?:brand|research-brand)")',
                     lambda m: m[1] + home + m[2], raw)
        has_chapters = any(script in raw for script in ('lab-docs.js', 'lab-craft-docs.js', 'lab-library-docs.js'))
        if has_chapters:
            href = relative(lab / 'assets/docs-startup.js')
            bootstrap = f'<style>html[data-docs-startup="pending"] main {{ visibility:hidden; }}</style>\n<script src="{escape(href)}"></script>\n'
            # The startup helper is deliberately synchronous and small.
            raw = raw.replace('<head>', '<head>\n' + bootstrap, 1)
        if name == 'research/reader-study.html':
            raw = raw.replace('<body>', '<body><main id="reader-study">', 1).replace('</body>', '</main></body>', 1)
            questions=ast.literal_eval(re.search(r'const questions=(\[.*?\]);',raw,re.S)[1])
            tasks=''.join(f'<li><h3>{escape(title)}</h3><p>{escape(question)}</p></li>' for title,question in questions)
            fallback='<noscript><section id="study-tasks"><h2>Reading tasks</h2><p>Entering and downloading a response here requires JavaScript. You can read these tasks and save your answers in a separate document.</p><ol>'+tasks+'</ol></section></noscript>'
            raw=raw.replace('<form id="reader-form">',fallback+'<form id="reader-form">',1)
        if '../robot-learning-series/' in name:
            raw = raw.replace('aria-label="Topics explored"', '').replace('aria-label="Three essays"', '')
            # Generic containers need no accessible names. Their children carry
            # the named article/link semantics.
            raw = re.sub(r'(<div class="(?:hero-tags|chapter-grid)"[^>]*?)\s+aria-label="[^"]*"', r'\1', raw)
            nav = f'<nav aria-label="Main navigation"><a href="{home}">Home</a><a href="{relative(lab / "start-here.html")}">Start here</a><a href="{relative(lab / "research.html")}">Research</a><a href="#essay-1">Read the series</a></nav>'
            raw = re.sub(r'<a class="top-link".*?</a>', nav, raw, count=1, flags=re.S)
            additions = ''.join(f'<link rel="stylesheet" href="{relative(lab / ("assets/" + path))}">\n' for path in ('site-search.css', 'robot-site-shell.css'))
            additions += ''.join(f'<script src="{relative(lab / ("assets/" + path))}" defer></script>\n' for path in ('search-engine.js', 'site-search.js'))
            raw = raw.replace('</head>', additions + '</head>', 1)
            raw = raw.replace('<body id="top">', '<body id="top" data-site-family="robot">', 1)
        if not re.search(r'<body\b[^>]*data-site-family="research"',raw):
            craft=relative(stage / 'craft-documentation-proposal/craft-model.html')+'#craft-overview'
            def prepare_header(match):
                fragment=match[0]
                if 'data-site-craft' in fragment:return fragment
                if re.search(r'<a\b[^>]*href="[^"]*craft-model.html',fragment):
                    return re.sub(r'(<a\b)([^>]*href="[^"]*craft-model.html[^>]*>)',r'\1 data-site-craft\2',fragment,count=1)
                active=' aria-current="page"' if 'data-edition="craft"' in raw else ''
                return fragment.replace('</nav>',f'<a data-site-craft href="{craft}"{active}>Craft</a></nav>',1)
            raw=re.sub(r'<header class="topbar(?: [^"]*)?">.*?</header>',prepare_header,raw,count=1,flags=re.S)
        # Reserve the shared search slot in static HTML, so enhancement does
        # not push the navigation to a new position after first paint.
        if not re.search(r'<div\b[^>]*class="docs-search"',raw):
            raw=re.sub(r'(</nav>)(\s*</div>\s*</header>)',r'\1<div class="docs-search" data-search-placeholder></div>\2',raw,count=1)
        # Head metadata stays relative until the deployment address is supplied.
        # Absolute canonical/share URLs are produced only for explicit public_url.
        raw = raw.replace('</head>', '<meta property="og:type" content="website">\n</head>', 1)
        title = re.search(r'<title>(.*?)</title>', raw, re.S)
        description = re.search(r'<meta name="description" content="([^"]*)"', raw)
        share = f'<meta property="og:title" content="{escape(unescape(title[1]), quote=True)}">\n' if title else ''
        if description:
            share += f'<meta property="og:description" content="{description[1]}">\n'
        raw = raw.replace('</head>', share + '</head>', 1)
        page.write_text(raw, encoding='utf-8')
    print('Applied portable navigation, startup and reading semantics.')


if __name__ == '__main__':
    apply(Path(sys.argv[1]).resolve())
