#!/usr/bin/env python3
"""Extract native PostgreSQL 16 test clients from one local image; no global install."""
import argparse
import hashlib
import json
from pathlib import Path
import shlex
import shutil
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--image", required=True, help="Existing local PostgreSQL 16 image or digest")
parser.add_argument("--target", required=True, help="New absolute directory for native clients and libraries")
args = parser.parse_args()
target = Path(args.target)
if not target.is_absolute() or target.exists():
    parser.error("--target must be a new absolute directory")


def run(command):
    return subprocess.run(command, capture_output=True, text=True, check=True, timeout=30).stdout.strip()


identity = json.loads(run(["docker", "image", "inspect", args.image]))[0]
if identity["Os"] != "linux" or identity["Architecture"] != "amd64":
    parser.error("native test clients require a linux/amd64 image")
image = identity["Id"]
libraries = [
    "libpq.so.5", "libreadline.so.8", "libssl.so.3", "libcrypto.so.3",
    "libgssapi_krb5.so.2", "libldap.so.2", "libtinfo.so.6", "libz.so.1",
    "libzstd.so.1", "libkrb5.so.3", "libk5crypto.so.3", "libcom_err.so.2",
    "libkrb5support.so.0", "liblber.so.2", "libsasl2.so.2", "libkeyutils.so.1",
]
target.parent.mkdir(parents=True, exist_ok=True)
target.mkdir()
container = None
success = False
try:
    for name in ("bin", "native", "lib"):
        (target / name).mkdir()
    container = run(["docker", "create", "--entrypoint", "sh", image, "-c", "true"])
    for name in ("psql", "pg_isready"):
        run(["docker", "cp", "-L", f"{container}:/usr/lib/postgresql/16/bin/{name}", str(target / "native" / name)])
    for name in libraries:
        run(["docker", "cp", "-L", f"{container}:/usr/lib/x86_64-linux-gnu/{name}", str(target / "lib" / name)])
    # Keep the host's glibc/loader. These wrappers execute the actual extracted clients.
    versions = {}
    for name in ("psql", "pg_isready"):
        wrapper = target / "bin" / name
        wrapper.write_text(
            "#!/bin/sh\nLD_LIBRARY_PATH=" + shlex.quote(str(target / "lib"))
            + '"${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" exec '
            + shlex.quote(str(target / "native" / name)) + ' "$@"\n'
        )
        wrapper.chmod(0o755)
        versions[name] = run([str(wrapper), "--version"])
        if "(PostgreSQL) 16." not in versions[name]:
            raise ValueError("extracted client is not PostgreSQL 16")
    manifest = {
        "schema_version": "craft.postgres-native-test-clients/v1", "authority_effect": "none",
        "image_id": image, "versions": versions, "bin_directory": str(target / "bin"),
        "global_install": False,
        "file_hashes": {str(file.relative_to(target)): hashlib.sha256(file.read_bytes()).hexdigest()
                        for file in target.rglob("*") if file.is_file()},
        "limits": "Pinned Debian-based PostgreSQL 16 image, linux/amd64 and compatible host glibc required.",
    }
    (target / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    success = True
    print(json.dumps({"result": "pass", "bin_directory": manifest["bin_directory"], "versions": versions}))
finally:
    try:
        if container:
            run(["docker", "rm", "-v", container])
    finally:
        if not success:
            shutil.rmtree(target)
