#!/usr/bin/env python3
"""Prepare a definition, record or Artifact Type draft; never signs or admits."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / 'ports'))
from creation import DEFINITION_CARRIER, ARTIFACT_TYPE_CARRIER, Store, REPO, create_draft
from lab_runtime.common import RuntimeFault, encoded


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--store', required=True, help='Explicit existing source-bound native branch')
    sub = parser.add_subparsers(dest='kind', required=True)
    for kind in ['definition', 'record', 'artifact-type']:
        p = sub.add_parser(kind)
        for flag in ['file', 'project', 'decision', 'proposal-id', 'out']:
            p.add_argument('--' + flag, required=True)
        p.add_argument('--scope', choices=['project', 'work'], default='project')
        p.add_argument('--work')
        p.add_argument('--carrier', default={'definition': DEFINITION_CARRIER, 'artifact-type': ARTIFACT_TYPE_CARRIER}.get(kind), required=kind == 'record')
        p.add_argument('--version-ref', required=kind == 'record')
        if kind == 'artifact-type':
            p.add_argument('--schema', required=True, help='Original JSON schema document')
            p.add_argument('--contract', required=True, help='Exact native instance contract binding')
            p.add_argument('--owner', required=True, help='Draft steward; does not grant native admission authority')
    args = parser.parse_args()
    try:
        result = create_draft(Store(args.store, REPO), args.file, kind=args.kind, project=args.project,
                              scope=args.scope, work=args.work, carrier=args.carrier, version=args.version_ref,
                              decision=args.decision, proposal_id=args.proposal_id, output=args.out,
                              schema_source=getattr(args, 'schema', None), contract_source=getattr(args, 'contract', None),
                              owner=getattr(args, 'owner', None))
        print(encoded(result).decode(), end='')
        return 0
    except (RuntimeFault, OSError, ValueError, KeyError) as error:
        print(encoded({'outcome': 'BLOCKED', 'reason': str(error), 'authority_effect': 'none'}).decode(), end='')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
