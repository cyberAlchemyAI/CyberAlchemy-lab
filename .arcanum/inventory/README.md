# Repository inventory

This package provides the repository's generated, path-complete index. The
source repository is the authority; this package is a navigation and lookup
layer that points back to source paths.

## Contents

- [`index.md`](index.md) is the human-readable repository map and file-type rollup.
- [`inventory.json`](inventory.json) lists every included file with its path,
  Git tracking state, file kind, byte size, extension, and SHA-256 digest. It
  also includes counts for each directory prefix.
- [`content-map.jsonl.gz`](content-map.jsonl.gz) maps the contents of each
  included file and every member found inside repository TAR archives. It
  records format-aware structure such as Markdown sections, JSON/YAML/TOML
  field paths, code declarations, prose spans, and PDF pages.
- [`content-search.sqlite3`](content-search.sqlite3) is a full-text search
  index for extracted text, including text from TAR archive members and PDFs.
- [`queries/definitions-status.md`](queries/definitions-status.md) explains how
  to read the current governed Definition registry and candidate history.
- [`queries/cyberalchemy-v2-migration-decisions.md`](queries/cyberalchemy-v2-migration-decisions.md)
  traces the migration decision chain and its current execution boundary.
- [`queries/governance-repository-map.md`](queries/governance-repository-map.md)
  connects the complete path inventory to the candidate governance module and its exact status routes.
- [`schema.md`](schema.md) records scope, fields, and refresh rules.
- [`tags.md`](tags.md) defines the controlled area and artifact labels used by
  this index.
- [`log.md`](log.md) records inventory refreshes.

The manifest covers tracked files and present, non-ignored untracked files.
It excludes `.git/`, Git-ignored paths, empty directories, and the manifest
itself because a manifest cannot include its own stable digest. Symlinks are
hashed by their link-target text without following them. A refresh includes
new repository files automatically.

## Refresh

From the repository root, run:

```sh
python3 tooling/inventory/build_inventory.py
```

Install the content-mapping parsers and build the structural map plus full-text
search index:

```sh
python3 -m pip install -r .arcanum/inventory/requirements.txt
python3 tooling/inventory/build_content_map.py
```

Then check both generated indexes and source coverage with:

```sh
python3 tooling/inventory/build_inventory.py --check
python3 tooling/inventory/build_content_map.py --check
```

Search the extracted corpus with:

```sh
python3 tooling/inventory/build_content_map.py --search 'tenant isolation'
```

The maps are deterministic for the current working tree and installed parser
versions. Raw source files are never modified. Binary records include format
metadata, available sections or members, image dimensions when recognized,
printable strings, and byte digests. The raw binary payload remains in its
source file and is not copied into the text-search index.
