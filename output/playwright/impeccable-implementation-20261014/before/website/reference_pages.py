"""Split exact records into static pages, with byte-independent wording checks.

The original complete library reaches the editorial preservation check first.
This step then compares every record by identity after moving it. Legacy links
are routed before parsing the catalog. No fetch is required for file:// use.
"""
from html import escape
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit, unquote


def split(stage):
    lab = stage / 'governance-lab-series'
    sys.path.insert(0, str(lab))
    from build_site_search import Document, Node, VOID, clean

    def serialize(node):
        if isinstance(node, str):
            return escape(node, quote=False)
        if not node.tag:
            return ''.join(serialize(child) for child in node.children)
        attrs = ''.join(' ' + key + ('' if value is None else '="' + escape(value, quote=True) + '"') for key, value in node.attrs.items())
        if node.tag in VOID:
            return f'<{node.tag}{attrs}>'
        contents = ''.join(child if isinstance(child, str) else serialize(child) for child in node.children) if node.tag in {'script', 'style'} else ''.join(serialize(child) for child in node.children)
        return f'<{node.tag}{attrs}>{contents}</{node.tag}>'

    def normative(node):
        if node.has_class('reference-aid'):
            return ''
        return ' '.join(normative(child) if isinstance(child, Node) else child for child in node.children)

    def digest(node):
        return hashlib.sha256(clean(normative(node)).encode()).hexdigest()

    page_path = lab / 'lab-reference-library.html'
    document = Document(page_path.read_text())
    rows = document.root.all(lambda node: node.has_class('catalog-item'))
    route_map, records, full_text = {}, [], {}
    for row in rows:
        identity = row.attrs['id']
        destination = f'reference/{identity}.html'
        body = row.first(lambda node: node.has_class('record-body'))
        for node in row.all(lambda node: 'id' in node.attrs):
            route_map[node.attrs['id']] = destination
        panel = row.parent
        while panel and not panel.has_class('catalog-panel'):
            panel = panel.parent
        title = row.first(lambda node: node.has_class('catalog-title')).text().strip()
        records.append({'id': identity, 'href': destination, 'title': title,
                        'catalog': panel.attrs['id'], 'body_sha256': digest(body)})
        full_text[identity] = row.attrs.get('data-search', clean(body.text()).lower())

    def rebase(node, origin, destination):
        for child in node.all(lambda node: True):
            for attr in ('href', 'src', 'data'):
                value = child.attrs.get(attr)
                if not value:
                    continue
                parts = urlsplit(value)
                if parts.scheme or parts.netloc:
                    continue
                target = (origin.parent / unquote(parts.path)).resolve() if parts.path else origin
                if target == page_path and parts.fragment in route_map:
                    target = lab / route_map[parts.fragment]
                relative = Path(os.path.relpath(target, destination.parent)).as_posix()
                child.attrs[attr] = relative + ('?' + parts.query if parts.query else '') + ('#' + parts.fragment if parts.fragment else '')

    output = lab / 'reference'
    output.mkdir(exist_ok=True)
    before, after = [], []
    source_consumers = {}
    catalog_labels = {
        'library-reading-guide': 'How to use the library',
        'catalog-definitions': 'Definitions',
        'catalog-types': 'Record formats',
        'catalog-relations': 'Connection rules',
        'catalog-endpoints': 'Endpoint kinds',
        'catalog-history': 'Versions and record facets',
    }
    for record, row in zip(records, rows):
        identity, name = record['id'], record['href']
        destination = lab / name
        body = row.first(lambda node: node.has_class('record-body'))
        before.append(digest(body))
        moved = Document(serialize(body)).root.first(lambda node: node.has_class('record-body'))
        rebase(moved, page_path, destination)
        for heading in moved.all(lambda node: node.tag == 'h4'):
            heading.tag='h2'
        for index, code in enumerate(moved.all(lambda node: node.tag == 'pre'),1):
            code.attrs.update({'tabindex':'0','role':'region','aria-label':record['title']+' code block '+str(index)})
        # Formal details stay intact. Their initial disclosure is presentation.
        first_detail = moved.first(lambda node: node.tag == 'details')
        if first_detail:
            first_detail.attrs['open'] = None
        # Section IDs and outline labels are presentation; exact body text stays
        # inside the existing preservation comparison below.
        outline = [(identity, 'Overview')]
        for node in moved.all(lambda node: node.tag in {'h2', 'details'}):
            target = node.first(lambda child: child.tag == 'summary') if node.tag == 'details' else node
            if not target:
                continue
            label = clean(target.text())
            if not label:
                continue
            target.attrs.setdefault('id', f'{identity}-section-{len(outline)}')
            outline.append((target.attrs['id'], label))
        head = Document(serialize(document.root.first(lambda node: node.tag == 'head'))).root.first(lambda node: node.tag == 'head')
        head.children = [node for node in head.children if not isinstance(node, Node) or not (
            node.tag == 'script' and any(key in node.attrs.get('src', '') for key in ('reference-library.js', 'lab-library-docs.js', 'docs-startup.js'))
            or node.tag == 'link' and node.attrs.get('rel') == 'canonical')]
        head.first(lambda node: node.tag == 'title').children = [record['title'] + ' · Lab reference']
        if not head.first(lambda node: node.tag == 'link' and node.attrs.get('href', '').endswith('reference-record-page.css')):
            head.children.append(Node('link', {'rel': 'stylesheet', 'href': 'assets/reference-record-page.css'}))
        head.children.append(Node('script', {'src': 'assets/reference-record-page.js', 'defer': None}))
        rebase(head, page_path, destination)
        header = Document(serialize(document.root.first(lambda node: node.tag == 'header' and node.has_class('topbar')))).root.first(lambda node: node.tag == 'header')
        rebase(header, page_path, destination)
        for link in header.first(lambda node: node.tag == 'nav').all(lambda node: node.tag == 'a'):
            if link.attrs.get('href', '').split('#')[0] == '../lab-reference-library.html':
                link.attrs['aria-current'] = 'page'
            else:
                link.attrs.pop('aria-current', None)
        catalog = record['catalog']
        catalog_label = catalog_labels[catalog]
        catalog_links = ''.join(
            f'<a data-library-route="{key}" href="../lab-reference-library.html#{key}"'
            + (' aria-current="location"' if key == catalog else '')
            + f'>{escape(label)}</a>' for key, label in catalog_labels.items())
        sidebar = f'''<aside class="article-tree" aria-label="Documentation navigation"><details class="article-contents"><summary>Browse documentation</summary><nav aria-label="Documentation navigation"><a href="../start-here.html">Start here</a><a href="../governance-lab-reference.html#start">Lab overview</a><a href="../lab-reference-library.html#reference">Reference library</a>{catalog_links}<a href="../lab-reference-library.html#articles-library">Expanded essays</a></nav></details></aside>'''
        outline_links = ''.join(f'<a href="#{escape(key, quote=True)}">{escape(label)}</a>' for key, label in outline)
        toc = f'''<aside class="docs-local-nav" aria-label="On this page"><details class="docs-toc"><summary>On this page</summary><nav aria-label="Headings on this page">{outline_links}</nav></details></aside>'''
        footer = document.root.first(lambda node: node.tag == 'footer')
        if footer:
            footer = Document(serialize(footer)).root.first(lambda node: node.tag == 'footer')
            rebase(footer, page_path, destination)
        title = escape(record['title'])
        html = f'''<!doctype html><html lang="en">{serialize(head)}<body data-edition="reference" data-docs-enhanced="record" data-record-catalog="{catalog}"><a class="skip-link" href="#{identity}">Skip to the record</a>{serialize(header)}<main class="docs-record-layout">{sidebar}<article class="record-page" id="{identity}" tabindex="-1"><header class="docs-topic-header"><p class="docs-breadcrumb"><a href="../lab-reference-library.html#reference">Reference</a> / <a href="../lab-reference-library.html#{catalog}">{escape(catalog_label)}</a> / {title}</p><h1>{title}</h1></header>{serialize(moved)}<p class="record-return"><a href="../lab-reference-library.html#{catalog}">Return to {escape(catalog_label)}</a></p></article>{toc}</main>{serialize(footer) if footer else ''}</body></html>\n'''
        destination.write_text(html, encoding='utf-8')
        leaf = Document(html)
        for node in leaf.root.all(lambda node: node.tag == 'a'):
            href = node.attrs.get('href', '').split('#')[0]
            if href.startswith('../'):
                source_consumers.setdefault(href[3:], set()).add(name)
        after.append(digest(leaf.root.first(lambda node: node.has_class('record-body'))))
        summary = row.first(lambda node: node.tag == 'summary')
        intro = body.first(lambda node: node.has_class('reader-intro'))
        ref = body.first(lambda node: node.has_class('record-id'))
        preview = '<div class="catalog-preview">' + (serialize(intro) if intro else '')
        if ref:
            preview += '<p class="catalog-identity">' + escape(clean(ref.text())) + '</p>'
        preview += f'<p><a class="record-link" href="{name}#{identity}">Read the complete {title} record <span aria-hidden="true">→</span></a></p></div>'
        compact = Document(preview).root.first(lambda node: node.has_class('catalog-preview'))
        row.children = [summary, compact]
        row.attrs['data-search'] = clean(row.text()).lower()
        compact.parent = row

    baseline = json.loads((lab / 'research/preservation-baseline.json').read_text())['reference bodies excluding explanatory reading aids']
    if before != baseline or after != baseline or len(records) != 454:
        raise ValueError('Moving reference records changed protected wording or coverage.')
    # Resolve a legacy record URL before requesting the catalog's styles and
    # enhancement scripts, rather than starting them and aborting on redirect.
    library_head=document.root.first(lambda node: node.tag == 'head')
    charset_index=next((i+1 for i,node in enumerate(library_head.children) if isinstance(node,Node) and node.tag=='meta' and 'charset' in node.attrs),0)
    library_head.children.insert(charset_index,Node('script', {'src': 'assets/reference-routes.js'}))
    page_path.write_text('<!doctype html>\n' + serialize(document.root), encoding='utf-8')
    routes = '/* Generated static record routes. */\n(() => {const routes=' + json.dumps(route_map, separators=(',', ':')) + ';const base=new URL("../",document.currentScript.src);let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{return;}if(routes[id]){const target=new URL(routes[id],base);target.search=location.search;target.hash=id;location.replace(target.href);}})();\n'
    (lab / 'assets/reference-routes.js').write_text(routes)
    from compressed_script import write_payload
    search_delivery=write_payload(lab / 'assets/reference-search-data.js','LabReferenceSearchText',full_text)
    metadata = {'authority_effect': 'none', 'records': records, 'legacy_routes': route_map,
                'preserved_bodies': len(after), 'search_delivery':search_delivery,
                'preservation': 'Identity-ordered equality with the original 454-body baseline.'}
    (lab / 'research/reference-pages.json').write_text(json.dumps(metadata, indent=2) + '\n')
    manifest_path = lab / 'research/documentation-manifest.json'
    manifest = json.loads(manifest_path.read_text())
    manifest['html_files'] += [record['href'] for record in records]
    for binding in manifest['bindings']:
        binding['affected_pages'] = sorted(set(binding['affected_pages']) | source_consumers.get(binding['source'], set()))
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'reference_pages': len(records), 'protected_bodies_preserved': len(after), 'catalog_bytes': page_path.stat().st_size}))
    return metadata
