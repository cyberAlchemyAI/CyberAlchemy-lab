#!/usr/bin/env python3
"""Build a structural and full-text map of repository file contents."""

from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
from html.parser import HTMLParser
import io
import json
import re
import shutil
import sqlite3
import subprocess
import sys
import tarfile
import tempfile
import tomllib
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
INVENTORY_ROOT = ROOT / ".arcanum" / "inventory"
SOURCE_MANIFEST = INVENTORY_ROOT / "inventory.json"
MAP_PATH = INVENTORY_ROOT / "content-map.jsonl.gz"
SEARCH_PATH = INVENTORY_ROOT / "content-search.sqlite3"
INFO_PATH = INVENTORY_ROOT / "content-map-info.json"

CODE_SUFFIXES = {
    ".c", ".js", ".mjs", ".mts", ".py", ".rs", ".sql", ".tla", ".tsx", ".ts",
    ".lean", ".alloy", ".html", ".sh", ".cfg", ".template", ".tmpl",
}
CODE_DECLARATION = re.compile(
    r"^\s*(?:(?:export|pub|async|static|private|protected|const|default)\s+)*"
    r"(?:function|class|interface|type|enum|struct|trait|mod|fn|def|macro_rules!)\s+"
    r"([A-Za-z_$][\w$]*)",
    re.MULTILINE,
)
IMPORT = re.compile(r"^\s*(?:import\s+.+|from\s+\S+\s+import\s+.+|use\s+.+;?)\s*$", re.MULTILINE)
MD_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
MD_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)|^\[[^\]]+\]:\s*(\S+)", re.MULTILINE)


def ar_members(data: bytes) -> list[tuple[str, bytes]]:
    if not data.startswith(b"!<arch>\n"):
        return []
    members = []
    long_names = b""
    cursor = 8
    while cursor + 60 <= len(data):
        header = data[cursor : cursor + 60]
        if header[58:60] != b"`\n":
            break
        raw_name = header[:16].decode("ascii", "replace").strip()
        try:
            size = int(header[48:58].decode("ascii").strip())
        except ValueError:
            break
        start = cursor + 60
        payload = data[start : start + size]
        cursor = start + size + (size & 1)
        if raw_name == "//":
            long_names = payload
            continue
        if raw_name in {"/", "/SYM64/"} or raw_name.startswith("__.SYMDEF"):
            continue
        if raw_name.startswith("#1/"):
            try:
                name_size = int(raw_name[3:])
                name = payload[:name_size].decode("utf-8", "replace").rstrip("\0")
                payload = payload[name_size:]
            except ValueError:
                name = raw_name
        elif raw_name.startswith("/") and raw_name[1:].isdigit():
            offset = int(raw_name[1:])
            end = long_names.find(b"/\n", offset)
            name = long_names[offset:end if end >= 0 else None].decode("utf-8", "replace")
        else:
            name = raw_name.rstrip("/")
        members.append((name, payload))
    return members


def binary_structure(path: str, data: bytes) -> tuple[dict, str]:
    suffix = PurePosixPath(path).suffix.lower()
    strings = []
    features = {}
    with tempfile.NamedTemporaryFile(suffix=suffix or ".bin") as temporary:
        temporary.write(data)
        temporary.flush()
        file_tool = shutil.which("file")
        description = subprocess.run([file_tool, "--brief", temporary.name], capture_output=True, text=True, check=False).stdout.strip() if file_tool else "binary data"
        if data.startswith(b"\x7fELF"):
            features["format"] = "ELF"
            readelf = shutil.which("readelf")
            if readelf:
                result = subprocess.run([readelf, "-h", "-S", "-s", "--wide", temporary.name], capture_output=True, text=True, check=False)
                elf_text = result.stdout
                fields = {}
                for key, value in re.findall(r"^\s*(Class|Data|OS/ABI|ABI Version|Type|Machine|Version|Entry point address):\s*(.*?)\s*$", elf_text, re.MULTILINE):
                    fields[key] = value
                sections = sorted(set(re.findall(r"^\s*\[\s*\d+\]\s+(\S+)", elf_text, re.MULTILINE)))
                symbol_names = sorted(set(re.findall(r"^\s*\d+:\s+\S+\s+\d+\s+\S+\s+\S+\s+\S+\s+(\S+)", elf_text, re.MULTILINE)))
                features.update({"header": fields, "sections": sections, "symbol_names": symbol_names, "readelf_status": result.returncode})
        if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
            width, height = int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
            chunks = []
            offset = 8
            while offset + 12 <= len(data):
                length = int.from_bytes(data[offset : offset + 4], "big")
                kind = data[offset + 4 : offset + 8].decode("ascii", "replace")
                chunks.append({"type": kind, "data_bytes": length})
                offset += length + 12
                if kind == "IEND":
                    break
            features.update({"format": "PNG", "width": width, "height": height, "chunks": chunks})
        elif data.startswith(b"\0\0\x01\0") and len(data) >= 6:
            count = int.from_bytes(data[4:6], "little")
            entries = []
            for offset in range(6, min(len(data), 6 + count * 16), 16):
                if offset + 16 > len(data):
                    break
                width, height, colors, reserved, planes, bits, size, image_offset = __import__("struct").unpack_from("<BBBBHHII", data, offset)
                entries.append({"width": width or 256, "height": height or 256, "colors": colors, "planes": planes, "bits_per_pixel": bits, "image_bytes": size, "image_offset": image_offset})
            features.update({"format": "ICO", "image_count": count, "images": entries})
        elif data.startswith(b"!<arch>\n"):
            members = ar_members(data)
            features.update({"format": "ar-archive", "member_count": len(members), "members": [name for name, _ in members]})
        else:
            features["format"] = "opaque-binary"
        strings_tool = shutil.which("strings")
        if strings_tool:
            result = subprocess.run([strings_tool, "-a", "-n", "4", temporary.name], capture_output=True, check=False)
            strings = [line.decode("utf-8", "replace") for line in result.stdout.splitlines() if line]
        else:
            strings = [value.decode("utf-8", "replace") for value in re.findall(rb"[\x20-\x7e]{4,}", data)]
    description = description or features.get("format", "opaque binary")
    features.update({"file_description": description, "printable_string_count": len(strings), "printable_string_samples": strings[:30]})
    return {
        "content_kind": "binary-structure",
        "format": features.get("format", "opaque-binary"),
        "status": "mapped-binary-structure",
        "byte_count": len(data),
        "sha256": sha256(data),
        "preview": " | ".join(strings[:3])[:240],
        "features": features,
    }, "\n".join(strings)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def text_decode(data: bytes) -> tuple[str | None, str]:
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        try:
            return data.decode("utf-16"), "utf-16"
        except UnicodeDecodeError:
            return None, "binary"
    try:
        return data.decode("utf-8-sig"), "utf-8"
    except UnicodeDecodeError:
        return None, "binary"


def json_pointer_segment(segment: str) -> str:
    return segment.replace("~", "~0").replace("/", "~1")


def structural_paths(value) -> tuple[list[dict], dict]:
    counts: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    lengths: dict[str, list[int]] = collections.defaultdict(list)
    stack = [(value, "$")]
    nodes = 0
    while stack:
        item, path = stack.pop()
        nodes += 1
        if isinstance(item, dict):
            counts[path]["object"] += 1
            for key, child in item.items():
                stack.append((child, path + "/" + json_pointer_segment(str(key))))
        elif isinstance(item, list):
            counts[path]["array"] += 1
            lengths[path].append(len(item))
            for child in item:
                stack.append((child, path + "/*"))
        elif item is None:
            counts[path]["null"] += 1
        elif isinstance(item, bool):
            counts[path]["boolean"] += 1
        elif isinstance(item, (int, float)):
            counts[path]["number"] += 1
        else:
            counts[path]["string"] += 1
    entries = []
    for path in sorted(counts):
        entry = {"path": path, "types": dict(sorted(counts[path].items()))}
        if path in lengths:
            entry["array_lengths"] = {
                "count": len(lengths[path]),
                "min": min(lengths[path]),
                "max": max(lengths[path]),
                "empty_count": sum(length == 0 for length in lengths[path]),
            }
        entries.append(entry)
    return entries, {"node_count": nodes, "root_type": type(value).__name__}


def paragraph_spans(text: str, limit: int = 240) -> list[dict]:
    spans = []
    start = None
    buf = []
    lines = text.splitlines()
    for number, line in enumerate(lines, 1):
        if line.strip():
            if start is None:
                start = number
            buf.append(line.strip())
        elif start is not None:
            content = " ".join(buf)
            spans.append({"start_line": start, "end_line": number - 1, "chars": len(content), "preview": content[:limit]})
            start, buf = None, []
    if start is not None:
        content = " ".join(buf)
        spans.append({"start_line": start, "end_line": len(lines), "chars": len(content), "preview": content[:limit]})
    return spans


def markdown_structure(text: str) -> dict:
    lines = text.splitlines()
    headings = []
    for n, line in enumerate(lines, 1):
        match = MD_HEADING.match(line)
        if match:
            headings.append({"level": len(match.group(1)), "title": match.group(2), "line": n})
    sections = []
    for i, heading in enumerate(headings):
        next_line = len(lines) + 1
        for later in headings[i + 1 :]:
            if later["level"] <= heading["level"]:
                next_line = later["line"]
                break
        sections.append({"level": heading["level"], "title": heading["title"], "start_line": heading["line"], "end_line": next_line - 1})
    links = [next((item for item in match.groups() if item), "") for match in MD_LINK.finditer(text)]
    fences = collections.Counter()
    open_fence = None
    for line in lines:
        match = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if not match:
            continue
        marker, info = match.groups()
        if open_fence is None:
            language = info.strip().split()
            fences[language[0].lower() if language else "plain"] += 1
            open_fence = marker[0]
        elif marker[0] == open_fence:
            open_fence = None
    return {
        "headings": headings,
        "sections": sections,
        "links": links,
        "paragraphs": paragraph_spans(text),
        "fenced_code_blocks": dict(sorted(fences.items())),
    }


def code_structure(text: str) -> dict:
    declarations = [{"name": m.group(1), "line": text.count("\n", 0, m.start()) + 1} for m in CODE_DECLARATION.finditer(text)]
    imports = [{"line": text.count("\n", 0, m.start()) + 1, "text": m.group(0).strip()[:240]} for m in IMPORT.finditer(text)]
    return {"declarations": declarations, "imports": imports, "paragraphs": paragraph_spans(text, 180)}


class HtmlOutline(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tag_counts = collections.Counter()
        self.elements = []
        self.text_parts = []
        self.active_text = None

    def handle_starttag(self, tag, attrs):
        self.tag_counts[tag] += 1
        attributes = dict(attrs)
        if tag in {"title", "h1", "h2", "h3", "a", "img", "form", "input", "button", "script", "link"}:
            keys = {"id", "class", "href", "src", "alt", "action", "method", "type", "name", "rel"}
            self.elements.append({"tag": tag, "line": self.getpos()[0], "attributes": {key: value for key, value in attributes.items() if key in keys}})
        if tag in {"title", "h1", "h2", "h3"}:
            self.active_text = {"tag": tag, "line": self.getpos()[0], "text": []}

    def handle_endtag(self, tag):
        if self.active_text and self.active_text["tag"] == tag:
            self.active_text["text"] = " ".join(self.active_text["text"]).strip()
            self.elements.append(self.active_text)
            self.active_text = None

    def handle_data(self, data):
        if data.strip():
            self.text_parts.append(data.strip())
            if self.active_text:
                self.active_text["text"].append(data.strip())


def html_structure(text: str) -> dict:
    parser = HtmlOutline()
    parser.feed(text)
    parser.close()
    visible = "\n".join(parser.text_parts)
    return {"tag_counts": dict(sorted(parser.tag_counts.items())), "elements": parser.elements,
            "visible_text_chars": len(visible), "visible_text_paragraphs": paragraph_spans(visible)}


def map_text(path: str, data: bytes) -> tuple[dict, str]:
    text, encoding = text_decode(data)
    if text is None:
        return binary_structure(path, data)

    suffix = PurePosixPath(path).suffix.lower()
    record = {
        "content_kind": "text",
        "encoding": encoding,
        "char_count": len(text),
        "line_count": len(text.splitlines()),
        "word_count": len(re.findall(r"\b[\w'-]+\b", text, flags=re.UNICODE)),
        "status": "mapped",
    }
    if suffix == ".json":
        try:
            value = json.loads(text)
            paths, summary = structural_paths(value)
            record.update({"format": "json", "status": "mapped-structured", "structure": summary, "field_paths": paths})
        except (json.JSONDecodeError, RecursionError) as error:
            record.update({"format": "json-text-fallback", "parse_error": str(error)[:300], "paragraphs": paragraph_spans(text)})
    elif suffix == ".jsonl":
        paths: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
        record_count = 0
        errors = []
        for number, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
                fields, _ = structural_paths(obj)
                record_count += 1
                for field in fields:
                    for typ, count in field["types"].items():
                        paths[field["path"]][typ] += count
            except (json.JSONDecodeError, RecursionError) as error:
                errors.append({"line": number, "error": str(error)[:160]})
        record.update({
            "format": "jsonl", "status": "mapped-structured" if not errors else "mapped-with-parse-errors",
            "record_count": record_count,
            "field_paths": [{"path": path, "types": dict(sorted(types.items()))} for path, types in sorted(paths.items())],
            "parse_errors": errors,
        })
    elif suffix in {".yaml", ".yml"}:
        try:
            import yaml
            values = list(yaml.safe_load_all(text))
            paths, summary = structural_paths(values[0] if len(values) == 1 else values)
            record.update({"format": "yaml", "status": "mapped-structured", "document_count": len(values), "structure": summary, "field_paths": paths})
        except Exception as error:
            record.update({"format": "yaml-text-fallback", "parse_error": str(error)[:300], "paragraphs": paragraph_spans(text)})
    elif suffix == ".toml":
        try:
            value = tomllib.loads(text)
            paths, summary = structural_paths(value)
            record.update({"format": "toml", "status": "mapped-structured", "structure": summary, "field_paths": paths})
        except Exception as error:
            record.update({"format": "toml-text-fallback", "parse_error": str(error)[:300], "paragraphs": paragraph_spans(text)})
    elif suffix == ".md":
        record.update({"format": "markdown", "status": "mapped-structured", **markdown_structure(text)})
    elif suffix == ".html":
        record.update({"format": "html", "status": "mapped-structured", "html_structure": html_structure(text)})
    elif suffix in CODE_SUFFIXES:
        record.update({"format": "source-text", "status": "mapped-structured", **code_structure(text)})
    else:
        record.update({"format": "plain-text", "paragraphs": paragraph_spans(text)})
    if text.strip() and len(text) <= 1000:
        record["preview"] = text.strip()[:500]
    elif text.strip():
        record["preview"] = text.strip()[:240]
    return record, text


def pdf_content(data: bytes, source_path: str) -> tuple[dict, str]:
    try:
        from pypdf import PdfReader
    except ImportError as error:
        raise RuntimeError("PDF mapping requires pypdf; install tooling/inventory/requirements.txt") from error
    reader = PdfReader(io.BytesIO(data), strict=False)
    pages = []
    texts = []
    for number, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        texts.append(text)
        pages.append({"page": number, "char_count": len(text), "preview": text.strip()[:240]})
    text = "\n\n".join(texts)
    record = {
        "content_kind": "pdf-text",
        "format": "pdf",
        "status": "mapped-structured" if text.strip() else "pdf-no-extractable-text",
        "page_count": len(reader.pages),
        "metadata": {str(k): str(v)[:500] for k, v in (reader.metadata or {}).items()},
        "pages": pages,
        "char_count": len(text),
        "preview": text.strip()[:240],
        "word_count": len(re.findall(r"\b[\w'-]+\b", text, flags=re.UNICODE)),
        "outline": [str(item.title) for item in reader.outline] if reader.outline else [],
    }
    return record, text


def make_entry(path: str, data: bytes, *, kind: str, source_path: str, member_path: str | None = None) -> tuple[dict, str]:
    identifier = path if member_path is None else f"{source_path}!/{member_path}"
    base = {"id": identifier, "path": path, "source_path": source_path, "kind": kind, "size_bytes": len(data), "sha256": sha256(data)}
    if member_path is not None:
        base["member_path"] = member_path
    suffix = PurePosixPath(path).suffix.lower()
    if suffix == ".pdf" or data.startswith(b"%PDF-"):
        detail, full_text = pdf_content(data, identifier)
    else:
        detail, full_text = map_text(path, data)
    base.update(detail)
    return base, full_text


def add_archive_members(archive_path: str, archive_bytes: bytes, emit, container_id: str | None = None, depth: int = 0) -> int:
    container_id = container_id or archive_path
    if depth > 8:
        return 0
    count = 0
    try:
        tf = tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:*")
    except tarfile.TarError:
        return add_ar_members(archive_path, archive_bytes, emit, container_id, depth)
    with tf:
        for member in tf:
            raw_name = member.name
            member_id = f"{container_id}!/{raw_name}"
            base = {"id": member_id, "path": archive_path, "source_path": archive_path, "container_id": container_id, "member_path": raw_name}
            if member.isdir():
                emit({**base, "kind": "archive-directory", "content_kind": "directory", "status": "mapped-container-entry", "size_bytes": 0}, "")
                count += 1
            elif member.isfile():
                stream = tf.extractfile(member)
                data = stream.read() if stream else b""
                nested_tar = False
                try:
                    nested = tarfile.open(fileobj=io.BytesIO(data), mode="r:*")
                    nested.close()
                    nested_tar = True
                except tarfile.TarError:
                    pass
                nested_ar = data.startswith(b"!<arch>\n")
                if nested_tar or nested_ar:
                    format_name = "tar" if nested_tar else "ar"
                    emit({**base, "kind": "archive-member-container", "content_kind": "archive", "format": format_name, "status": "mapped-container", "size_bytes": len(data), "sha256": sha256(data), "mode": oct(member.mode)}, "")
                    count += 1
                    count += add_archive_members(archive_path, data, emit, member_id, depth + 1)
                else:
                    entry, full_text = make_entry(raw_name, data, kind="archive-member", source_path=archive_path, member_path=raw_name)
                    entry.update(base)
                    entry["sha256"] = sha256(data)
                    entry["mode"] = oct(member.mode)
                    emit(entry, full_text)
                    count += 1
            elif member.issym() or member.islnk():
                emit({**base, "kind": "archive-link", "content_kind": "link", "link_target": member.linkname, "status": "mapped-link-metadata", "size_bytes": 0}, "")
                count += 1
            else:
                emit({**base, "kind": "archive-special-entry", "content_kind": "special", "status": "mapped-entry-metadata", "size_bytes": member.size}, "")
                count += 1
    return count


def add_ar_members(archive_path: str, archive_bytes: bytes, emit, container_id: str, depth: int) -> int:
    members = ar_members(archive_bytes)
    if not members:
        return 0
    count = 0
    for name, data in members:
        member_id = f"{container_id}!/{name}"
        base = {"id": member_id, "path": archive_path, "source_path": archive_path, "container_id": container_id, "member_path": name}
        if data.startswith(b"!<arch>\n"):
            emit({**base, "kind": "archive-member-container", "content_kind": "archive", "format": "ar", "status": "mapped-container", "size_bytes": len(data), "sha256": sha256(data)}, "")
            count += 1
            count += add_ar_members(archive_path, data, emit, member_id, depth + 1)
        else:
            entry, full_text = make_entry(name, data, kind="archive-member", source_path=archive_path, member_path=name)
            entry.update(base)
            entry["sha256"] = sha256(data)
            emit(entry, full_text)
            count += 1
    return count


def write_map() -> dict:
    if not SOURCE_MANIFEST.is_file():
        raise RuntimeError("run tooling/inventory/build_inventory.py first")
    check = subprocess.run([sys.executable, str(ROOT / "tooling/inventory/build_inventory.py"), "--check"], cwd=ROOT, capture_output=True, text=True)
    if check.returncode:
        raise RuntimeError("source inventory is stale; refresh it before mapping contents\n" + check.stderr.strip())
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    INVENTORY_ROOT.mkdir(parents=True, exist_ok=True)
    if MAP_PATH.exists():
        MAP_PATH.unlink()
    if SEARCH_PATH.exists():
        SEARCH_PATH.unlink()
    connection = sqlite3.connect(SEARCH_PATH)
    connection.execute("CREATE TABLE documents (id INTEGER PRIMARY KEY, lookup TEXT UNIQUE, kind TEXT, status TEXT, summary TEXT)")
    connection.execute("CREATE VIRTUAL TABLE search USING fts5(path, content, content='', tokenize='unicode61')")
    map_out = gzip.open(MAP_PATH, "wt", encoding="utf-8", newline="\n", compresslevel=6)
    counters = collections.Counter()
    status_counts = collections.Counter()

    def emit(entry: dict, full_text: str) -> None:
        map_out.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")
        lookup = entry["id"]
        status = entry.get("status", "unknown")
        summary = entry.get("preview", "")
        cursor = connection.execute("INSERT INTO documents(lookup,kind,status,summary) VALUES(?,?,?,?)", (lookup, entry.get("kind"), status, summary))
        rowid = cursor.lastrowid
        connection.execute("INSERT INTO search(rowid,path,content) VALUES(?,?,?)", (rowid, lookup, full_text))
        counters[entry.get("kind", "unknown")] += 1
        status_counts[status] += 1

    try:
        for file_record in manifest["files"]:
            path = file_record["path"]
            source = ROOT / path
            if file_record["kind"] == "symlink":
                target = source.readlink().as_posix()
                emit({"id": path, "path": path, "source_path": path, "kind": "symlink", "content_kind": "link", "status": "mapped-link-metadata", "link_target": target, "size_bytes": file_record["size_bytes"], "sha256": file_record["sha256"]}, target)
                continue
            data = source.read_bytes()
            if sha256(data) != file_record["sha256"]:
                raise RuntimeError(f"source changed after path inventory: {path}")
            if path.lower().endswith((".tar.gz", ".tgz")):
                detail = {"id": path, "path": path, "source_path": path, "kind": "archive", "content_kind": "tar-archive", "format": "tar", "status": "mapped-container", "size_bytes": len(data), "sha256": sha256(data)}
                emit(detail, "")
                member_count = add_archive_members(path, data, emit)
                detail["member_count"] = member_count
                counters["archive-member-count"] += member_count
            elif path.lower().endswith(".gz"):
                try:
                    expanded = gzip.decompress(data)
                    detail, full_text = make_entry(path[:-3], expanded, kind="compressed-content", source_path=path)
                    detail.update({"id": path, "path": path, "source_path": path, "kind": "compressed-content", "compressed_size_bytes": len(data), "expanded_size_bytes": len(expanded), "sha256": sha256(data)})
                    emit(detail, full_text)
                except (OSError, EOFError):
                    emit({"id": path, "path": path, "source_path": path, "kind": "compressed-file", "content_kind": "gzip", "status": "gzip-decompression-failed", "size_bytes": len(data), "sha256": sha256(data)}, "")
            else:
                entry, full_text = make_entry(path, data, kind="file", source_path=path)
                emit(entry, full_text)
            if sum(counters.values()) % 1000 == 0:
                connection.commit()
        connection.commit()
    finally:
        map_out.close()
        connection.close()

    result = {
        "source_file_count": manifest["summary"]["file_count"],
        "map_record_count": sum(counters[k] for k in counters if k != "archive-member-count"),
        "archive_member_count": counters["archive-member-count"],
        "record_kinds": dict(sorted(counters.items())),
        "statuses": dict(sorted(status_counts.items())),
        "map_size_bytes": MAP_PATH.stat().st_size,
        "search_size_bytes": SEARCH_PATH.stat().st_size,
    }
    try:
        import pypdf
        import yaml
        parser_versions = {"pypdf": pypdf.__version__, "PyYAML": yaml.__version__}
    except ImportError as error:
        raise RuntimeError(f"required content parser unavailable: {error}") from error
    info = {
        "format": "cyberalchemy-lab-content-map/v1",
        "source_manifest_sha256": sha256(SOURCE_MANIFEST.read_bytes()),
        "builder_sha256": sha256(Path(__file__).read_bytes()),
        "requirements_sha256": sha256((INVENTORY_ROOT / "requirements.txt").read_bytes()),
        "parser_versions": parser_versions,
        **result,
    }
    INFO_PATH.write_text(json.dumps(info, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return info


def tar_members(data: bytes):
    try:
        archive = tarfile.open(fileobj=io.BytesIO(data), mode="r:*")
    except tarfile.TarError:
        return None

    def entries():
        with archive:
            for member in archive:
                if member.isfile():
                    stream = archive.extractfile(member)
                    yield member.name, stream.read() if stream else b"", "file", None
                elif member.isdir():
                    yield member.name, b"", "directory", None
                elif member.issym() or member.islnk():
                    yield member.name, b"", "link", member.linkname
                else:
                    yield member.name, b"", "special", None
    return entries()


def validate_map() -> dict:
    if not MAP_PATH.is_file() or not SEARCH_PATH.is_file():
        raise RuntimeError("content map or search database is missing")
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    info = json.loads(INFO_PATH.read_text(encoding="utf-8")) if INFO_PATH.is_file() else {}
    expected_source_hash = sha256(SOURCE_MANIFEST.read_bytes())
    expected_builder_hash = sha256(Path(__file__).read_bytes())
    expected_requirements_hash = sha256((INVENTORY_ROOT / "requirements.txt").read_bytes())
    if info.get("source_manifest_sha256") != expected_source_hash:
        raise RuntimeError("content map was built from a different source inventory")
    if info.get("builder_sha256") != expected_builder_hash or info.get("requirements_sha256") != expected_requirements_hash:
        raise RuntimeError("content map builder or parser requirements changed; rebuild it")
    connection = sqlite3.connect(SEARCH_PATH)
    try:
        db_count = connection.execute("SELECT count(*) FROM documents").fetchone()[0]
        fts_count = connection.execute("SELECT count(*) FROM search").fetchone()[0]
        map_count = 0
        unique = set()
        statuses = collections.Counter()
        with gzip.open(MAP_PATH, "rt", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                row = json.loads(line)
                if row["id"] in unique:
                    raise RuntimeError(f"duplicate map id at line {line_number}: {row['id']}")
                unique.add(row["id"])
                statuses[row.get("status", "unknown")] += 1
                map_count += 1
        if not (map_count == db_count == fts_count):
            raise RuntimeError(f"record-count mismatch: map={map_count}, documents={db_count}, search={fts_count}")
        physical = {manifest_path["path"]: manifest_path for manifest_path in manifest["files"]}
        missing = set(physical) - unique
        if missing:
            raise RuntimeError(f"physical files missing from map ({len(missing)}), first: {sorted(missing)[:5]}")
        root_records = {}
        container_records = {}
        archive_members = collections.defaultdict(dict)
        with gzip.open(MAP_PATH, "rt", encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                if row.get("kind") in {"file", "archive", "compressed-content", "compressed-file", "symlink"} and row.get("id") == row.get("source_path"):
                    root_records[row["source_path"]] = row
                if row.get("kind") in {"archive", "archive-member-container"}:
                    container_records[row["id"]] = row
                if row.get("member_path") is not None:
                    archive_members[row["container_id"]][row["member_path"]] = row
        for path, manifest_row in physical.items():
            mapped = root_records.get(path)
            if not mapped or mapped.get("sha256") != manifest_row["sha256"]:
                raise RuntimeError(f"content map digest does not match path manifest: {path}")
        def verify_container(container_id: str, data: bytes) -> None:
            expected = archive_members[container_id]
            actual_members = tar_members(data)
            is_tar = actual_members is not None
            if not is_tar:
                actual_members = ((name, raw, "file", None) for name, raw in ar_members(data))
            seen = set()
            for name, raw, member_kind, link_target in actual_members:
                seen.add(name)
                mapped = expected.get(name)
                if not mapped:
                    raise RuntimeError(f"archive entry missing from content map: {container_id}!/{name}")
                expected_kind = mapped.get("kind")
                if member_kind == "file" and mapped.get("sha256") and mapped["sha256"] != sha256(raw):
                    raise RuntimeError(f"archive member digest mismatch: {container_id}!/{name}")
                if member_kind == "directory" and expected_kind != "archive-directory":
                    raise RuntimeError(f"archive directory kind mismatch: {container_id}!/{name}")
                if member_kind == "link" and (expected_kind != "archive-link" or mapped.get("link_target") != link_target):
                    raise RuntimeError(f"archive link metadata mismatch: {container_id}!/{name}")
                if member_kind == "special" and expected_kind != "archive-special-entry":
                    raise RuntimeError(f"archive special entry mismatch: {container_id}!/{name}")
                if expected_kind == "archive-member-container":
                    verify_container(mapped["id"], raw)
            if seen != set(expected):
                raise RuntimeError(f"archive member-set mismatch: {container_id}")

        for container_id, row in container_records.items():
            if row.get("kind") == "archive":
                verify_container(container_id, (ROOT / container_id).read_bytes())
        search_probe = connection.execute("SELECT rowid FROM search WHERE search MATCH ? LIMIT 1", ("CyberAlchemy",)).fetchone()
        if not search_probe:
            raise RuntimeError("full-text search probe did not match indexed repository content")
        return {"source_files": len(physical), "map_records": map_count, "archive_members": info.get("archive_member_count", 0), "statuses": dict(sorted(statuses.items())), "search_probe": True}
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate map and search index coverage")
    parser.add_argument("--search", help="search indexed paths and file contents")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    try:
        if args.search is not None:
            connection = sqlite3.connect(SEARCH_PATH)
            rows = connection.execute(
                "SELECT d.lookup,d.kind,d.status,d.summary,bm25(search) FROM search JOIN documents d ON d.id=search.rowid WHERE search MATCH ? ORDER BY bm25(search) LIMIT ?",
                (args.search, args.limit),
            ).fetchall()
            for lookup, kind, status, summary, rank in rows:
                print(json.dumps({"path": lookup, "kind": kind, "status": status, "preview": summary, "rank": rank}, ensure_ascii=False))
            connection.close()
            return 0
        if args.check:
            print(json.dumps(validate_map(), indent=2, ensure_ascii=False))
            return 0
        print(json.dumps(write_map(), indent=2, ensure_ascii=False))
        return 0
    except Exception as error:
        print(f"content map error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
