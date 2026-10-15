"""Owned stdlib dual renderer. Never imports Lab or writes outside this package."""
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[6]
TOKEN = re.compile(r"\[\[(source|page|concept):([a-z0-9-]+)\|([^\]]+)\]\]")

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def read_selected(path, expected):
    path = Path(path)
    if not path.is_file() or path.is_symlink() or any(p.is_symlink() for p in path.parents):
        raise ValueError("Unselected or symbolic input")
    raw = path.read_bytes()
    if sha(raw) != expected:
        raise ValueError("Input digest mismatch")
    return raw

def write_new(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(raw)

def relative(target, parent):
    return Path(os.path.relpath(target, parent)).as_posix()

def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

class Renderer:
    def __init__(self, narrative, sources, output):
        self.narrative = narrative
        self.sources = sources
        self.output = output
        self.pages = {p["key"]: p for p in narrative["pages"]}
        self.source_rows = sources["source_bindings"]
        self.concepts = sources["canonical_concepts"]
        self.outputs = []
        self.section_parity = []
        self.references = []

    def paths(self, page):
        return {
            "fragment": self.output / "proposed/website/source/governance-lab-series/runtime/templates" / (page["site_file"] + ".in"),
            "preview": self.output / "preview/governance-lab-series" / page["site_file"],
            "markdown": self.output / "markdown/docs/lab/runtime" / page["markdown_route"],
        }

    def destination(self, kind, key, mode, page, parent):
        if kind == "source":
            row = self.source_rows[key]
            if mode == "fragment":
                return "research/sources/" + row["original_path"]
            return relative(ROOT / row["snapshot_path"], parent)
        if kind == "page":
            target = self.pages[key]
            if mode == "fragment":
                return target["site_file"]
            return relative(self.paths(target)[mode], parent)
        canonical_html, canonical_md = self.concepts[key]
        if mode == "markdown":
            return relative(ROOT / canonical_md, parent)
        filename, anchor = canonical_html.split("#", 1)
        if mode == "fragment":
            return Path(filename).name + "#" + anchor
        return relative(ROOT / filename, parent) + "#" + anchor

    def inline(self, text, mode, page, parent):
        chunks = []
        cursor = 0
        for match in TOKEN.finditer(text):
            chunks.append(html.escape(text[cursor:match.start()]) if mode != "markdown" else text[cursor:match.start()])
            kind, key, label = match.groups()
            destination = self.destination(kind, key, mode, page, parent)
            if mode == "markdown":
                chunks.append("[" + label + "](" + destination + ")")
            else:
                chunks.append('<a href="' + html.escape(destination, quote=True) + '">' + html.escape(label) + "</a>")
            self.references.append({"page": page["key"], "kind": kind, "key": key, "mode": mode, "target": destination})
            cursor = match.end()
        chunks.append(html.escape(text[cursor:]) if mode != "markdown" else text[cursor:])
        result = "".join(chunks)
        if "[[" in result or "{{" in result:
            raise ValueError("Unresolved body token")
        return result

    def blocks(self, body, mode, page, parent):
        rendered = []
        for block in re.split(r"\n\s*\n", body.strip()):
            command = re.fullmatch(r"\{\{CODE:([a-z0-9-]+)\}\}", block.strip())
            if command:
                code = self.narrative["code_blocks"][command.group(1)]
                if mode == "markdown":
                    fence = chr(96) * 4
                    rendered.append(fence + "bash\n" + code + "\n" + fence)
                else:
                    rendered.append('<pre><code class="language-bash">' + html.escape(code) + "</code></pre>")
                continue
            lines = block.splitlines()
            if block.startswith("|"):
                rows = [re.split(r"\s+\|\s+", line.strip().strip("|").strip()) for line in lines]
                if len(rows) < 3 or not all(re.fullmatch(r":?-+:?", item.strip()) for item in rows[1]):
                    raise ValueError("Malformed table")
                if len({len(row) for row in rows}) != 1:
                    raise ValueError("Unequal table columns")
                if mode == "markdown":
                    rendered.append("\n".join("| " + " | ".join(self.inline(x, mode, page, parent) for x in row) + " |" for row in rows))
                else:
                    heading = "".join("<th scope=\"col\">" + self.inline(x, mode, page, parent) + "</th>" for x in rows[0])
                    content = "".join("<tr>" + "".join("<td>" + self.inline(x, mode, page, parent) + "</td>" for x in row) + "</tr>" for row in rows[2:])
                    rendered.append('<div class="table-wrap"><table><thead><tr>' + heading + "</tr></thead><tbody>" + content + "</tbody></table></div>")
            elif all(line.startswith("- ") for line in lines):
                if mode == "markdown":
                    rendered.append("\n".join("- " + self.inline(line[2:], mode, page, parent) for line in lines))
                else:
                    rendered.append("<ul>" + "".join("<li>" + self.inline(line[2:], mode, page, parent) + "</li>" for line in lines) + "</ul>")
            else:
                prose = " ".join(lines)
                rendered.append(self.inline(prose, mode, page, parent) if mode == "markdown" else "<p>" + self.inline(prose, mode, page, parent) + "</p>")
        return "\n\n".join(rendered)

    def diagram(self, diagram, mode, page, parent):
        if mode == "markdown":
            fence = chr(96) * 4
            return fence + "mermaid\n" + diagram["code"] + "\n" + fence + "\n\n" + diagram["alternative"] + "\n\n" + diagram["meaning"]
        return '<figure id="' + html.escape(diagram["id"]) + '"><pre><code class="language-mermaid">' + html.escape(diagram["code"]) + "</code></pre><figcaption>" + html.escape(diagram["alternative"]) + "</figcaption><p>" + html.escape(diagram["meaning"]) + "</p></figure>"

    def body(self, page, mode, parent):
        out = []
        if mode == "markdown":
            out = ["# " + page["title"], page["description"], "Draft prepared on 2026-10-14. Integration and final T21 qualification remain pending."]
        else:
            out = ['<header class="start-masthead"><p class="eyebrow">Lab runtime · proposed documentation</p><h1>' + html.escape(page["title"]) + "</h1><p>" + html.escape(page["description"]) + '</p><p class="source-note">Draft prepared on 2026-10-14. Integration and final T21 qualification remain pending.</p></header>']
        sources_used = set()
        for section in page["sections"]:
            sid = page["article_id"] + "-" + slug(section["title"])
            if mode == "markdown":
                out.append("## " + section["title"])
            else:
                out.append('<section id="' + sid + '" aria-labelledby="' + sid + '-title"><h2 id="' + sid + '-title">' + html.escape(section["title"]) + "</h2>")
            out.append(self.blocks(section["body"], mode, page, parent))
            sources_used.update(m.group(2) for m in TOKEN.finditer(section["body"]) if m.group(1) == "source")
            if section["diagram"]:
                sources_used.update(section["diagram"]["evidence"])
                out.append(self.diagram(section["diagram"], mode, page, parent))
            if mode != "markdown":
                out.append("</section>")
            self.section_parity.append({"page": page["key"], "section_id": sid, "mode": mode,
                "body_sha256": sha(section["body"].encode()),
                "diagram_sha256": sha(json.dumps(section["diagram"], sort_keys=True).encode()) if section["diagram"] else None})
        if mode == "markdown":
            out.append("## Selected public evidence")
        else:
            out.append('<section class="source-notes" id="' + page["article_id"] + '-sources"><h2>Selected public evidence</h2><ul>')
        for key in sorted(sources_used):
            row = self.source_rows[key]
            label = row["original_path"]
            destination = self.destination("source", key, mode, page, parent)
            detail = "SHA-256 " + row["sha256"] + "; " + str(row["size_bytes"]) + " bytes. Public technical snapshot; no authority transfer."
            if mode == "markdown":
                out.append("- [" + label + "](" + destination + "). " + detail)
            else:
                out.append('<li><a href="' + html.escape(destination, quote=True) + '">' + html.escape(label) + "</a>. " + html.escape(detail) + "</li>")
        if mode != "markdown":
            out.append("</ul></section>")
        return "\n\n".join(out)

    def preview_shell(self, shell, page, body):
        filename = self.paths(page)["preview"]
        shell = re.sub(r"<title>.*?</title>", "<title>" + html.escape(page["title"]) + " · CyberAlchemy Lab</title>", shell, count=1, flags=re.S)
        shell = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + html.escape(page["description"], quote=True) + m.group(2), shell, count=1)
        shell = shell.replace('data-site-start aria-current="page"', "data-site-start")
        shell = shell.replace('href="#start-here"', 'href="#' + page["article_id"] + '"')
        # Resolve existing shell navigation/assets against its maintained site directory.
        def shell_url(match):
            attribute, url = match.groups()
            if url.startswith(("#", "http:", "https:", "mailto:", "data:")):
                return match.group(0)
            target, separator, anchor = url.partition("#")
            actual = ROOT / "website/source/governance-lab-series" / target
            return attribute + '="' + relative(actual.resolve(), filename.parent) + (separator + anchor if separator else "") + '"'
        shell = re.sub(r'(href|src)="([^"]+)"', shell_url, shell)
        shell, count = re.subn(r'<article id="start-here" class="start-content" tabindex="-1">.*?</article>',
            '<article id="' + page["article_id"] + '" class="start-content" tabindex="-1">' + body + "</article>", shell, count=1, flags=re.S)
        if count != 1:
            raise ValueError("Shared article shell changed")
        toc = "".join('<a href="#' + page["article_id"] + "-" + slug(s["title"]) + '">' + html.escape(s["title"]) + "</a>" for s in page["sections"])
        shell, count = re.subn(r'(<details class="docs-toc" id="start-toc">.*?<nav aria-label="Headings on this page">).*?(</nav>)',
            lambda m: m.group(1) + toc + m.group(2), shell, count=1, flags=re.S)
        if count != 1:
            raise ValueError("Shared contents shell changed")
        shell = shell.replace("{{READING_TIME}}", str(max(1, round(sum(len(s["body"].split()) for s in page["sections"]) / 220))) + " min")
        shell = shell.replace('href="#start-content"', 'href="#' + page["article_id"] + '"')
        if "{{" in shell:
            raise ValueError("Unresolved shared shell field")
        return shell

    def emit(self, path, text):
        raw = (text.rstrip() + "\n").encode()
        write_new(path, raw)
        self.outputs.append({"path": path.relative_to(self.output).as_posix(), "sha256": sha(raw), "size_bytes": len(raw)})

    def run(self, shell):
        for page in self.pages.values():
            paths = self.paths(page)
            fragment = self.body(page, "fragment", paths["fragment"].parent)
            self.emit(paths["fragment"], fragment)
            preview_body = self.body(page, "preview", paths["preview"].parent)
            self.emit(paths["preview"], self.preview_shell(shell, page, preview_body))
            self.emit(paths["markdown"], self.body(page, "markdown", paths["markdown"].parent))
        routes = [{"site_source": p["site_file"], "article_id": p["article_id"],
            "markdown_destination": "docs/lab/runtime/" + p["markdown_route"], "title": p["title"]} for p in self.pages.values()]
        self.emit(self.output / "import-routes.json", json.dumps({"routes": routes, "applied": False}, indent=2, sort_keys=True))
        return {"schema_version": "lab-T21-runtime-render/v1-candidate", "pages": len(self.pages),
            "diagrams": sum(bool(s["diagram"]) for p in self.pages.values() for s in p["sections"]),
            "outputs": self.outputs, "section_parity": self.section_parity, "reference_bindings": self.references,
            "shared_site_mutated": False, "runtime_executed": False, "task_complete": False,
            "claim_ceiling": "Owned dual rendering only. Shared build/editorial/search/import/setup/current runtime qualification remain pending."}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--narrative-sha256", required=True)
    parser.add_argument("--source-map-sha256", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = (HERE / args.output).resolve()
    if output.parent != HERE or output.exists():
        raise ValueError("Output must be a new direct owned child")
    narrative_raw = read_selected(HERE / "narrative.json", args.narrative_sha256)
    source_raw = read_selected(HERE / "source-map.json", args.source_map_sha256)
    narrative, sources = json.loads(narrative_raw), json.loads(source_raw)
    if len(narrative["pages"]) != 14 or len({p["markdown_route"] for p in narrative["pages"]}) != 14:
        raise ValueError("Fourteen distinct routes required")
    for row in sources["source_bindings"].values():
        raw = read_selected(ROOT / row["snapshot_path"], row["sha256"])
        if len(raw) != row["size_bytes"]:
            raise ValueError("Input length mismatch")
    shell_row = sources["source_bindings"]["site-shell"]
    shell = read_selected(ROOT / shell_row["snapshot_path"], shell_row["sha256"]).decode()
    report = Renderer(narrative, sources, output).run(shell)
    report["narrative_sha256"] = sha(narrative_raw)
    report["source_map_sha256"] = sha(source_raw)
    write_new(output / "render-receipt.json", (json.dumps(report, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"result": "PASS-owned-dual-render", "pages": report["pages"], "diagrams": report["diagrams"],
        "outputs": len(report["outputs"]), "runtime_executed": False}))

if __name__ == "__main__":
    main()
