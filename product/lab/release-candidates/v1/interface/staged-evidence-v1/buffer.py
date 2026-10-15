"""Stage exact candidate evidence bytes, then publish outside a pure scope.

This class supplies no filesystem, policy, clock, permission or source adapter.
Its host independently selects the validator, writer and boundary check. The
aggregate bound covers temporary calculation output, never Agent Session notes.
"""
import hashlib

MAX_OBJECT_BYTES = 1024 * 1024
MAX_TOTAL_BYTES = 64 * 1024 * 1024
MAX_OBJECTS = 256


class EvidenceBuffer:
    def __init__(self, workspace_ref, validate_bytes):
        if type(workspace_ref) is not str or not workspace_ref or not callable(validate_bytes):
            raise ValueError('exact workspace and independent privacy validator required')
        self.workspace_ref = workspace_ref
        self.validate_bytes = validate_bytes
        self._objects = {}
        self._total = 0
        self.closed = False

    def object(self, raw):
        if self.closed:
            raise ValueError('evidence buffer is closed')
        if type(raw) is not bytes or len(raw) > MAX_OBJECT_BYTES:
            raise ValueError('exact bounded evidence bytes required')
        self.validate_bytes(raw)
        digest = hashlib.sha256(raw).hexdigest()
        old = self._objects.get(digest)
        if old is not None and old != raw:
            raise ValueError('staged evidence digest conflict')
        if old is None:
            if len(self._objects) >= MAX_OBJECTS or self._total + len(raw) > MAX_TOTAL_BYTES:
                raise ValueError('aggregate evidence staging budget exceeded')
            self._objects[digest] = raw
            self._total += len(raw)
        return {'ref': 'workspace-object:' + self.workspace_ref + ':' + digest,
                'sha256': digest}

    def commit(self, write_object, require_outside_scope):
        if self.closed:
            raise ValueError('evidence buffer is closed')
        try:
            require_outside_scope()
            for digest, raw in self._objects.items():
                # Recheck the boundary for every write, even after a writer error.
                require_outside_scope()
                self.validate_bytes(raw)
                if hashlib.sha256(raw).hexdigest() != digest:
                    raise ValueError('staged evidence bytes changed')
                expected = {'ref': 'workspace-object:' + self.workspace_ref + ':' + digest,
                            'sha256': digest}
                if write_object(raw) != expected:
                    raise ValueError('actual evidence writer binding differs')
        finally:
            self.discard()

    def discard(self):
        self._objects.clear()
        self._total = 0
        self.closed = True
