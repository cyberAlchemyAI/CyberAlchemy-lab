"""Disjoint conformance composition; preserves full native callbacks, so no speedup claim.

Only a trusted successor can select these callbacks. This module never replaces
the selected native implementation or the API33 fact-scope registry.
"""

import datetime as dt
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Callable

from probe import need, verify_boundary


@dataclass(frozen=True)
class OriginalChecks:
    source_semantic: Callable[[], object]
    package: Callable[[], object]
    policy: Callable[[], object]
    lease: Callable[[], object]

    def __post_init__(self):
        need(all(callable(callback) for callback in self.callbacks()),
             "ORIGINAL_CALLBACK_REQUIRED")

    def callbacks(self):
        return (self.source_semantic, self.package, self.policy, self.lease)


def current_source(expires_at):
    if expires_at is None:
        return
    end = dt.datetime.fromisoformat(expires_at)
    need(end.tzinfo is not None and end.utcoffset() == dt.timedelta() and
         dt.datetime.now(dt.timezone.utc) < end, "SOURCE_PERIOD_EXPIRED")


def entry(root, rows, capture, checks, expires_at):
    current_source(expires_at)
    verify_boundary(root, rows, capture)
    for callback in checks.callbacks():
        callback()


def exit_checks(root, rows, capture, checks, expires_at):
    """Run every selected read-only exit check and retain every failure."""
    errors = []
    for callback in (lambda: verify_boundary(root, rows, capture),
                     *checks.callbacks(), lambda: current_source(expires_at)):
        try:
            callback()
        except BaseException as error:
            errors.append(error)
    if len(errors) == 1:
        raise errors[0]
    if errors:
        raise BaseExceptionGroup("multiple exit checks failed", errors)


@contextmanager
def original_callback_window(root, rows, capture, checks, *, source_expires_at=None):
    """Conformance-only entry/body/exit, with originals called on both boundaries."""
    entry(root, rows, capture, checks, source_expires_at)
    body_error = None
    try:
        yield
    except BaseException as error:
        body_error = error
    exit_error = None
    try:
        exit_checks(root, rows, capture, checks, source_expires_at)
    except BaseException as error:
        exit_error = error
    if body_error is not None and exit_error is not None:
        raise BaseExceptionGroup("body and exit checks failed", [body_error, exit_error])
    if exit_error is not None:
        raise exit_error
    if body_error is not None:
        raise body_error
