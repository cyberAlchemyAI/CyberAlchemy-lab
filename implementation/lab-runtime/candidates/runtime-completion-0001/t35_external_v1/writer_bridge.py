"""Prospective T35 external-root writer boundary; every effect is disabled."""
from __future__ import annotations

import os

from .binding_adapter import activation_capability
from .held_paths import (HeldCanonicalDirectory, verify_parent_chain,
                         verify_snapshot_chain)
from .path_contract import (OUTPUT_PARENT, require, validate_intent,
                            verify_process_and_parent)


def inspect_pre_effect(intent: dict) -> dict:
    """Read-only bounded observation of installed topology if present.

    A PASS here would still not prove unique same-UID process custody or the
    mkdirat-before-open interval. No caller may use it as activation authority.
    """
    validate_intent(intent)
    with HeldCanonicalDirectory(str(OUTPUT_PARENT)) as parent:
        verify_parent_chain(intent, parent)
        verify_process_and_parent(intent, parent.fd)
        with HeldCanonicalDirectory(intent['input_snapshot_path']) as snapshot:
            verify_snapshot_chain(intent, snapshot)
            require(parent.attached() and snapshot.attached(),
                    'held output or input ancestry changed')
    return {'schema_version': 'lab-T35-external-root-pre-effect-observation/v1-inactive',
            'result': 'BOUNDED-OBSERVATION-ONLY', 'effect_authorized': False,
            'exclusive_same_uid_writer_proved': False,
            'continuous_supervisor_custody_proved': False}


def mkdir_child(*_args, **_kwargs):
    # The exclusive writer mechanism is not installed, and mkdirat itself
    # yields no child descriptor. Do not call os.mkdir here.
    activation_capability()
    raise RuntimeError('unreachable external-root child creation')


def write_leaf(*_args, **_kwargs):
    activation_capability()
    raise RuntimeError('unreachable external-root leaf creation')


def dispatch_stage_or_preview(*_args, **_kwargs):
    activation_capability()
    raise RuntimeError('unreachable external-root phase dispatch')
