"""Adapt unselected native Source code to external protected archive custody."""

import ast
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE = "implementation/lab-runtime/local-host/source8-current-fixture/engine-v3"


def replace_one(value, old, new):
    if value.count(old) != 1:
        raise ValueError("PRIVATE_ARCHIVE_PREIMAGE_REFUSED " + old[:70])
    return value.replace(old, new)


class Hardener:
    def __init__(self, retained, private_archive):
        self.retained = retained
        self.private_archive = Path(private_archive)
        if not self.private_archive.is_absolute():
            raise ValueError("PRIVATE_ARCHIVE_ABSOLUTE_REQUIRED")

    def harden(self, role, filename, text, role_value):
        text = self.retained.harden(role, filename, text, role_value)
        if role == "source" and filename == "base.py":
            text = replace_one(text,
                "(ROOT/'product/lab/release-candidates/v1/interface')/'custody-correction-v4/loader.py'",
                "(ROOT/'" + ENGINE + "/loader.py')")
            text = replace_one(text,
                "(ROOT/'product/lab/release-candidates/v1/interface')/'custody-correction-v4/pins.json'",
                "(ROOT/'" + ENGINE + "/pins.json')")
            text = replace_one(text, "    _capture_identity();return raw\ndef verify_source(pin):",
                "    _capture_identity()\n"
                "    if row['path']==ARCHIVE_HANDLE_REF:_external_archive_bytes(parse(raw))\n"
                "    return raw\n"
                "ARCHIVE_HANDLE_REF=(HERE/'packages/0001/archive-handle.json').relative_to(ROOT).as_posix()\n"
                "PRIVATE_ARCHIVE=Path(" + repr(str(self.private_archive)) + ")\n"
                "def _external_archive_bytes(handle):\n"
                "    import stat\n"
                "    require(type(handle) is dict and set(handle)=={'schema','path','sha256'} and "
                "handle['schema']=='cal-source8-private-archive-handle/v1' and "
                "handle['path']==str(PRIVATE_ARCHIVE),'private archive handle differs')\n"
                "    require(PRIVATE_ARCHIVE.is_file() and not PRIVATE_ARCHIVE.is_symlink() and "
                "not PRIVATE_ARCHIVE.resolve().is_relative_to(ROOT) and "
                "PRIVATE_ARCHIVE.parent.is_dir() and not PRIVATE_ARCHIVE.parent.is_symlink(),"
                "'private archive origin differs')\n"
                "    parent=PRIVATE_ARCHIVE.parent.stat();item=PRIVATE_ARCHIVE.stat()\n"
                "    require(parent.st_uid==os.getuid() and stat.S_IMODE(parent.st_mode)==0o700 "
                "and item.st_uid==os.getuid() and stat.S_IMODE(item.st_mode)==0o600 "
                "and item.st_size<=64*1024*1024,'private archive custody differs')\n"
                "    raw=PRIVATE_ARCHIVE.read_bytes()\n"
                "    require(sha(raw)==handle['sha256'],'private archive digest differs')\n"
                "    return raw\n"
                "def external_archive(row):return _external_archive_bytes(parse(original(row)))\n"
                "def verify_source(pin):")
        if role == "source" and filename == "build.py":
            text = replace_one(text, "OLD_PERIOD=(ROOT/'product/lab/release-candidates/v1/interface')/'current-participation-v5/packages/0001/period.json'",
                "OLD_PERIOD=(ROOT/'product/lab/release-candidates/v1/interface')/'current-participation-v5/packages/0001/period.json'\n"
                "PRIVATE_ARCHIVE=Path(" + repr(str(self.private_archive)) + ")\n"
                "def emit_private(value):\n"
                "    import stat\n"
                "    parent=PRIVATE_ARCHIVE.parent\n"
                "    require(parent.is_dir() and not parent.is_symlink() and not parent.resolve().is_relative_to(ROOT),"
                "'private archive root differs')\n"
                "    meta=parent.stat()\n"
                "    require(meta.st_uid==os.getuid() and stat.S_IMODE(meta.st_mode)==0o700,"
                "'private archive parent owner/mode differs')\n"
                "    fd=os.open(PRIVATE_ARCHIVE,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)\n"
                "    with os.fdopen(fd,'wb') as stream:\n"
                "        raw=encoded(value)\n"
                "        require(stream.write(raw)==len(raw),'private archive short write')\n"
                "        stream.flush();os.fsync(stream.fileno())\n")
            text = replace_one(text, "finally:emit(out/'branch.snapshot',archive(store,pins))",
                               "finally:emit_private(archive(store,pins))")
            text = replace_one(text, "    files=[binding(path) for path in sorted(out.rglob('*')) if path.is_file()]",
                "    emit(out/'archive-handle.json',{'schema':'cal-source8-private-archive-handle/v1',"
                "'path':str(PRIVATE_ARCHIVE),'sha256':sha(PRIVATE_ARCHIVE.read_bytes())})\n"
                "    files=[binding(path) for path in sorted(out.rglob('*')) if path.is_file()]")
            text = replace_one(text, "'archive_binding':binding(out/'branch.snapshot')",
                               "'archive_binding':binding(out/'archive-handle.json')")
        if role == "source" and filename == "cold.py":
            text = replace_one(text,
                "    require((ROOT/manifest['archive_binding']['path']).stat().st_size<=64*1024*1024,'bounded original source archive required')\n"
                "    archive=parse(original(manifest['archive_binding']))",
                "    archive=parse(external_archive(manifest['archive_binding']))")
        ast.parse(text)
        return text
