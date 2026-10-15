#!/usr/bin/env python3
"""Render the captured Lab/Craft edition and package its static resource closure."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from html import escape
from html.parser import HTMLParser
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit
import zipfile

ROOT = Path(__file__).resolve().parent
LAB = "governance-lab-series"
CRAFT = "craft-documentation-proposal"
EXCLUDED = {".git", ".venv", "__pycache__", "versions", "output", "release", ".draft-history"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class References(HTMLParser):
    """Collect static URLs, IDs, and meta-refresh destinations without executing HTML."""

    def __init__(self, text: str):
        super().__init__(convert_charrefs=True)
        self.urls: list[str] = []
        self.ids: list[str] = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "id" in values:
            self.ids.append(values["id"])
        if tag in {"a", "link", "img", "script", "source", "iframe", "object"}:
            self.urls.extend(values[key] for key in ("href", "src", "data") if values.get(key))
            if values.get("srcset"):
                self.urls.extend(part.strip().split()[0] for part in values["srcset"].split(","))
        if tag == "meta" and values.get("http-equiv", "").lower() == "refresh":
            match = re.search(r"url\s*=\s*(.+)", values.get("content", ""), re.I)
            if match:
                self.urls.append(match.group(1).strip().strip("\"'"))

    handle_startendtag = handle_starttag


def relative_target(base: Path, url: str, boundary: Path) -> Path | None:
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    if parsed.path.startswith("/"):
        raise ValueError(f"Root-relative URL prevents project hosting: {base.name}: {url}")
    target = (base.parent / unquote(parsed.path)).resolve()
    if not target.is_relative_to(boundary):
        raise ValueError(f"Local reference escapes the site: {base.name}: {url}")
    if not target.is_file():
        raise FileNotFoundError(f"Missing resource: {base.relative_to(boundary)} -> {url}")
    if any(part in EXCLUDED or part.startswith(".env") for part in target.relative_to(boundary).parts):
        raise ValueError(f"Excluded resource linked from page: {url}")
    return target


def render(stage: Path, logs: Path) -> None:
    env = dict(os.environ, PYTHONUTF8="1", LAB_SITE_SKIP_SEARCH_INDEX="1")
    steps = [
        ("role-icons", stage / LAB / "render_role_icons.py"),
        ("examples", stage / LAB / "documentation_examples.py"),
        ("craft", stage / CRAFT / "tools/build_article.py"),
        ("essays-and-reference", stage / LAB / "render_series.py"),
        ("guide-and-search", stage / LAB / "render_article.py"),
        ("site-presentation", ROOT / "site_presentation.py"),
        ("natural-editorial", ROOT / "editorial_style.py"),
        ("site-finish", ROOT / "site_finish.py"),
        ("final-search", stage / LAB / "build_site_search.py"),
        ("documentation-checks", stage / LAB / "documentation_checks.py"),
    ]
    for name, script in steps:
        if name == 'natural-editorial':
            apply_typography(stage)
        print(f"Building {name}…", flush=True)
        command = [sys.executable, str(script)]
        if name in {'natural-editorial', 'site-presentation', 'site-finish'}:
            command.append(str(stage))
        result = subprocess.run(command, cwd=script.parent, env=env,
                                text=True, encoding="utf-8", capture_output=True)
        (logs / f"{name}.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode:
            raise RuntimeError(f"{name} failed; see {logs / (name + '.log')}\n{result.stderr[-4000:]}")


def apply_typography(stage: Path) -> None:
    """Apply the shared presentation sheet before final search fingerprints."""
    manifest = json.loads((stage / LAB / 'research/documentation-manifest.json').read_text())
    names = manifest['html_files'] + ['research/reader-study.html', '../robot-learning-series/robot-learning-series.html']
    stylesheet = stage / LAB / 'assets/site-typography.css'
    for name in names:
        page = stage / LAB / name
        if not page.is_file():
            continue
        raw = page.read_text(encoding='utf-8')
        if 'site-typography.css' in raw:
            continue
        href = Path(os.path.relpath(stylesheet, page.parent)).as_posix()
        raw = raw.replace('</head>', f'<link rel="stylesheet" href="{escape(href)}">\n</head>', 1)
        page.write_text(raw, encoding='utf-8')


def select_files(stage: Path) -> set[Path]:
    manifest = json.loads((stage / LAB / "research/documentation-manifest.json").read_text())
    queue = [stage / LAB / name for name in manifest["html_files"]]
    queue += [stage / LAB / "research/reader-study.html", stage / CRAFT / "index.html",
              stage / LAB / "research/editorial-edition.json"]
    queue += [stage / LAB / 'research' / name for name in ('search-judgments.json', 'site-search-index.json', 'documentation-manifest.json')]
    if manifest.get('reference_pages_manifest'):
        queue.append(stage / LAB / manifest['reference_pages_manifest'])
    # These resources load dynamically and therefore have no initial HTML URL.
    for folder in (stage / LAB / "assets", stage / CRAFT / "assets", stage / LAB / "examples"):
        # Retain the original illustrations in source. Ship only the vector
        # replacements; any legacy image still referenced is followed below.
        queue.extend(path for path in folder.rglob("*") if path.is_file()
                     and 'brain-medallions' not in path.parts)
    selected: set[Path] = set()
    while queue:
        path = queue.pop().resolve()
        if path in selected:
            continue
        if not path.is_relative_to(stage) or not path.is_file():
            raise ValueError(f"Invalid deployment resource: {path}")
        relative = path.relative_to(stage)
        if any(part in EXCLUDED or part.startswith(".env") for part in relative.parts):
            raise ValueError(f"Excluded deployment resource: {relative}")
        selected.add(path)
        urls: list[str] = []
        if path.suffix == ".html":
            document = References(path.read_text(encoding="utf-8"))
            duplicates = [key for key, count in Counter(document.ids).items() if count > 1]
            if duplicates:
                raise ValueError(f"Duplicate IDs: {relative}: {duplicates[:10]}")
            urls = document.urls
        elif path.suffix == ".css":
            urls = re.findall(r"url\([\s\"']*([^\)\"']+)", path.read_text(encoding="utf-8"))
        for url in urls:
            target = relative_target(path, url.strip(), stage)
            if target is not None:
                queue.append(target)
    return selected


def redirect(destination: str, label: str) -> str:
    # Preserve query strings and deep links when JavaScript is available.
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{escape(label)}</title><link rel=\"icon\" type=\"image/svg+xml\" href=\"{escape('governance-lab-series/assets/kep/cyberalchemy-lab-logo-light-v2.svg' if destination.startswith('governance-lab-series/') else 'assets/kep/cyberalchemy-lab-logo-light-v2.svg')}\"><meta http-equiv=\"refresh\" content=\"0; url={escape(destination)}\">"
            "<script>location.replace(" + json.dumps(destination) + "+location.search+location.hash);</script>"
            f"</head><body><p><a href=\"{escape(destination)}\">{escape(label)}</a></p></body></html>\n")


def archive_site(directory: Path, archive: Path) -> None:
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                info = zipfile.ZipInfo(path.relative_to(directory).as_posix(), (1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                output.writestr(info, path.read_bytes())


def build() -> dict:
    if sys.version_info < (3, 11):
        raise RuntimeError("Use Python 3.11 or newer.")
    missing = [name for name in ("markdown_it", "jsonschema") if importlib.util.find_spec(name) is None]
    if missing:
        raise RuntimeError("Install website/requirements.txt before building: " + ", ".join(missing))
    config = json.loads((ROOT / "site.json").read_text())
    output = ROOT / config["output_directory"]
    if output.parent != ROOT or output.name != "dist":
        raise ValueError("The managed deployment output must be website/dist.")
    work = ROOT / ".build"
    work.mkdir(exist_ok=True)
    logs = work / "logs"
    logs.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="render-", dir=work) as temporary:
        stage = Path(temporary) / "source"
        shutil.copytree(ROOT / "source", stage, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        shutil.copy2(ROOT / "hackathon.json", stage / LAB / "hackathon.json")
        render(stage, logs)
        (stage / CRAFT / "index.html").write_text(redirect("craft-model.html", "Craft documentation"))
        entry = stage / config["entry"]
        if not entry.is_file() or not entry.resolve().is_relative_to(stage):
            raise ValueError("site.json entry must identify a generated local page.")
        search = json.loads((stage / LAB / "research/site-search-index.json").read_text())
        editorial = json.loads((stage / LAB / "research/editorial-edition.json").read_text())
        if digest(stage / LAB / "assets/site-search-index.js") != search["index_sha256"]:
            raise ValueError("Search index digest does not match the generated index.")
        for name, expected in search["source_html_sha256"].items():
            if digest(stage / LAB / name) != expected:
                raise ValueError(f"Stale search source: {name}")
        files = select_files(stage)
        assembled = Path(temporary) / "dist"
        assembled.mkdir()
        for path in sorted(files):
            target = assembled / path.relative_to(stage)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(path.read_bytes())
        (assembled / "index.html").write_text(redirect(config["entry"], "CyberAlchemy Lab"))
        (assembled / ".nojekyll").write_text("")
        rows = [{"path": p.relative_to(assembled).as_posix(), "sha256": digest(p), "bytes": p.stat().st_size}
                for p in sorted(assembled.rglob("*")) if p.is_file()]
        receipt = {"schema_version": "lab-website-release/v1", "authority_effect": "none",
                   "entry": "index.html", "destination": config["entry"], "search_entries": search["entries"],
                   "search_groups": search["groups"], "source_mode": config["source_mode"],
                   "source_capture_date": "2026-10-08",
                   "editorial_edition": {"date": editorial["date"], "voice": editorial["voice"],
                                         "editorial_copy_sha256": editorial["editorial_copy_sha256"]},
                   "files": rows,
                   "scope": "Static documentation; no Lab runtime, admission or deployment performed."}
        (assembled / "release-manifest.json").write_text(json.dumps(receipt, indent=2) + "\n")
        # Render in a temporary tree; only replace previous output after success.
        previous = ROOT / ".build/previous-dist"
        if previous.exists():
            shutil.rmtree(previous)
        if output.exists():
            output.replace(previous)
        try:
            assembled.replace(output)
        except Exception:
            if previous.exists():
                previous.replace(output)
            raise
        if previous.exists():
            shutil.rmtree(previous)
    artifacts = ROOT / "artifacts"
    artifacts.mkdir(exist_ok=True)
    archive = artifacts / "cyberalchemy-lab-website.zip"
    archive_site(output, archive)
    summary = {"output": "website/dist", "archive": "website/artifacts/" + archive.name,
               "archive_sha256": digest(archive), "archive_bytes": archive.stat().st_size,
               "files": len(receipt["files"]) + 1, "search_entries": receipt["search_entries"],
               "search_groups": receipt["search_groups"], "deployment_performed": False}
    (artifacts / "build.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:
        build()
    except (ValueError, RuntimeError, OSError) as error:
        print(f"Website build failed: {error}", file=sys.stderr)
        sys.exit(1)
