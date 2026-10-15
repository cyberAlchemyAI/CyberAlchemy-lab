"""Independent public documentation checks. No Lab imports or execution."""
import ast
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
ROOT = PACKAGE.parents[6]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def normal(text):
    return " ".join(text.split())

class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.urls = []
        self.active = []
        self.sections = {}
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        self.urls.extend(a[k] for k in ("href", "src") if k in a)
        if tag == "section":
            self.active.append(a.get("id"))
            if a.get("id"):
                self.sections[a["id"]] = []
    def handle_endtag(self, tag):
        if tag in ("p", "h2", "th", "td", "pre", "figcaption", "li"):
            for key in self.active:
                if key:
                    self.sections[key].append(" ")
        if tag == "section":
            self.active.pop()
    def handle_data(self, text):
        for key in self.active:
            if key:
                self.sections[key].append(text)

manifest = json.loads((PACKAGE / "source-manifest.json").read_text())
for r in manifest["files"]:
    p = ROOT / r["path"]
    assert sha(p) == r["sha256"] and p.stat().st_size == r["size_bytes"]
selection = json.loads((PACKAGE / "selection.json").read_text())
for name, expected in selection["bindings"].items():
    assert sha(PACKAGE / name) == expected
sources = json.loads((PACKAGE / "source-map.json").read_text())
originals = []
for key, r in sources["source_bindings"].items():
    assert sha(ROOT / r["snapshot_path"]) == r["sha256"]
    assert (ROOT / r["snapshot_path"]).stat().st_size == r["size_bytes"]
    originals.append({"key": key, "sha256": sha(ROOT / r["original_path"]),
                      "matches_snapshot": sha(ROOT / r["original_path"]) == r["sha256"]})
assert all(r["matches_snapshot"] for r in originals)
n = json.loads((PACKAGE / "narrative.json").read_text())
contents = (ROOT / sources["source_bindings"]["contents"]["snapshot_path"]).read_text()
expected_routes = set(re.findall(r"`docs/lab/runtime/([^`]+\.md)`", contents.split("## Generated API reference")[0]))
assert {p["markdown_route"] for p in n["pages"]} == expected_routes
token = re.compile(r"\[\[(?:source|concept|page):([a-z0-9-]+)\|([^\]]+)\]\]")
cache = {}
links = 0
sections = 0
diagrams = 0
for page in n["pages"]:
    html_path = PACKAGE / "render-0002/preview/governance-lab-series" / page["site_file"]
    md_path = PACKAGE / "render-0002/markdown/docs/lab/runtime" / page["markdown_route"]
    doc = Document(html_path.read_text())
    md = md_path.read_text()
    assert len(doc.ids) == len(set(doc.ids))
    for origin, urls in ((html_path, doc.urls), (md_path, re.findall(r"\[[^\]]+\]\(([^)]+)\)", md))):
        for url in urls:
            u = urlsplit(url)
            assert not u.scheme and not u.netloc
            target = (origin.parent / unquote(u.path)).resolve() if u.path else origin
            assert target.is_file() and ROOT in target.parents
            if u.fragment and target.suffix == ".html":
                if target not in cache:
                    cache[target] = Document(target.read_text())
                assert unquote(u.fragment) in cache[target].ids
            links += 1
    for s in page["sections"]:
        sid = page["article_id"] + "-" + re.sub(r"[^a-z0-9]+", "-", s["title"].lower()).strip("-")
        body = token.sub(lambda m: m.group(2), s["body"])
        body = re.sub(r"\{\{CODE:([a-z0-9-]+)\}\}", lambda m: n["code_blocks"][m.group(1)], body)
        text_blocks = []
        for block in re.split(r"\n\s*\n", body):
            if block.startswith("|"):
                for line in block.splitlines():
                    if not re.fullmatch(r"[|\s:-]+", line):
                        text_blocks.append(" ".join(x.strip() for x in line.strip().strip("|").split("|")))
            elif block.startswith("- "):
                text_blocks.append("\n".join(line[2:] for line in block.splitlines()))
            else:
                text_blocks.append(block)
        expected = s["title"] + " " + " ".join(text_blocks)
        if s["diagram"]:
            d = s["diagram"]
            expected += " " + d["code"] + " " + d["alternative"] + " " + d["meaning"]
            assert "````mermaid\n" + d["code"] + "\n````" in md
            diagrams += 1
        assert normal("".join(doc.sections[sid])) == normal(expected), (page["key"], s["title"])
        section_md = md.split("## " + s["title"] + "\n", 1)[1].split("\n## ", 1)[0]
        section_md = re.sub(r"\[([^\]]+)\]\([^)]+\)", lambda m: m.group(1), section_md)
        source_with_diagram = body
        if s["diagram"]:
            source_with_diagram += "\n\n````mermaid\n" + d["code"] + "\n````\n\n" + d["alternative"] + "\n\n" + d["meaning"]
        source_with_diagram = source_with_diagram.replace(n["code_blocks"]["read-command"], "````bash\n" + n["code_blocks"]["read-command"] + "\n````")
        assert normal(section_md) == normal(source_with_diagram), ("Markdown punctuation/body parity", page["key"], s["title"])
        sections += 1
    for mode in ("render-0002", "render-0003"):
        receipt = json.loads((PACKAGE / mode / "render-receipt.json").read_text())
        assert len(receipt["outputs"]) == 43
        for r in receipt["outputs"]:
            assert sha(PACKAGE / mode / r["path"]) == r["sha256"]
            assert sha(PACKAGE / "render-0002" / r["path"]) == sha(PACKAGE / "render-0003" / r["path"])
syntax = subprocess.run(["bash", "-n"], input=n["code_blocks"]["read-command"], text=True, capture_output=True)
assert syntax.returncode == 0
index = json.loads((PACKAGE / "code-index.json").read_text())
symbol_count = 0
for r in index["files"]:
    if r["snapshot_path"].endswith(".py"):
        tree = ast.parse((ROOT / r["snapshot_path"]).read_text())
        symbols = {(node.lineno, node.end_lineno, type(node).__name__) for node in ast.walk(tree)
                   if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
        for declared in r["symbols"]:
            assert (declared["line"], declared["end_line"], declared["kind"]) in symbols
            symbol_count += 1
result = {"schema_version": "lab-T21-independent-narrative-static-checks/v1-candidate", "result": "PASS",
          "component_manifest_files": len(manifest["files"]), "selected_binding_files": len(selection["bindings"]),
          "public_snapshots_and_originals": len(originals), "public_originals": originals,
          "pages": len(n["pages"]), "sections_with_punctuation_preserved": sections,
          "diagrams": diagrams, "resolving_local_links": links, "deterministic_outputs": 43,
          "AST_location_checks": symbol_count, "bash_syntax": "PASS; no commands executed",
          "runtime_executed": False, "shared_site_mutated": False, "task_complete": False}
with (HERE / "result.json").open("x") as stream:
    json.dump(result, stream, indent=2, sort_keys=True)
    stream.write("\n")
print(json.dumps({k:v for k,v in result.items() if k != "public_originals"}))
