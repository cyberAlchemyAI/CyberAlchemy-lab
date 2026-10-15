"""Sealed fact copies with original source guards at operation boundaries.

Only a synchronous pure calculation may use a scope. The selected producer,
source objects, channel and package callbacks are private host selections. No
public request can declare them. No original callback is replaced, no permission
is cached, and no expiry, Assignment period or source is renewed.
"""
import copy
import hashlib
import threading
from contextlib import contextmanager
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_KERNEL = _HERE / 'scope.py'
_KERNEL_SHA = hashlib.sha256(_KERNEL.read_bytes()).hexdigest()
_active = threading.local()


def require(value, reason):
    if not value:
        raise ValueError(reason)


class ReadScope:
    def __init__(self, parent, eligibility, channel, producer, package_checks):
        require(type(parent) is producer.reader.adapter.SignedSources,
                'scope requires the actual selected SignedSources class')
        require(eligibility is producer.EL is producer.reader.adapter.eligibility,
                'scope eligibility selection differs')
        require(channel.source is parent, 'scope channel names another source')
        require(all(callable(checker) and type(pin) is str and len(pin) == 64
                    for checker, pin in package_checks), 'closed package checks required')
        self.parent = parent; self.eligibility = eligibility
        self.channel = channel; self.host = getattr(channel, 'channel', channel)
        self.producer = producer; self.package_checks = tuple(package_checks)
        self.thread = threading.get_ident(); self.closed = False
        self.original_sources = parent.sources
        self.original_callback = parent.sources.current_guard
        self.original_parent_callback = parent.guard
        self.original_channel_callback = channel.guard
        self.kernel_sha = _KERNEL_SHA
        self.scope_ref = parent.sources.scope_ref
        self.source_cut = copy.deepcopy(parent.sources.source_cut)
        self.records = copy.deepcopy(list(parent.sources.records.values()))
        self.schemas = copy.deepcopy(list(parent.sources.schemas.values()))
        self.record_stamp = parent.record_stamp
        self.schema_stamp = parent.schema_stamp
        self.expected_records = self.record_stamp(self.records)
        self.expected_schemas = self.schema_stamp(self.schemas)
        self.snapshot = None
        # The guard belongs solely to the new copy. Original ExactSources keeps
        # its full current_guard before, during and after this calculation.
        self.local_callback = self.check
        self.snapshot = eligibility.ExactSources(self.scope_ref, self.source_cut,
                                                self.records, self.schemas,
                                                self.local_callback)
        self.check()

    def check(self):
        require(not self.closed and threading.get_ident() == self.thread,
                'fact scope is closed or belongs to another thread')
        require(_KERNEL_SHA == self.kernel_sha and not _KERNEL.is_symlink()
                and hashlib.sha256(_KERNEL.read_bytes()).hexdigest() == self.kernel_sha,
                'fact scope kernel changed')
        require(self.parent.sources is self.original_sources
                and self.parent.guard == self.original_parent_callback
                and self.original_sources.current_guard == self.original_callback
                and self.channel.source is self.parent
                and self.channel.guard == self.original_channel_callback,
                'fact scope original source or callbacks changed')
        require(self.original_sources.scope_ref == self.scope_ref
                and self.original_sources.source_cut == self.source_cut,
                'fact scope original source scope or cut changed')
        snapshot = self.snapshot
        if snapshot is None:
            return True
        require(snapshot.scope_ref == self.scope_ref and snapshot.source_cut == self.source_cut
                and snapshot.current_guard == self.local_callback,
                'fact scope copied scope, cut or callback changed')
        require(self.record_stamp(snapshot.records.values()) == self.expected_records,
                'fact scope copied original records changed')
        require(self.schema_stamp(snapshot.schemas.values()) == self.expected_schemas
                and set(snapshot.validators) == set(snapshot.schemas)
                and all(self.producer.encoded(validator.schema) ==
                        self.producer.encoded(self.producer.EL.parse(snapshot.schemas[key].original_schema))
                        for key, validator in snapshot.validators.items()),
                'fact scope copied schemas or validators changed')
        return True


def active_scope():
    value = getattr(_active, 'value', None)
    if value is not None:
        value.check()
    return value


def scope_for_source(parent):
    value = active_scope()
    if value is None:
        return None
    require(value.parent is parent, 'fact scope selects another source')
    return value


def policy_scope(host):
    """Only the exact registered host can borrow the copied source selection.

The host must still read and verify its actual policy on every permission call.
This function supplies no permission, Actor, role, deadline or grant.
"""
    value = active_scope()
    if value is None:
        return None
    require(host is value.host, 'fact scope selects another host channel')
    return value


def parent_guard(parent):
    value = scope_for_source(parent)
    return parent.guard() if value is None else value.check()


def package_guard(parent, checker, pin):
    value = scope_for_source(parent)
    if value is None:
        return checker(pin)
    require(any(original is checker and selected == pin
                for original, selected in value.package_checks),
            'package check was not selected at this fact scope boundary')
    return value.check()


def require_outside_scope():
    require(getattr(_active, 'value', None) is None,
            'API dispatch and durable effects cannot run inside a pure fact scope')


@contextmanager
def read_scope(parent, eligibility, channel, *, producer, package_checks=()):
    require_outside_scope()
    package_checks = tuple(package_checks)
    # Full checks are real original calls; there is no shared digest/mtime cache.
    parent.guard()
    for checker, pin in package_checks:
        checker(pin)
    channel.guard()
    scope = ReadScope(parent, eligibility, channel, producer, package_checks)
    parent.guard()
    channel.guard()
    _active.value = scope
    try:
        yield scope.snapshot
    finally:
        # Full exit checks run with the scope unavailable. A failed copied or
        # original-source guard prevents return of the pure result to its writer.
        del _active.value
        try:
            scope.check()
        finally:
            scope.closed = True
            try:
                parent.guard()
            finally:
                try:
                    for checker, pin in package_checks:
                        checker(pin)
                finally:
                    channel.guard()
