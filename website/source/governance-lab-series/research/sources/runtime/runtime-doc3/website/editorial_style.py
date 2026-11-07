"""Apply approved explanatory prose while retaining records and inline references."""
from html import escape, unescape
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parent
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


def normalize(value):
    return re.sub(r'\s+([.,:;!?])', r'\1', re.sub(r'\s+', ' ', value).strip())


class Paragraphs(HTMLParser):
    def __init__(self, raw):
        super().__init__(convert_charrefs=True)
        self.raw = raw
        self.offsets = [0]
        self.offsets += [match.end() for match in re.finditer('\n', raw)]
        self.paragraphs = []
        self.current = None
        self.stack = []
        self.feed(raw)

    def position(self):
        line, column = self.getpos()
        return self.offsets[line - 1] + column

    def handle_starttag(self, tag, attrs):
        classes = {part for _, values in self.stack for part in values.get('class', '').split()}
        if tag == 'p' and self.current is None:
            protected = 'record-body' in classes and 'reference-aid' not in classes
            self.current = {'start': self.position() + len(self.get_starttag_text()), 'text': [], 'protected': protected}
        if tag not in VOID:
            self.stack.append((tag, dict(attrs)))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_data(self, text):
        if self.current is not None:
            self.current['text'].append(text)

    def handle_endtag(self, tag):
        if tag == 'p' and self.current is not None:
            self.current['end'] = self.position()
            self.current['key'] = normalize(' '.join(self.current['text']))
            self.paragraphs.append(self.current)
            self.current = None
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                self.stack = self.stack[:index]
                break


def preserve_markup(original, replacement, link_labels=None):
    result = '<br><br>'.join(escape(part) for part in replacement.split('\n\n'))
    retained = []
    link_labels = link_labels or {}
    for match in re.finditer(r'<(a|strong|code|em)\b[^>]*>.*?</\1>', original, re.S):
        markup = match.group()
        text = normalize(unescape(re.sub('<[^>]+>', '', markup)))
        if match.group(1) == 'a':
            label = escape(link_labels.get(text, text))
            occurrence = re.search(re.escape(label), result, re.I) if label else None
            if occurrence:
                opening = re.match(r'<a\b[^>]*>', markup).group()
                linked = opening + occurrence.group() + '</a>'
                result = result[:occurrence.start()] + linked + result[occurrence.end():]
            else:
                retained.append(markup)
            continue
        needle = escape(text)
        if needle and needle in result:
            result = result.replace(needle, markup, 1)
    if retained:
        result += ' ' + ' · '.join(retained)
    # Retain inner anchor identities even when their wording changes.
    for identity in re.findall(r'\bid="([^"]+)"', original):
        if f'id="{identity}"' not in result:
            result += f'<span id="{escape(identity)}"></span>'
    return result


def apply(stage):
    # Use the renderer's parser for the same content boundaries as maintenance.
    sys.path.insert(0, str(stage / 'governance-lab-series'))
    from build_site_search import Document, clean

    def normative_text(node):
        if node.has_class('reference-aid'):
            return ''
        return ' '.join(normative_text(child) if hasattr(child, 'tag') else child for child in node.children)

    def fingerprints(document, predicate, normative=False):
        return [hashlib.sha256((clean(normative_text(node)) if normative else node.text()).encode()).hexdigest()
                for node in document.root.all(predicate)]

    corpus = json.loads((ROOT / 'editorial-copy.json').read_text())
    groups = {}
    for entry in corpus['entries']:
        group = groups.setdefault(entry['page'], {})
        key = normalize(entry['original'])
        if key in group and group[key]['editorial'] != entry['editorial']:
            raise ValueError(f'Conflicting editorial passages: {entry["page"]}: {key}')
        group[key] = entry
    receipt = {'voice': corpus['voice'], 'date': corpus['date'],
               'editorial_copy_sha256': hashlib.sha256((ROOT / 'editorial-copy.json').read_bytes()).hexdigest(),
               'authority_effect': 'none', 'pages': {}, 'unmatched': []}
    for name, edits in groups.items():
        targets = [name]
        if name == 'governance-lab-series/governance-lab-reference.html':
            targets.append('governance-lab-series/governance-lab-series.html')
        matches = set()
        for target in targets:
            path = stage / target
            raw = path.read_text(encoding='utf-8')
            original_document = Document(raw)
            parsed = Paragraphs(raw)
            replacements = []
            for paragraph in parsed.paragraphs:
                key = paragraph['key']
                if key in edits and not paragraph['protected']:
                    matches.add(key)
                    inner = raw[paragraph['start']:paragraph['end']]
                    entry = edits[key]
                    replacements.append((paragraph['start'], paragraph['end'], preserve_markup(
                        inner, entry['editorial'], entry.get('link_labels'))))
            for start, end, replacement in reversed(replacements):
                raw = raw[:start] + replacement + raw[end:]
            revised_document = Document(raw)
            for label, predicate in [
                ('code blocks', lambda n: n.tag == 'pre'),
                ('quotations', lambda n: n.tag == 'blockquote'),
                ('formal definition cards', lambda n: n.has_class('definition-core')),
            ]:
                if fingerprints(original_document, predicate) != fingerprints(revised_document, predicate):
                    raise ValueError(f'Editorial revision changed {label}: {target}')
            path.write_text(raw, encoding='utf-8')
            receipt['pages'][target] = {'changed_passages': len(replacements), 'sha256': hashlib.sha256(raw.encode()).hexdigest()}
        receipt['unmatched'] += [{'page': name, 'original': key} for key in edits if key not in matches]
    if receipt['unmatched']:
        raise ValueError('Editorial source changed: ' + json.dumps(receipt['unmatched'][:4], ensure_ascii=False))
    library = Document((stage / 'governance-lab-series/lab-reference-library.html').read_text())
    baseline = json.loads((stage / 'governance-lab-series/research/preservation-baseline.json').read_text())
    bodies = fingerprints(library, lambda n: n.has_class('record-body'), normative=True)
    if bodies != baseline['reference bodies excluding explanatory reading aids']:
        raise ValueError('Editorial revision changed captured reference record bodies')
    receipt['preserved_reference_bodies'] = len(bodies)
    receipt['expanded_essay_fingerprints'] = fingerprints(
        library, lambda n: n.tag == 'article' and n.attrs.get('id', '').startswith('essay-'), normative=True)
    receipt['preservation'] = 'Captured record bodies, code blocks, quotations and formal definition cards retain their wording.'
    (stage / 'governance-lab-series/research/editorial-edition.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'editorial_pages': len(receipt['pages']), 'changed_passages': sum(v['changed_passages'] for v in receipt['pages'].values())}))
    return receipt


if __name__ == '__main__':
    apply(Path(sys.argv[1]).resolve())
