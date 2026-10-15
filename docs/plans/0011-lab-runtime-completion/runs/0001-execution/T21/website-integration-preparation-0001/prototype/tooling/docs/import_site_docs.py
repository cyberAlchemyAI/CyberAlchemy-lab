#!/usr/bin/env python3
"""Import the reviewed Lab website into a repository-readable Markdown edition.

Uses only the Python standard library. Source HTML is read, never executed.
The import creates explanatory documentation, not admitted authority records.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
from datetime import date
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
OMIT = {'script', 'style', 'aside', 'nav', 'button', 'input', 'select', 'option', 'kbd'}


class Node:
    def __init__(self, tag='', attrs=None):
        self.tag, self.attrs, self.children = tag, dict(attrs or []), []

    def all(self, predicate):
        result = [self] if predicate(self) else []
        for child in self.children:
            if isinstance(child, Node):
                result.extend(child.all(predicate))
        return result

    def first(self, predicate):
        return next(iter(self.all(predicate)), None)

    def text(self):
        return ''.join(c.text() if isinstance(c, Node) else c for c in self.children)

    def has(self, cls):
        return cls in self.attrs.get('class', '').split()


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.root, self.stack = Node(), []
        self.stack = [self.root]
        self.feed(text)
        self.ids = {n.attrs['id']: n for n in self.root.all(lambda n: 'id' in n.attrs)}

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                self.stack = self.stack[:index]
                break

    def handle_data(self, value):
        self.stack[-1].children.append(value)


def compact(text):
    return re.sub(r'\s+', ' ', text).strip()


def serialize(node):
    if isinstance(node, str):
        return escape(node)
    attrs = ''.join(f' {k}="{escape(v or "", quote=True)}"' for k, v in node.attrs.items())
    return f'<{node.tag}{attrs}>' + ''.join(serialize(c) for c in node.children) + f'</{node.tag}>'


class Importer:
    def __init__(self, site, repo, imported_on=None):
        self.site, self.repo = site.resolve(), repo.resolve()
        self.imported_on = imported_on or date.today().isoformat()
        self.dest = self.repo / 'docs/lab'
        self.documents, self.jobs, self.routes, self.source_hashes = {}, [], {}, {}
        self.assets, self.unresolved = {}, set()
        self.style = '\n'.join(p.read_text() for p in sorted((site / 'assets').glob('*.css')))
        self.style += '\n' + (site / 'assets/kep/design-system.css').read_text()
        self.style = re.sub(r'@font-face\s*\{[^}]*\}', '', self.style)
        self.style += '\nsvg{font-family:Arial,sans-serif}text{font-family:Arial,sans-serif}'

    def document(self, source):
        if source not in self.documents:
            raw = (self.site / source).read_bytes()
            self.source_hashes[source] = hashlib.sha256(raw).hexdigest()
            self.documents[source] = Document(raw.decode('utf-8'))
        return self.documents[source]

    def add(self, source, identifier, output, title=None):
        doc = self.document(source)
        node = doc.ids.get(identifier) if identifier else doc.root.first(lambda n: n.tag == 'main')
        if node is None:
            raise ValueError(f'Missing source section {source}#{identifier}')
        self.jobs.append((source, node, output, title))
        self.routes.setdefault((source, ''), output)
        for child in node.all(lambda n: 'id' in n.attrs):
            self.routes[(source, child.attrs['id'])] = output

    def relative(self, target, output):
        return Path(os.path.relpath(target, (self.dest / output).parent)).as_posix()

    def link(self, value, source, output):
        parts = urlsplit(value)
        if parts.scheme in {'http', 'https', 'mailto'}:
            return value
        if parts.scheme:
            self.unresolved.add(value)
            return ''
        target = (self.site / source).parent / unquote(parts.path) if parts.path else self.site / source
        target = Path(os.path.abspath(target))
        name = Path(os.path.relpath(target, self.site)).as_posix()
        route = self.routes.get((name, parts.fragment)) or self.routes.get((name, ''))
        if route:
            result = self.relative(self.dest / route, output)
            if parts.fragment and (name, parts.fragment) in self.routes:
                result += '#' + parts.fragment
            return result
        if '/research/sources/runtime/' in target.as_posix() and target.is_file():
            return self.asset(target,output)
        if '/research/sources/' in target.as_posix():
            repo_path = target.as_posix().split('/research/sources/', 1)[1]
            live = self.repo / repo_path
            if live.is_file():
                return self.relative(live, output)
            # Retained public snapshots are downloadable inert resources.
            # Keep the original repository route when its file is available.
            if target.is_file() and target.resolve().is_relative_to(self.site / 'research/sources'):
                return self.asset(target, output)
        if target.is_file() and target.suffix.lower() not in {'.html', '.htm', '.py', '.js', '.css'}:
            return self.asset(target, output)
        self.unresolved.add(name + ('#' + parts.fragment if parts.fragment else ''))
        return ''

    def asset(self, path, output):
        key = path.as_posix()
        if key not in self.assets:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            relative = Path('assets') / f'{digest[:12]}-{path.name}'
            target = self.dest / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            self.assets[key] = {'path': relative.as_posix(), 'sha256': digest}
        return self.relative(self.dest / self.assets[key]['path'], output)

    def children(self, node, source, output):
        return ''.join(self.md(c, source, output) for c in node.children)

    def diagram(self, node, output):
        large = node.attrs.get('role') == 'img' or node.attrs.get('viewBox', node.attrs.get('viewbox', '')).split()[-2:] not in [[], ['24', '24']]
        if not large:
            return ''
        markup = serialize(node)
        for lower, proper in {
            'viewbox': 'viewBox', 'preserveaspectratio': 'preserveAspectRatio',
            'markerwidth': 'markerWidth', 'markerheight': 'markerHeight',
            'refx': 'refX', 'refy': 'refY', 'markerunits': 'markerUnits',
            'gradientunits': 'gradientUnits', 'gradienttransform': 'gradientTransform',
            'patternunits': 'patternUnits', 'patterncontentunits': 'patternContentUnits',
            'clippathunits': 'clipPathUnits', 'textlength': 'textLength', 'lengthadjust': 'lengthAdjust'
        }.items():
            markup = markup.replace(' ' + lower + '=', ' ' + proper + '=')
        for lower, proper in {'lineargradient': 'linearGradient', 'radialgradient': 'radialGradient', 'clippath': 'clipPath', 'textpath': 'textPath', 'foreignobject': 'foreignObject'}.items():
            markup = re.sub(r'(</?)' + lower + r'(?=[\s>])', lambda m: m[1] + proper, markup)
        markup = re.sub(r'(<svg\b[^>]*)(>)', lambda m: m[1] + (' xmlns="http://www.w3.org/2000/svg"' if 'xmlns=' not in m[1] else '') + m[2] + '<style>' + escape(self.style) + '</style>', markup, count=1)
        digest = hashlib.sha256(markup.encode()).hexdigest()
        path = self.dest / 'assets' / f'diagram-{digest[:12]}.svg'
        path.parent.mkdir(parents=True, exist_ok=True)
        if 'diagram:' + digest not in self.assets:
            path.write_text(markup)
            self.assets['diagram:' + digest] = {'path': path.relative_to(self.dest).as_posix(), 'sha256': digest}
        texts = [compact(n.text()) for n in node.all(lambda n: n.tag == 'text')]
        title = node.first(lambda n: n.tag == 'title')
        label = compact(title.text()) if title else node.attrs.get('aria-label', 'Lab model diagram')
        transcript = ' · '.join(dict.fromkeys(t for t in texts if t))
        return f'\n\n![{label}]({self.relative(path, output)})\n\n' + (f'**Diagram labels:** {transcript}\n\n' if transcript else '')

    def md(self, node, source, output):
        if isinstance(node, str):
            return re.sub(r'\s+', ' ', node)
        tag = node.tag
        if tag in OMIT or node.attrs.get('aria-hidden') == 'true' and tag != 'svg':
            return ''
        if node.attrs.get('id') in {'map-journey', 'map-step-copy', 'map-step-count', 'map-zoom-status', 'governance-focus-controls'}:
            return ''
        if any(node.has(c) for c in {'smap-toolbar', 'smap-legend', 'smap-display-controls', 'smap-view-controls'}):
            return ''
        if tag == 'noscript':
            return ''
        if tag == 'svg':
            return self.diagram(node, output)
        if node.has('company-brain-map'):
            return '\n\n## How the company brain connects\n\n' + '''```mermaid
flowchart TB
  people[People: intentions and review] --- state[Shared project state]
  agents[Agents: temporary sessions] --- state
  state --- knowledge[Knowledge: meanings and evidence]
  state --- work[Work: plans and attempts]
  state --- decisions[Decisions: review and change]
```

| Part | Its role |
| --- | --- |
| People | Express intentions, examine evidence and make decisions within their authority. |
| Agents | Recover checked context and ontology views, then act within separately established permission. |
| Knowledge | Preserve definitions, sources, observations and lessons with their meaning and limits. |
| Work | Connect bounded jobs and attempts to their results and evidence. |
| Decisions | Record authorized, exact changes within their scope. |

The connections above explain responsibilities. They do not declare new ontology relation kinds. Machine sessions are temporary; durable knowledge belongs to Project State.

'''
        anchor = f'\n\n<a id="{escape(node.attrs["id"], quote=True)}"></a>\n\n' if 'id' in node.attrs else ''
        content = self.children(node, source, output)
        if tag in {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
            return anchor + '\n\n' + '#' * int(tag[1]) + ' ' + compact(content) + '\n\n'
        if tag == 'a':
            href = self.link(node.attrs.get('href', ''), source, output)
            value = f'[{compact(content)}]({href})' if href and compact(content) else content
            if any(node.has(c) for c in {'chapter-card', 'next-essay', 'work-link'}):
                value = '\n\n' + value + '\n\n'
            return anchor + value
        if tag == 'img':
            path = (self.site / source).parent / node.attrs.get('src', '')
            if not path.is_file():
                return ''
            return '\n\n![' + node.attrs.get('alt', 'Illustration') + '](' + self.asset(path.resolve(), output) + ')\n\n'
        if tag == 'pre':
            code = node.first(lambda n: n.tag == 'code')
            raw = (code or node).text().strip('\n')
            classes = (code or node).attrs.get('class', '')
            language = re.search(r'language-([a-z0-9]+)', classes)
            lang = language[1] if language else ('json' if raw.strip().startswith(('{', '[')) else '')
            return anchor + '\n\n````' + lang + '\n' + raw + '\n````\n\n'
        if tag == 'code':
            return '`' + compact(node.text()).replace('`', '\\`') + '`'
        if tag in {'strong', 'b'}:
            return '**' + compact(content) + '**' if compact(content) else ''
        if tag in {'em', 'i'}:
            return '*' + compact(content) + '*'
        if tag == 'br':
            return '\n'
        if tag == 'table':
            rows = []
            for row in node.all(lambda n: n.tag == 'tr'):
                cells = [compact(self.children(c, source, output)).replace('|', '\\|') for c in row.children if isinstance(c, Node) and c.tag in {'th', 'td'}]
                if cells:
                    rows.append(cells)
            if not rows:
                return content
            width = max(map(len, rows))
            rows = [r + [''] * (width - len(r)) for r in rows]
            lines = ['| ' + ' | '.join(r) + ' |' for r in rows]
            lines.insert(1, '| ' + ' | '.join(['---'] * width) + ' |')
            return anchor + '\n\n' + '\n'.join(lines) + '\n\n'
        if tag in {'ul', 'ol'}:
            items = [c for c in node.children if isinstance(c, Node) and c.tag == 'li']
            lines = []
            for i, c in enumerate(items, 1):
                value = self.children(c, source, output).strip()
                lines.append((f'{i}. ' if tag == 'ol' else '- ') + value.replace('\n', '\n   '))
            return anchor + '\n\n' + '\n'.join(lines) + '\n\n'
        if tag == 'dt':
            return '\n\n**' + compact(content) + '**\n\n'
        if tag == 'dd':
            return content.strip() + '\n\n'
        if tag == 'summary':
            title = node.first(lambda n: n.has('catalog-title'))
            if title:
                badge = node.first(lambda n: n.has('badge'))
                return '\n\n## ' + compact(title.text()) + '\n\n' + (compact(self.children(badge, source, output)) + '\n\n' if badge else '')
            return '\n\n### ' + compact(content) + '\n\n'
        if tag == 'blockquote':
            return '\n\n' + '\n'.join('> ' + line for line in content.strip().splitlines()) + '\n\n'
        if tag in {'p', 'figure', 'figcaption', 'section', 'article', 'header', 'div', 'details', 'dl'}:
            return anchor + '\n\n' + content.strip() + '\n\n'
        return anchor + (' ' + content + ' ' if tag == 'span' else content)

    def build(self):
        for source, node, output, title in self.jobs:
            raw = self.md(node, source, output)
            raw = re.sub(r'\n[ \t]+\n', '\n\n', raw)
            raw = re.sub(r'\n{3,}', '\n\n', raw).strip()
            raw = raw.replace('Start with the whole system. Choose a view, then select a concept to read its explanation and connections.', 'Start with the whole system, then read the diagrams for governance, records, agents, evidence and learning below.')
            # A retained source statement contains an embedded Markdown link.
            # Rewrite its destination, leaving its text and JSON blocks intact.
            sections = re.split(r'(````.*?````)', raw, flags=re.S)
            for i in range(0, len(sections), 2):
                sections[i] = sections[i].replace('](DEFINITION-DRIFT-AUDIT.md)', '](' + self.relative(self.repo/'authority/definitions/DEFINITION-DRIFT-AUDIT.md', output) + ')')
                sections[i] = re.sub(r'(?<=\S)[ \t]{2,}(?=\S)', ' ', sections[i])
            raw = ''.join(sections)
            if title:
                raw = '# ' + title + '\n\n' + raw
            navigation = self.relative(self.dest / 'README.md', output)
            text = f'[Documentation home]({navigation})\n\n{raw}\n'
            path = self.dest / output
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        catalog = json.loads((self.site / 'research/catalog.json').read_text())
        records = []
        for group in ['definitions', 'artifact_types', 'relations', 'endpoints']:
            for record in catalog[group]:
                path = record.get('repository_path') or record.get('artifact_path') or record.get('instance_path') or record.get('path')
                digest = record.get('sha256') or record.get('artifact_sha256') or record.get('instance_sha256')
                if path:
                    live = self.repo / path
                    actual = hashlib.sha256(live.read_bytes()).hexdigest() if live.is_file() else None
                    records.append({'group': group, 'path': path, 'captured_sha256': digest, 'repository_sha256': actual, 'matches_capture': actual == digest if digest else None})
        reference = self.dest / 'reference'
        reference.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.site / 'research/catalog.json', reference / 'catalog-snapshot.json')
        manifest = {
            'schema_version': 'lab-documentation-import/v1', 'authority_effect': 'none',
            'imported_on': self.imported_on, 'catalog_captured_at': catalog['captured_at'],
            'catalog_counts': catalog['counts'],
            'pages': [{'source': source, 'output': output, 'source_sha256': self.source_hashes[source], 'output_sha256': hashlib.sha256((self.dest/output).read_bytes()).hexdigest()} for source, _, output, _ in self.jobs],
            'assets': list(self.assets.values()), 'record_sources': records,
            'source_standing_note': ('All digest-bearing catalog sources match the selected repository bytes at import time. This is content integrity, not admission or permanent standing.' if all(r['matches_capture'] is not False for r in records) else 'Some catalog sources differ from, or are unavailable in, the selected repository. Retained public snapshots preserve the captured edition; this import does not establish current repository standing.'),
            'source_comparison_counts': {'matching': sum(r['matches_capture'] is True for r in records), 'different': sum(r['matches_capture'] is False and r['repository_sha256'] is not None for r in records), 'unavailable': sum(r['repository_sha256'] is None for r in records)},
            'unresolved_links': sorted(self.unresolved),
            'scope': 'Markdown explanatory edition of reviewed documentation. No runtime execution, standing change, publication or admission.'
        }
        editorial_path = self.site / 'research/editorial-edition.json'
        if editorial_path.is_file():
            editorial = json.loads(editorial_path.read_text())
            manifest['editorial_edition'] = {key: editorial[key] for key in ['date', 'voice', 'editorial_copy_sha256']}
        (self.dest / 'IMPORT-MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
        print(json.dumps({'pages': len(self.jobs), 'assets': len(self.assets), 'unresolved_links': sorted(self.unresolved), 'changed_captured_sources': sum(r['matches_capture'] is False for r in records)}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', type=Path, required=True, help='Reviewed governance-lab-series directory')
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--imported-on', type=lambda value: date.fromisoformat(value).isoformat(),
                        default=None, help='Import date as YYYY-MM-DD; defaults to today')
    args = parser.parse_args()
    importer = Importer(args.site, args.repo, args.imported_on)
    for source, identifier, output in [
        ('start-here.html', 'start-here', 'start-here.md'),
        ('index.html', 'lab-home', 'company-brain.md'),
        ('research.html', 'research-lab', 'research-and-culture.md'),
        ('company-brain.html', 'company-brain', 'why-a-company-brain.md'),
        ('source-and-status.html', 'source-and-status', 'source-and-status.md'),
        ('research/reader-study.html', 'reader-study', 'research/reader-study.md'),
        ('incident-walkthrough.html', 'incident-walkthrough', 'tutorials/incident-walkthrough.md'),
        ('concept-comparisons.html', 'concept-comparisons', 'concepts/comparisons.md'),
        ('read-record.html', 'read-record', 'how-to/read-a-record.md'),
        ('prepare-incident-assessment.html', 'prepare-incident-assessment', 'how-to/prepare-incident-assessment.md'),
        ('prepare-definition.html', 'prepare-definition', 'how-to/prepare-definition.md'),
        ('resume-agent-work.html', 'resume-agent-work', 'how-to/resume-agent-work.md'),
        ('record-examples.html', 'record-examples', 'reference/record-examples.md'),
        ('governance-lab-reference.html', 'foundations', 'guide/introduction.md'),
        ('governance-lab-reference.html', 'system-map', 'guide/system-map.md'),
        ('lab-reference-library.html', 'library-reading-guide', 'reference/reading-the-library.md'),
        ('lab-reference-library.html', 'research', 'sources.md'),
        ('../craft-documentation-proposal/craft-model.html', None, 'craft/model.md')
    ]:
        importer.add(source, identifier, output)
    for identifier, filename, title in [
        ('governance', 'authority', 'Authority and meaning'),
        ('evidence', 'provenance', 'Provenance and evidence'),
        ('change', 'lifecycle', 'Lifecycle and admission'),
        ('purpose', 'intent-product-project', 'Intent, product and project'),
        ('records', 'records-and-connections', 'Definitions, records and connections'),
        ('agent', 'agents-and-memory', 'Agent work and memory'),
        ('learning', 'operational-learning', 'Operational learning'),
        ('today', 'operational-scope', 'Operational scope of the documentation snapshot')
    ]:
        importer.add('governance-lab-reference.html', identifier, f'guide/{filename}.md', title)
    # A deployment package contains rendered essays, without their draft TXT
    # inputs. Recover stable output names from each rendered article instead.
    library = importer.document('lab-reference-library.html')
    essays = library.root.all(lambda n: n.tag == 'article' and re.fullmatch(r'essay-\d+', n.attrs.get('id', '')))
    historical_inputs = sorted(args.site.glob('0*.txt'))
    for article in sorted(essays, key=lambda n: int(n.attrs['id'].split('-')[1])):
        number = int(article.attrs['id'].split('-')[1])
        name = article.attrs.get('data-source-name')
        if not name and number <= len(historical_inputs):
            name = historical_inputs[number - 1].name
        if not name or not re.fullmatch(r'\d{2}-[a-z0-9-]+\.txt', name):
            raise ValueError(f'Missing stable source name for {article.attrs["id"]}')
        importer.add('lab-reference-library.html', article.attrs['id'], f'essays/{Path(name).stem}.md')
    for identifier, filename, title in [
        ('catalog-definitions', 'definitions', 'Definitions'),
        ('catalog-types', 'artifact-types', 'Artifact Type contracts'),
        ('catalog-relations', 'relation-kinds', 'Declared relation kinds'),
        ('catalog-endpoints', 'endpoint-kinds', 'Declared endpoint kinds')
    ]:
        importer.add('lab-reference-library.html', identifier, f'reference/{filename}.md', title)
    record_manifest = args.site / 'research/reference-pages.json'
    if record_manifest.is_file():
        reference = json.loads(record_manifest.read_text())
        for record in reference['records']:
            output = f'reference/records/{record["id"]}.md'
            importer.add(record['href'], record['id'], output, record['title'])
            for identity, destination in reference['legacy_routes'].items():
                if destination == record['href']:
                    importer.routes[('lab-reference-library.html', identity)] = output
    runtime_manifest=args.site/'research/runtime-pages.json'
    documentation=json.loads((args.site/'research/documentation-manifest.json').read_text())
    if documentation.get('runtime_pages_manifest') and not runtime_manifest.is_file():raise ValueError('Selected runtime import descriptor missing from deployment')
    if runtime_manifest.is_file():
        runtime=json.loads(runtime_manifest.read_text())
        if runtime['schema_version']!='lab-runtime-site-pages/v1-candidate' or len(runtime['pages'])!=14:raise ValueError('Fourteen exact runtime import routes required')
        for page in runtime['pages']:
            importer.add(page['site_file'],page['article_id'],'runtime/'+page['markdown_route'])
    importer.routes[('governance-lab-reference.html', '')] = 'guide/README.md'
    importer.routes[('governance-lab-reference.html', 'start')] = 'guide/introduction.md'
    importer.routes[('governance-lab-series.html', '')] = 'guide/README.md'
    for (source, key), output in list(importer.routes.items()):
        if source == 'governance-lab-reference.html':
            importer.routes[('governance-lab-series.html', key)] = output
    importer.routes[('lab-reference-library.html', '')] = 'reference/README.md'
    importer.routes[('lab-reference-library.html', 'reference')] = 'reference/README.md'
    importer.routes[('lab-reference-library.html', 'library')] = 'reference/README.md'
    importer.routes[('lab-reference-library.html', 'articles-library')] = 'essays/README.md'
    importer.routes[('lab-reference-library.html', 'governance-model')] = 'essays/README.md'
    importer.routes[('lab-reference-library.html', 'lab-model')] = 'essays/README.md'
    if (args.site.parent / 'robot-learning-series/robot-learning-series.html').is_file():
        importer.add('../robot-learning-series/robot-learning-series.html', None, 'tutorials/robot-learning-series.md')
    importer.routes[('assets/kep/design-system.css', '')] = 'MAINTENANCE.md'
    importer.build()


if __name__ == '__main__':
    main()
