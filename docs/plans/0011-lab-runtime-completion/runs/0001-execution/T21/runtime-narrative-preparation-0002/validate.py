"""Public owned rendering checks; no Lab imports, execution or live state."""
import argparse
import hashlib
from html.parser import HTMLParser
import html
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[6]
TOKEN = re.compile(r"\[\[(source|page|concept):([a-z0-9-]+)\|([^\]]+)\]\]")

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def words(text):
    return re.findall(r"\w+", html.unescape(text))

def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

class Parsed(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = []; self.links = []; self.sections = {}; self.section_stack = []
        self.code = []; self.current_code = None
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        for name in ("href", "src"):
            if name in attrs:
                self.links.append(attrs[name])
        if tag == "section":
            self.section_stack.append(attrs.get("id"))
            if attrs.get("id"):
                self.sections[attrs["id"]] = []
        if tag == "code":
            self.current_code = {"class": attrs.get("class"), "text": []}
    def handle_endtag(self, tag):
        if tag == "section":
            self.section_stack.pop()
        if tag == "code" and self.current_code is not None:
            self.code.append({"class": self.current_code["class"], "text": "".join(self.current_code["text"])})
            self.current_code = None
    def handle_data(self, data):
        for sid in self.section_stack:
            if sid:
                self.sections[sid].append(data)
        if self.current_code is not None:
            self.current_code["text"].append(data)

def local_link(source, value, cache):
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc:
        raise AssertionError(("Unexpected remote preview link", source, value))
    if not parsed.path:
        target = source
    else:
        target = (source.parent / unquote(parsed.path)).resolve()
    assert target.is_file(), ("Missing local target", source, value)
    assert target == ROOT or ROOT in target.parents, ("Outside selected repository", target)
    if parsed.fragment and target.suffix == ".html":
        if target not in cache:
            cache[target] = Parsed(target.read_text())
        assert unquote(parsed.fragment) in cache[target].ids, ("Missing fragment", source, value)
    return {"source": source.relative_to(ROOT).as_posix(), "href": value,
        "resolved": target.relative_to(ROOT).as_posix(), "fragment": parsed.fragment}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--render", default="render-0001")
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    generation = HERE / args.render
    report_path = HERE / args.report
    assert report_path.parent == HERE and not report_path.exists()
    narrative = json.loads((HERE / "narrative.json").read_text())
    sources = json.loads((HERE / "source-map.json").read_text())
    receipt = json.loads((generation / "render-receipt.json").read_text())
    assert receipt["narrative_sha256"] == digest(HERE / "narrative.json")
    assert receipt["source_map_sha256"] == digest(HERE / "source-map.json")
    assert len(narrative["pages"]) == 14
    expected_routes = {
        "README.md", "status.md", "tutorials/first-inspection.md", "tutorials/local-work.md",
        "how-to/provision-and-review.md", "how-to/agent-sessions.md", "how-to/recover-and-retry.md",
        "how-to/paperclip.md", "how-to/packages-and-installation.md", "explanation/architecture.md",
        "explanation/work-evidence-learning.md", "explanation/state-authority-and-memory.md",
        "reference/cli-and-environment.md", "development-and-maintenance.md"}
    assert {p["markdown_route"] for p in narrative["pages"]} == expected_routes
    for row in sources["source_bindings"].values():
        path = ROOT / row["snapshot_path"]
        assert digest(path) == row["sha256"] and path.stat().st_size == row["size_bytes"]
    for row in receipt["outputs"]:
        path = generation / row["path"]
        assert digest(path) == row["sha256"] and path.stat().st_size == row["size_bytes"]
    cache = {}; links = []; sections = []; diagrams = []; command_occurrences = 0
    for page in narrative["pages"]:
        preview = generation / "preview/governance-lab-series" / page["site_file"]
        markdown = generation / "markdown/docs/lab/runtime" / page["markdown_route"]
        text = preview.read_text(); md = markdown.read_text(); parsed = Parsed(text); cache[preview] = parsed
        assert len(parsed.ids) == len(set(parsed.ids)), ("Duplicate owned HTML IDs", preview)
        assert "[[" not in text and "{{" not in text and "[[" not in md and "{{" not in md
        for link in parsed.links:
            links.append(local_link(preview, link, cache))
        for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", md):
            links.append(local_link(markdown, match.group(2), cache))
        for section in page["sections"]:
            sid = page["article_id"] + "-" + slug(section["title"])
            body = TOKEN.sub(lambda m: m.group(3), section["body"])
            body = re.sub(r"\{\{CODE:([a-z0-9-]+)\}\}", lambda m: narrative["code_blocks"][m.group(1)], body)
            expected = section["title"] + "\n" + body
            diagram = section["diagram"]
            if diagram:
                expected += "\n" + diagram["code"] + "\n" + diagram["alternative"] + "\n" + diagram["meaning"]
                actual_code = [x["text"] for x in parsed.code if x["class"] == "language-mermaid"]
                assert diagram["code"] in actual_code
                fence = chr(96) * 4
                assert fence + "mermaid\n" + diagram["code"] + "\n" + fence in md
                diagrams.append({"page": page["key"], "id": diagram["id"],
                    "code_sha256": hashlib.sha256(diagram["code"].encode()).hexdigest(),
                    "identical_html_markdown": True, "text_equivalent": True,
                    "evidence": diagram["evidence"]})
            # Markdown, HTML and source bodies agree after markup, whitespace and table dividers.
            html_words = words("\n".join(parsed.sections[sid]))
            section_md = md.split("## " + section["title"] + "\n", 1)[1].split("\n## ", 1)[0]
            section_md = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: m.group(1), section_md)
            section_md = re.sub(chr(96) * 4 + r"(bash|mermaid)?\n?", "", section_md)
            assert html_words == words(expected), ("HTML body differs", page["key"], section["title"])
            assert words(section["title"] + "\n" + section_md) == words(expected), ("Markdown body differs", page["key"], section["title"])
            sections.append({"page": page["key"], "section_id": sid,
                "source_body_sha256": hashlib.sha256(section["body"].encode()).hexdigest(),
                "html_markdown_source_text_equal": True})
        commands = [x["text"] for x in parsed.code if x["class"] == "language-bash"]
        if page["key"] == "first-inspection":
            assert commands == [narrative["code_blocks"]["read-command"]]
            command_occurrences += 1
    assert len(diagrams) == 5 and command_occurrences == 1
    # Syntax only: bash -n does not invoke the Lab or create its store.
    syntax = subprocess.run(["bash", "-n"], input=narrative["code_blocks"]["read-command"], text=True, capture_output=True)
    assert syntax.returncode == 0
    command = narrative["code_blocks"]["read-command"]
    for required in ['--store "$lab_read_store" "$@"', "lab_v1_read verify", "lab_v1_read status",
        "lab_v1_read inspect product-capability:cyberalchemy-lab:governed-knowledge-lifecycle --record",
        "assert not Path(sys.argv[3]).exists()", "-I -X utf8 -B -S", "--inhibit-cache"]:
        assert required in command
    # Confirm admitted parser grammar by its exact captured source, without importing it.
    cli = (ROOT / sources["source_bindings"]["v1-cli"]["snapshot_path"]).read_text()
    for required in ['add_parser("verify")', 'add_parser("status")', 'add_parser("inspect")',
        'add_argument("subject")', 'add_argument("--record"', 'add_argument("--store"']:
        assert required in cli
    result = {"schema_version": "lab-T21-runtime-narrative-validation/v1-candidate",
        "result": "PASS-owned-public-static-rendering", "pages": 14, "sections": len(sections),
        "diagrams": diagrams, "public_snapshots": len(sources["source_bindings"]),
        "owned_local_links": len(links), "section_parity": sections, "links": links,
        "narrative_sha256": digest(HERE / "narrative.json"), "source_map_sha256": digest(HERE / "source-map.json"),
        "render_receipt_sha256": digest(generation / "render-receipt.json"),
        "read_command_syntax": "bash -n PASS; captured admitted parser grammar present; no command executed",
        "interpreter": {"path": sys.executable, "version": sys.version, "qualification": "stdlib authoring only; no T07 installation qualification claimed"},
        "shared_site_build": False, "editorial_pass": False, "search_integration": False,
        "markdown_import_integration": False, "fresh_installation": False, "runtime_executed": False,
        "task_complete": False, "claim_ceiling": "Body/diagram fidelity and resolving owned preview links only; proposed final-site links require Root integration."}
    with report_path.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True); stream.write("\n")
    print(json.dumps({"result": result["result"], "pages": 14, "sections": len(sections),
        "diagrams": len(diagrams), "owned_local_links": len(links), "runtime_executed": False}))

if __name__ == "__main__":
    main()
