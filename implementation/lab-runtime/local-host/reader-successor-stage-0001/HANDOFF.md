# Reader successor stage 0001 — actual Source binding, effect disabled

Status: **ready for independent exact-byte static review; private stage effect
disabled**. The candidate binds the independently reviewed actual Source
one-shot, not a synthetic package. The Source effect review at
`context-successor-source-independent-effect-review-0001/review.json` has
SHA-256 `599d7cca4b87b98809e33636ad1326bc60ddba589123ec5a0a0c5e00b58a4440`.
The independently reviewed Reader selection-only release 0001 review has
SHA-256 `a593c8fbedb44c0941d578c2afb5b401f878f7d1990a1a86b4a0a788d3fd8b58`.
The actual package manifest is
`bdb5eac92cbb3f96857c4d2ccb00880441d55fb8f1dbbeb5cdaae8d81c720653`,
Source terminal is
`66c51614278e38e061eac7cc195288444efa176f36f13dd4243462faaa34c7b9`,
Reader manifest is
`048ef6c1f54387fc6e593f38b29723cb06f84649f12e9c75a0340d389b0f5756`,
and the exact 986-file stage plan is
`a5ee5e9812c4ab5d0e37b7fe99aec4f334dcb583668ad0489f267f7e2258478b`.

`stage.py --preflight` reselects the current Source manifests, period,
terminal and reviewed JSON through the frozen selector, compares the complete
plan and all eight generated Reader files, checks all selected source file
metadata, and hashes all 985 non-archive inputs. The protected
`branch.snapshot` body remains unopened. The live preflight reports 986 files,
33,413,752 selected bytes, current period, owner-only state parent, available
capacity and an unoccupied stage attempt. The selected durable attempt is
`/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/reader-stage-attempt`.
The stage root will contain 986 files and exactly the derived directory set,
including an empty private Source `receipts` directory. Its private package
files and package directories remain owner-only.

The future stage effect must be released in a disjoint reviewed successor;
`STAGE_RELEASE_ENABLED` is false here. That successor may use the exact
`stage.py` implementation after independent review. It claims a fresh 0700
attempt and writes an exclusive, durable consumed marker before the first
private archive read. It copies each selected file with held no-follow
ancestor descriptors, streams and hashes the archive while copying, reads
back each destination, and verifies the complete staged namespace and bytes
before and after a durable stage-only terminal. Any failure retains the
partial owner-only attempt and writes UNKNOWN where possible; no retry or
replacement is allowed. An external command observer must capture exit zero
and independently review the terminal and retained stage before Reader use.

Normal and optimized tests each pass **5/5**. They exercise the actual dynamic
Source binding and no-archive preflight, consumed attempt refusal, symlink
namespace rejection, effect refusal, and a post-create fault that retains an
UNKNOWN receipt in an already claimed owner-only attempt. The held-FD copy primitive is
byte-identical to reviewed `fresh-reader-docker-0008/anchored_copy.py` at
SHA-256 `0ada376b91b42651bec89602f2318ae39d369773e05b19eab0e1134fd8335259`.
No stage copy, Docker create, Reader cold-open, or protected Source8 authority
effect has occurred in this candidate. A Reader Docker release must later
freshly verify the staged 986 files and Source period, bind a compatible new
entrypoint and controller, observe image/UID/mount and exclusive name through
the external OS, enforce no retry, and obtain independent effect review.
