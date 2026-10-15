"""Externally pinned, original-byte native ontology read adapter."""
from __future__ import annotations
import copy
from dataclasses import dataclass
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from lab_runtime.common import byte_digest, digest, encoded, loads, require


def regular(path):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), 'native material must be a regular file')
    require(not any(p.is_symlink() for p in path.parents), 'native material symlink ancestor')
    return path.read_bytes()


def closure(directory):
    directory = Path(directory)
    require(directory.is_dir() and not directory.is_symlink(), 'native event directory required')
    result = {}
    for path in sorted(directory.iterdir()):
        require(path.name.endswith('.json'), 'native event closure contains unexpected material')
        raw = regular(path)
        require(len(raw) <= 8 * 1024 * 1024, 'native event byte budget exceeded')
        result[path.name] = raw
        require(len(result) <= 1000, 'native event count budget exceeded')
    require(result, 'native event closure is empty')
    return result


@dataclass(frozen=True)
class NativePins:
    executable_sha256: str
    semantic_files_digest: str
    governance_files_digest: str
    request_sha256: str
    semantic_cursor: int
    governance_cursor: int
    projection_digest: str


class NativeReadStore:
    """No sealing, append, activation or authority methods on the read adapter."""
    def __init__(self, semantic_directory, governance_directory, request, executable, pins):
        require(isinstance(pins, NativePins), 'independent native read pins required')
        self.semantic_directory = Path(semantic_directory)
        self.governance_directory = Path(governance_directory)
        self.executable = Path(executable)
        self.request = copy.deepcopy(request)
        self.pins = pins

    def read(self):
        semantic = closure(self.semantic_directory)
        governance = closure(self.governance_directory)
        require(sum(map(len, semantic.values())) + sum(map(len, governance.values())) <= 32*1024*1024, 'native history byte budget exceeded')
        shas = lambda values: {k: byte_digest(v) for k, v in values.items()}
        require(digest(shas(semantic)) == self.pins.semantic_files_digest, 'native semantic history changed')
        require(digest(shas(governance)) == self.pins.governance_files_digest, 'native governance history changed')
        require(byte_digest(regular(self.executable)) == self.pins.executable_sha256, 'native executable changed')
        raw_request = encoded(self.request)
        require(byte_digest(raw_request) == self.pins.request_sha256, 'native request pin mismatch')
        require(type(self.pins.semantic_cursor) is int and type(self.pins.governance_cursor) is int, 'native cursor must be integer')
        require(self.request['selector']['semantic_cursor'] == self.pins.semantic_cursor and self.request['governance_cursor'] == self.pins.governance_cursor, 'native cursor pin mismatch')
        # Verify a copied immutable byte snapshot, then recheck the original closure.
        with TemporaryDirectory(prefix='lab-native-read-') as temp:
            stage = Path(temp)
            for name, values in [('semantic', semantic), ('governance', governance)]:
                (stage/name).mkdir()
                for filename, raw in values.items(): (stage/name/filename).write_bytes(raw)
            (stage/'request.json').write_bytes(raw_request)
            process = subprocess.run([str(self.executable), str(stage/'semantic'), str(stage/'governance'), str(stage/'request.json')], capture_output=True, timeout=30)
        require(process.returncode == 0, 'native replay rejected: '+process.stderr.decode('utf-8', errors='replace')[:2000])
        result = loads(process.stdout)
        require(digest(result) == self.pins.projection_digest, 'native projection pin mismatch')
        require(result['schema_version'] == 'lab-native-context-read/v1-candidate' and result['authority_effect'] == 'none', 'native projection envelope mismatch')
        require(result['cut']['semantic_cursor'] == self.pins.semantic_cursor and result['governance_cursor'] == self.pins.governance_cursor, 'native replay cursor mismatch')
        require(closure(self.semantic_directory) == semantic and closure(self.governance_directory) == governance, 'native history changed during replay')
        require(byte_digest(regular(self.executable)) == self.pins.executable_sha256, 'native executable changed during replay')
        return copy.deepcopy(result)
