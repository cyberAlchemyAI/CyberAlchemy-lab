"""Narrative-owned text/table/code/diagram projection; no runtime imports."""
import html,hashlib,re,json
from pathlib import Path
TOKEN = re.compile(r"\[\[(source|page|concept):([a-z0-9-]+)\|([^\]]+)\]\]")
def sha(raw):return hashlib.sha256(raw).hexdigest()
def slug(text):return re.sub(r"[^a-z0-9]+","-",text.lower()).strip("-")
class Renderer:

    def __init__(self, narrative, sources, output):
        self.narrative = narrative
        self.sources = sources
        self.output = output
        self.pages = {p['key']: p for p in narrative['pages']}
        self.source_rows = sources['source_bindings']
        self.concepts = sources['canonical_concepts']
        self.outputs = []
        self.section_parity = []
        self.references = []

    def destination(self,kind,key,mode,page,parent):
        if mode!='fragment':raise ValueError('Site body projection requires fragment mode')
        if kind=='source':return self.output+self.source_rows[key]['original_path']
        if kind=='page':return self.pages[key]['site_file']
        filename,anchor=self.concepts[key][0].split('#',1)
        return Path(filename).name+'#'+anchor

    def inline(self, text, mode, page, parent):
        chunks = []
        cursor = 0
        for match in TOKEN.finditer(text):
            chunks.append(html.escape(text[cursor:match.start()]) if mode != 'markdown' else text[cursor:match.start()])
            kind, key, label = match.groups()
            destination = self.destination(kind, key, mode, page, parent)
            if mode == 'markdown':
                chunks.append('[' + label + '](' + destination + ')')
            else:
                chunks.append('<a href="' + html.escape(destination, quote=True) + '">' + html.escape(label) + '</a>')
            self.references.append({'page': page['key'], 'kind': kind, 'key': key, 'mode': mode, 'target': destination})
            cursor = match.end()
        chunks.append(html.escape(text[cursor:]) if mode != 'markdown' else text[cursor:])
        result = ''.join(chunks)
        if '[[' in result or '{{' in result:
            raise ValueError('Unresolved body token')
        return result

    def blocks(self, body, mode, page, parent):
        rendered = []
        for block in re.split('\\n\\s*\\n', body.strip()):
            command = re.fullmatch('\\{\\{CODE:([a-z0-9-]+)\\}\\}', block.strip())
            if command:
                code = self.narrative['code_blocks'][command.group(1)]
                if mode == 'markdown':
                    fence = chr(96) * 4
                    rendered.append(fence + 'bash\n' + code + '\n' + fence)
                else:
                    rendered.append('<pre><code class="language-bash">' + html.escape(code) + '</code></pre>')
                continue
            lines = block.splitlines()
            if block.startswith('|'):
                rows = [re.split('\\s+\\|\\s+', line.strip().strip('|').strip()) for line in lines]
                if len(rows) < 3 or not all((re.fullmatch(':?-+:?', item.strip()) for item in rows[1])):
                    raise ValueError('Malformed table')
                if len({len(row) for row in rows}) != 1:
                    raise ValueError('Unequal table columns')
                if mode == 'markdown':
                    rendered.append('\n'.join(('| ' + ' | '.join((self.inline(x, mode, page, parent) for x in row)) + ' |' for row in rows)))
                else:
                    heading = ''.join(('<th scope="col">' + self.inline(x, mode, page, parent) + '</th>' for x in rows[0]))
                    content = ''.join(('<tr>' + ''.join(('<td>' + self.inline(x, mode, page, parent) + '</td>' for x in row)) + '</tr>' for row in rows[2:]))
                    rendered.append('<div class="table-wrap"><table><thead><tr>' + heading + '</tr></thead><tbody>' + content + '</tbody></table></div>')
            elif all((line.startswith('- ') for line in lines)):
                if mode == 'markdown':
                    rendered.append('\n'.join(('- ' + self.inline(line[2:], mode, page, parent) for line in lines)))
                else:
                    rendered.append('<ul>' + ''.join(('<li>' + self.inline(line[2:], mode, page, parent) + '</li>' for line in lines)) + '</ul>')
            else:
                prose = ' '.join(lines)
                rendered.append(self.inline(prose, mode, page, parent) if mode == 'markdown' else '<p>' + self.inline(prose, mode, page, parent) + '</p>')
        return '\n\n'.join(rendered)

    def diagram(self, diagram, mode, page, parent):
        if mode == 'markdown':
            fence = chr(96) * 4
            return fence + 'mermaid\n' + diagram['code'] + '\n' + fence + '\n\n' + diagram['alternative'] + '\n\n' + diagram['meaning']
        return '<figure id="' + html.escape(diagram['id']) + '"><pre><code class="language-mermaid">' + html.escape(diagram['code']) + '</code></pre><figcaption>' + html.escape(diagram['alternative']) + '</figcaption><p>' + html.escape(diagram['meaning']) + '</p></figure>'

    def body(self, page, mode, parent):
        out = []
        if mode == 'markdown':
            out = ['# ' + page['title'], page['description'], 'Draft prepared on 2026-10-14. Integration and final T21 qualification remain pending.']
        else:
            out = ['<header class="start-masthead"><p class="eyebrow">Lab runtime · proposed documentation</p><h1>' + html.escape(page['title']) + '</h1><p>' + html.escape(page['description']) + '</p><p class="source-note">Draft prepared on 2026-10-14. Integration and final T21 qualification remain pending.</p></header>']
        sources_used = set()
        for section in page['sections']:
            sid = page['article_id'] + '-' + slug(section['title'])
            if mode == 'markdown':
                out.append('## ' + section['title'])
            else:
                out.append('<section id="' + sid + '" aria-labelledby="' + sid + '-title"><h2 id="' + sid + '-title">' + html.escape(section['title']) + '</h2>')
            out.append(self.blocks(section['body'], mode, page, parent))
            sources_used.update((m.group(2) for m in TOKEN.finditer(section['body']) if m.group(1) == 'source'))
            if section['diagram']:
                sources_used.update(section['diagram']['evidence'])
                out.append(self.diagram(section['diagram'], mode, page, parent))
            if mode != 'markdown':
                out.append('</section>')
            self.section_parity.append({'page': page['key'], 'section_id': sid, 'mode': mode, 'body_sha256': sha(section['body'].encode()), 'diagram_sha256': sha(json.dumps(section['diagram'], sort_keys=True).encode()) if section['diagram'] else None})
        if mode == 'markdown':
            out.append('## Selected public evidence')
        else:
            out.append('<section class="source-notes" id="' + page['article_id'] + '-sources"><h2>Selected public evidence</h2><ul>')
        for key in sorted(sources_used):
            row = self.source_rows[key]
            label = row['original_path']
            destination = self.destination('source', key, mode, page, parent)
            detail = 'SHA-256 ' + row['sha256'] + '; ' + str(row['size_bytes']) + ' bytes. Public technical snapshot; no authority transfer.'
            if mode == 'markdown':
                out.append('- [' + label + '](' + destination + '). ' + detail)
            else:
                out.append('<li><a href="' + html.escape(destination, quote=True) + '">' + html.escape(label) + '</a>. ' + html.escape(detail) + '</li>')
        if mode != 'markdown':
            out.append('</ul></section>')
        return '\n\n'.join(out)
