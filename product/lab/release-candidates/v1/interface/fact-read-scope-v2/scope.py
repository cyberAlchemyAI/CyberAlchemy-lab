"""Compose full source boundaries with uncached live policy checks.

Reuse the original sealed-copy implementation and its registered consumers.
No original function, callback, guard or module is replaced. The scope exists
only while a synchronous pure calculation and its policy checks run.
"""
from contextlib import contextmanager
import hashlib
import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'fact-read-scope-v1'
NAME = '_cal_lab_fact_read_scope_v1'
if NAME not in sys.modules:
    spec = importlib.util.spec_from_file_location(NAME, PARENT / '__init__.py',
                                                submodule_search_locations=[str(PARENT)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[NAME] = package
    spec.loader.exec_module(package)
K = __import__(NAME + '.scope', fromlist=['ReadScope'])
require = K.require
active_scope = K.active_scope
scope_for_source = K.scope_for_source
policy_scope = K.policy_scope
parent_guard = K.parent_guard
package_guard = K.package_guard
require_outside_scope = K.require_outside_scope

KERNEL = HERE / 'scope.py'
KERNEL_SHA = hashlib.sha256(KERNEL.read_bytes()).hexdigest()
PARENT_SHA = hashlib.sha256((PARENT / 'scope.py').read_bytes()).hexdigest()
ORIGINAL = (K.ReadScope, K.active_scope, K.policy_scope, K.require_outside_scope)
REGISTRY = K._active

def guard():
    require(Path(K.__file__).resolve() == PARENT / 'scope.py'
            and not KERNEL.is_symlink()
            and hashlib.sha256(KERNEL.read_bytes()).hexdigest() == KERNEL_SHA
            and hashlib.sha256((PARENT / 'scope.py').read_bytes()).hexdigest() == PARENT_SHA,
            'selected boundary or original copy kernel changed')
    require((K.ReadScope, K.active_scope, K.policy_scope, K.require_outside_scope) == ORIGINAL
            and K._active is REGISTRY, 'original scope callbacks or registry changed')

@contextmanager
def read_scope(parent, eligibility, channel, *, producer, package_checks=()):
    """Source facts and policy are separate obligations at both boundaries.

    Full parent and selected package guards establish source integrity. The
    original channel guard then reads its actual policy, revocation, Actor,
    limits and clock while borrowing only those sealed source facts. It never
    borrows permission. Full source exit guards run with no scope registered.
    A final real policy guard follows those checks and prevents return on drift.
    """
    guard()
    K.require_outside_scope()
    package_checks = tuple(package_checks)
    parent.guard()
    for checker, pin in package_checks:
        checker(pin)
    scope = K.ReadScope(parent, eligibility, channel, producer, package_checks)
    # The registry belongs to the unchanged original implementation. Its actual
    # consumers retain their exact identity checks and dispatch prohibition.
    # This private composition never accepts registry state from an API caller.
    REGISTRY.value = scope
    try:
        channel.guard()
        yield scope.snapshot
    finally:
        del REGISTRY.value
        errors = []
        def checked(callback):
            try:
                callback()
            except BaseException as error:
                errors.append(error)
        try:
            checked(scope.check)
            checked(parent.guard)
            for checker, pin in package_checks:
                checked(lambda checker=checker, pin=pin: checker(pin))
            checked(guard)
            # Recheck the copied facts after the full exit checks. Keep the
            # source facts available solely for this real final policy check.
            checked(scope.check)
            if not errors:
                REGISTRY.value = scope
                try:
                    checked(channel.guard)
                finally:
                    del REGISTRY.value
            else:
                # A failed source proof never enables borrowed selection, even
                # for cleanup. Retain the ordinary full channel exit check.
                checked(channel.guard)
        finally:
            scope.closed = True
        if errors:
            raise errors[0]
