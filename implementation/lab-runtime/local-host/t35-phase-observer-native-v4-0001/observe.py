"""Explicit, bounded T35 callback and pure-scope boundary observations.

This is a test/driver helper. It never replaces a selected callback or changes
the fact-scope kernel, permission, Source period, or lease. Only calls routed
through this helper are counted; it cannot infer hidden nested callbacks.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import inspect
import json
from pathlib import Path
import sys
import time
from types import MappingProxyType
import types


class BoundaryRefusal(ValueError):
    pass


API_SOURCE_MANIFEST = "product/lab/release-candidates/v1/interface/api-integration-v33-t03-one-lesson-native-v4-0004/source-manifest.json"
API_SOURCE_SHA256 = "822bef0481a1ce2e050be1324a1059e9bd3f018b96fb290fb10776fbc648bc64"
API = "product/lab/release-candidates/v1/interface/api-integration-v33-t03-one-lesson-native-v4-0004/"
EXPECTED_BOUNDARIES = {
    "Service.call": ("callback", API + "service.py", "Service.call"),
    "Service._call": ("callback", API + "service.py", "Service._call"),
    "MachinePeer.call": ("callback", API + "machine_transport.py", "MachinePeer.call"),
    "ReaderChannel.guard": ("callback", API + "auth.py", "ReaderChannel.guard"),
    "ReaderChannel.policy_guard": ("callback", API + "auth.py", "ReaderChannel.policy_guard"),
    "ReaderChannel.termination_guard": ("callback", API + "auth.py", "ReaderChannel.termination_guard"),
    "LiveReader.guard": ("callback", API + "current_context_sessions.py", "LiveReader.guard"),
    "PermissionBridge.guard": ("callback", API + "current_context_sessions.py", "PermissionBridge.guard"),
    "ContextSessions.delivery": ("callback", API + "current_context_sessions.py", "ContextSessions.delivery"),
    "SessionAttachment.guard": ("callback", API + "session_attachment.py", "SessionAttachment.guard"),
    "FACT_SCOPE.read_scope": ("pure_scope", "product/lab/release-candidates/v1/interface/fact-read-scope-v1/scope.py", "read_scope"),
    "model_read_batch": ("pure_scope", API + "guarded_reads.py", "model_read_batch"),
    "participation_snapshot": ("pure_scope", API + "guarded_reads.py", "participation_snapshot"),
    "Vault.lock": ("pure_scope", API + "workspace.py", "Vault.lock"),
    "ApplicationJournal.lock": ("pure_scope", API + "application_journal.py", "ApplicationJournal.lock"),
}


@dataclass(frozen=True)
class Selection:
    name: str
    kind: str
    path: Path
    sha256: str
    qualname: str


_SEAL = object()


class VerifiedBoundaries:
    """A closed source selection, or an explicitly non-qualifying test fixture."""

    __slots__ = ("rows", "release_pin", "fixture_only", "_frozen")

    def __setattr__(self, name, value):
        if getattr(self, "_frozen", False):
            raise BoundaryRefusal("VERIFIED_SELECTION_IMMUTABLE")
        object.__setattr__(self, name, value)

    def __init__(self, rows: dict[str, Selection], release_pin: str,
                 fixture_only: bool, seal):
        if seal is not _SEAL or not isinstance(rows, dict) or not rows:
            raise BoundaryRefusal("VERIFIED_SELECTION_REQUIRED")
        self.rows = MappingProxyType(dict(rows))
        self.release_pin = release_pin
        self.fixture_only = fixture_only
        self._frozen = True

    @classmethod
    def fixture(cls, *rows: Selection):
        if not rows or len({row.name for row in rows}) != len(rows):
            raise BoundaryRefusal("FIXTURE_SELECTION_REFUSED")
        return cls({row.name: row for row in rows}, "fixture-only", True, _SEAL)

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, name):
        return self.rows[name]


def verify_boundary_selection(path: Path, reviewed_sha256: str, root: Path) -> VerifiedBoundaries:
    """Cold-select exact candidate bytes; does not activate instrumentation."""
    if (not isinstance(reviewed_sha256, str) or len(reviewed_sha256) != 64
            or any(letter not in "0123456789abcdef" for letter in reviewed_sha256)
            or not path.is_file() or path.is_symlink() or path.resolve() != path
            or hashlib.sha256(path.read_bytes()).hexdigest() != reviewed_sha256):
        raise BoundaryRefusal("BOUNDARY_RELEASE_PIN_REFUSED")
    selected = json.loads(path.read_bytes())
    if (set(selected) != {"schema_version", "measurement_activated", "authority_effect", "claim_ceiling",
                          "api_source_manifest_binding", "boundaries"}
            or selected["schema_version"] != "lab-t35-explicit-boundary-selection/v1-candidate"
            or selected["measurement_activated"] is not False
            or selected["authority_effect"] != "none"
            or selected["api_source_manifest_binding"] !=
               {"path": API_SOURCE_MANIFEST, "sha256": API_SOURCE_SHA256}):
        raise BoundaryRefusal("BOUNDARY_SELECTION_CONTRACT_REFUSED")
    manifest = root / API_SOURCE_MANIFEST
    if (not manifest.is_file() or manifest.is_symlink()
            or hashlib.sha256(manifest.read_bytes()).hexdigest() != API_SOURCE_SHA256):
        raise BoundaryRefusal("BOUNDARY_API_SOURCE_REFUSED")
    source_rows = json.loads(manifest.read_bytes()).get("files")
    if not isinstance(source_rows, list):
        raise BoundaryRefusal("BOUNDARY_API_SOURCE_REFUSED")
    source_bindings = {row["path"]: row["sha256"] for row in source_rows
                       if isinstance(row, dict) and set(row) == {"path", "sha256"}}
    if len(source_bindings) != len(source_rows):
        raise BoundaryRefusal("BOUNDARY_API_SOURCE_REFUSED")
    rows = selected["boundaries"]
    if (not isinstance(rows, list) or len(rows) != len(EXPECTED_BOUNDARIES)
            or len({row.get("name") for row in rows if isinstance(row, dict)}) != len(rows)):
        raise BoundaryRefusal("BOUNDARY_INVENTORY_REFUSED")
    result = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"name", "kind", "path", "sha256", "qualname"}:
            raise BoundaryRefusal("BOUNDARY_ROW_SHAPE_REFUSED")
        expected = EXPECTED_BOUNDARIES.get(row["name"])
        if expected != (row["kind"], row["path"], row["qualname"]):
            raise BoundaryRefusal("BOUNDARY_ROW_SELECTION_REFUSED")
        if row["path"].startswith(API) and source_bindings.get(row["path"]) != row["sha256"]:
            raise BoundaryRefusal("BOUNDARY_API_ROW_REFUSED")
        source = root / row["path"]
        if (not source.is_file() or source.is_symlink() or source.resolve() != source
                or hashlib.sha256(source.read_bytes()).hexdigest() != row["sha256"]):
            raise BoundaryRefusal("BOUNDARY_ROW_BYTE_REFUSED")
        result[row["name"]] = Selection(row["name"], row["kind"], source, row["sha256"], row["qualname"])
    if set(result) != set(EXPECTED_BOUNDARIES):
        raise BoundaryRefusal("BOUNDARY_INVENTORY_REFUSED")
    return VerifiedBoundaries(result, reviewed_sha256, False, _SEAL)


def _utc(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise BoundaryRefusal("OBSERVED_DEADLINE_REQUIRED")
    return value.astimezone(timezone.utc)


def _same_callable(actual, expected) -> bool:
    if inspect.ismethod(actual) or inspect.ismethod(expected):
        return (inspect.ismethod(actual) and inspect.ismethod(expected)
                and actual.__self__ is expected.__self__
                and actual.__func__ is expected.__func__)
    return actual is expected


def _function(value):
    return inspect.unwrap(value.__func__ if inspect.ismethod(value) else value)


def _codes(code):
    yield code
    for value in code.co_consts:
        if isinstance(value, types.CodeType):
            yield from _codes(value)


def _code_signature(code):
    def constant(value):
        if isinstance(value, types.CodeType):
            return ("code", _code_signature(value))
        if type(value) in (str, bytes, int, float, complex, bool, type(None)):
            return (type(value).__name__, value)
        if value is Ellipsis:
            return ("ellipsis",)
        if type(value) is slice:
            return ("slice", constant(value.start), constant(value.stop), constant(value.step))
        if type(value) is tuple:
            return ("tuple", tuple(constant(item) for item in value))
        if type(value) is frozenset:
            return ("frozenset", tuple(sorted((constant(item) for item in value), key=repr)))
        raise BoundaryRefusal("BOUNDARY_CODE_CONSTANT_REFUSED")
    fields = ("co_argcount", "co_posonlyargcount", "co_kwonlyargcount", "co_nlocals", "co_stacksize",
              "co_flags", "co_code", "co_names", "co_varnames", "co_freevars", "co_cellvars",
              "co_filename", "co_name", "co_qualname", "co_firstlineno", "co_linetable", "co_exceptiontable")
    return tuple(getattr(code, field) for field in fields) + (tuple(constant(v) for v in code.co_consts),)


def _module_member(function):
    module = sys.modules.get(function.__module__)
    if module is None:
        raise BoundaryRefusal("BOUNDARY_MODULE_ORIGIN_REFUSED")
    member = module
    for part in function.__qualname__.split("."):
        if part == "<locals>" or not hasattr(member, part):
            raise BoundaryRefusal("BOUNDARY_MODULE_ORIGIN_REFUSED")
        member = getattr(member, part)
    return inspect.unwrap(member)


def verify_selection(selection: Selection, actual, expected, kind: str,
                     *, fixture_only: bool = False) -> None:
    if not isinstance(selection, Selection) or selection.kind != kind or not selection.name:
        raise BoundaryRefusal("BOUNDARY_SELECTION_SHAPE_REFUSED")
    if not _same_callable(actual, expected):
        raise BoundaryRefusal("BOUNDARY_CALLBACK_IDENTITY_REFUSED")
    function = _function(actual)
    path = selection.path
    if (not isinstance(path, Path) or not path.is_absolute() or not path.is_file()
            or path.is_symlink() or path.resolve() != path
            or not hasattr(function, "__code__")
            or Path(function.__code__.co_filename).resolve() != path
            or function.__qualname__ != selection.qualname
            or hashlib.sha256(path.read_bytes()).hexdigest() != selection.sha256):
        raise BoundaryRefusal("BOUNDARY_CALLBACK_ORIGIN_REFUSED")
    if not fixture_only and _module_member(function) is not function:
        raise BoundaryRefusal("BOUNDARY_MODULE_ORIGIN_REFUSED")
    source_codes = [code for code in _codes(compile(path.read_bytes(), str(path), "exec", dont_inherit=True))
                    if code.co_qualname == selection.qualname]
    if len(source_codes) != 1 or _code_signature(function.__code__) != _code_signature(source_codes[0]):
        raise BoundaryRefusal("BOUNDARY_CALLBACK_CODE_REFUSED")


class BoundaryLedger:
    """Record only explicitly selected boundaries under actual UTC deadlines."""

    def __init__(self, case_id: str, source_expires_at: datetime,
                 verified: VerifiedBoundaries):
        if not isinstance(case_id, str) or not case_id:
            raise BoundaryRefusal("CASE_ID_REQUIRED")
        if not isinstance(verified, VerifiedBoundaries):
            raise BoundaryRefusal("VERIFIED_SELECTION_REQUIRED")
        self.case_id = case_id
        self.source_expires_at = _utc(source_expires_at)
        self.verified = verified
        self.events: list[dict] = []

    def _selected(self, selection: Selection, kind: str):
        if (not isinstance(selection, Selection) or
                self.verified.rows.get(selection.name) is not selection or
                selection.kind != kind):
            raise BoundaryRefusal("CLOSED_BOUNDARY_SELECTION_REFUSED")

    def _start(self, selection: Selection, deadline: datetime):
        lease_end = _utc(deadline)
        effective_end = min(lease_end, self.source_expires_at)
        now = datetime.now(timezone.utc)
        start_ns = time.monotonic_ns()
        if now >= effective_end:
            self.events.append({"name": selection.name, "kind": selection.kind,
                                "started_at_utc": now.isoformat(), "completed_at_utc": now.isoformat(),
                                "monotonic_elapsed_seconds": 0.0,
                                "strictest_observed_expires_at": effective_end.isoformat(),
                                "status": "REFUSED_EXPIRED_BEFORE", "exception_class": None,
                                "expired_at_completion": True})
            raise BoundaryRefusal("OBSERVED_DEADLINE_EXPIRED_BEFORE")
        return now, start_ns, effective_end

    def _finish(self, selection: Selection, start, error: BaseException | None,
                scope_boundaries: int = 0):
        begun, start_ns, effective_end = start
        ended = datetime.now(timezone.utc)
        expired = ended >= effective_end
        status = ("CALLBACK_RAISED" if error is not None else
                  "EXPIRED_AFTER" if expired else "PASS")
        self.events.append({"name": selection.name, "kind": selection.kind,
                            "started_at_utc": begun.isoformat(), "completed_at_utc": ended.isoformat(),
                            "monotonic_elapsed_seconds": (time.monotonic_ns() - start_ns) / 1e9,
                            "strictest_observed_expires_at": effective_end.isoformat(),
                            "status": status, "exception_class": type(error).__name__ if error else None,
                            "expired_at_completion": expired,
                            "pure_scope_boundaries_observed": scope_boundaries})
        if error is None and expired:
            raise BoundaryRefusal("OBSERVED_DEADLINE_EXPIRED_AFTER")

    def callback(self, selection: Selection, actual, expected, deadline: datetime, *args, **kwargs):
        self._selected(selection, "callback")
        verify_selection(selection, actual, expected, "callback", fixture_only=self.verified.fixture_only)
        start = self._start(selection, deadline)
        try:
            result = actual(*args, **kwargs)
        except BaseException as error:
            self._finish(selection, start, error)
            raise
        self._finish(selection, start, None)
        return result

    @contextmanager
    def pure_scope(self, selection: Selection, actual, expected, deadline: datetime, *args, **kwargs):
        self._selected(selection, "pure_scope")
        verify_selection(selection, actual, expected, "pure_scope", fixture_only=self.verified.fixture_only)
        start = self._start(selection, deadline)
        entered = False
        exit_attempted = False
        try:
            with actual(*args, **kwargs) as value:
                entered = True
                try:
                    yield value
                finally:
                    exit_attempted = True
        except BaseException as error:
            self._finish(selection, start, error, int(entered) + int(exit_attempted))
            raise
        self._finish(selection, start, None, int(entered) + int(exit_attempted))

    def result(self) -> dict:
        return {"schema_version": "lab-t35-explicit-boundary-observation/v1",
                "case_id": self.case_id,
                "boundary_selection_sha256": self.verified.release_pin,
                "measurement_class": "fixture-only" if self.verified.fixture_only else "selected-candidate",
                "claim_ceiling": "Only explicitly routed callbacks and pure-scope entry/exit are counted; caller-supplied deadlines are not issuer-authenticated; expiry after work does not prove rollback; nested and unobserved callbacks remain unknown.",
                "source_expires_at": self.source_expires_at.isoformat(),
                "callback_count": sum(row["kind"] == "callback" and row["status"] != "REFUSED_EXPIRED_BEFORE"
                                      for row in self.events),
                "pure_scope_boundary_count": sum(row.get("pure_scope_boundaries_observed", 0)
                                                 for row in self.events),
                "events": list(self.events),
                "authority_effect": "none"}
