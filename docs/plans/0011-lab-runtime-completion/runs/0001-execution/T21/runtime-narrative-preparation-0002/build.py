"""ND01-owned driver; reuse the exact frozen dual renderer under its true filename."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[6]
PREDECESSOR = HERE.parent / "runtime-narrative-preparation-0001"
GENERATOR_PIN = "110d03b089dfc28040415cacebc2a646288a4162b9a99ba63acb6ff7f2869a9e"

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def selected(path, expected):
    assert path.is_file() and not path.is_symlink() and not any(p.is_symlink() for p in path.parents)
    raw = path.read_bytes()
    assert digest(raw) == expected, "Exact selected input mismatch"
    return raw

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--narrative-sha256", required=True)
    parser.add_argument("--source-map-sha256", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = (HERE / args.output).resolve()
    assert output.parent == HERE and not output.exists(), "New owned output required"
    generator_path = PREDECESSOR / "generate.py"
    generator_raw = selected(generator_path, GENERATOR_PIN)
    # Compile captured bytes under the actual predecessor filename; no origin alias.
    namespace = {"__name__": "T21_selected_document_renderer", "__file__": str(generator_path)}
    exec(compile(generator_raw, str(generator_path), "exec"), namespace)
    narrative_raw = selected(HERE / "narrative.json", args.narrative_sha256)
    source_raw = selected(HERE / "source-map.json", args.source_map_sha256)
    narrative, sources = json.loads(narrative_raw), json.loads(source_raw)
    assert len(narrative["pages"]) == 14 and len(sources["source_bindings"]) == 74
    for row in sources["source_bindings"].values():
        raw = selected(ROOT / row["snapshot_path"], row["sha256"])
        assert len(raw) == row["size_bytes"]
    shell_row = sources["source_bindings"]["site-shell"]
    shell = selected(ROOT / shell_row["snapshot_path"], shell_row["sha256"]).decode()
    report = namespace["Renderer"](narrative, sources, output).run(shell)
    report["narrative_sha256"] = digest(narrative_raw)
    report["source_map_sha256"] = digest(source_raw)
    report["reused_generator"] = {"true_path": generator_path.relative_to(ROOT).as_posix(),
        "sha256": GENERATOR_PIN, "compiled_filename": str(generator_path),
        "source_copy_or_filename_alias": False}
    namespace["write_new"](output / "render-receipt.json", (json.dumps(report, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"result": "PASS-owned-ND01-dual-render", "pages": report["pages"],
        "diagrams": report["diagrams"], "outputs": len(report["outputs"]),
        "public_inputs": 74, "runtime_executed": False}))

if __name__ == "__main__":
    main()
