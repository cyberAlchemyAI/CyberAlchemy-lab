"""Inert Mapper stage release facade; execution requires a disjoint successor.

This file cannot enable the stage by environment, argument or import. A later
effect release must bind this frozen candidate and its independent review.
"""
from __future__ import annotations

import json
import sys

import stage

EFFECT_ENABLED = False


def preflight():
    return stage.preflight()


def execute_reviewed_one_shot():
    raise stage.Refused('MAPPER_STAGE_RELEASE_EFFECT_DISABLED_PENDING_STATIC_REVIEW')


if __name__ == '__main__':
    if sys.argv[1:] == ['--preflight']:
        print(json.dumps(preflight(), sort_keys=True))
    elif sys.argv[1:] == ['--execute-reviewed-one-shot']:
        execute_reviewed_one_shot()
    else:
        raise SystemExit('expected --preflight or --execute-reviewed-one-shot')
