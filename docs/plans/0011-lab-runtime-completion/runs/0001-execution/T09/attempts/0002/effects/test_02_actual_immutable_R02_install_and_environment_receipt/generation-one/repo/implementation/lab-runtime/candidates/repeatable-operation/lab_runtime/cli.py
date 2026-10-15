"""Explicit read-only candidate CLI; operational API commands arrive separately."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .common import RuntimeFault
from .profiles import select
from .sources import capture


def main(argv=None):
    parser = argparse.ArgumentParser(description='Inspect an exact candidate source profile; no admission or runtime activation.')
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--profile', required=True)
    parser.add_argument('--profile-sha', required=True)
    parser.add_argument('--policy', required=True)
    parser.add_argument('--executable-manifest', required=True)
    parser.add_argument('--selection-review', required=True)
    parser.add_argument('--selection-review-sha', required=True)
    parser.add_argument('command', choices=['capture-status'])
    args = parser.parse_args(argv)
    try:
        selected = select(args.repo, profile_path=args.profile, profile_sha256=args.profile_sha,
                          policy_path=args.policy, executable_manifest_path=args.executable_manifest,
                          review_path=args.selection_review, review_sha256=args.selection_review_sha)
        source = capture(selected)
        print(json.dumps({'authority_effect': 'none', 'profile_id': selected.profile['profile_id'],
            'profile_sha256': source['source_profile_sha256'], 'snapshot_digest': source['snapshot_digest'],
            'source_cut': source['expected_cut'], 'subject_count': len(source['subjects']),
            'original_byte_materials': len(source['materials']), 'selection_scope': source['selection_scope']}, sort_keys=True))
        return 0
    except RuntimeFault as exc:
        print(json.dumps({'authority_effect': 'none', 'error': str(exc)}))
        return 2
