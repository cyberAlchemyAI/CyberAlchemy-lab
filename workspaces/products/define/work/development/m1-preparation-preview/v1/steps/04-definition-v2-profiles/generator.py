#!/usr/bin/env python3
"""Project one proposed Definition/v2 evaluation or lifecycle profile; no authority writes."""
import argparse
import json
from pathlib import Path

GENERATOR_ID = 'cal.generator.definition-profile-projections/v2'

def cell(value):
    return str(value).replace('|', r'\|').replace('\n', ' ')

def render(data):
    evaluation = data['schema_version'] == 'cyberalchemy-lab-evaluation-profile/v2'
    title = 'Definition/v2 evaluation profile' if evaluation else 'Definition/v2 lifecycle profile'
    lines = ['<!-- GENERATED FILE: edit the bound canonical profile JSON. -->', '', '# '+title, '',
             '> Generated from `'+data['source_direction']['canonical']+'`; this view is not canonical.', '',
             '- Record: `'+data['record_id']+'`', '- Status: `'+data['status']+'`',
             '- Authority effect: `'+data['authority_effect']+'`', '- Owner: `'+data['owner_ref']+'`',
             '- Subject: `'+data['subject_artifact_type_ref']+'`',
             '- Profile schema SHA256: `'+data['schema_digest']+'`',
             '- Check/phase contract: `'+data['binding_contract_ref']+'`',
             '- Check/phase contract SHA256: `'+data['binding_contract_sha256']+'`', '']
    if evaluation:
        lines += ['## Outcomes', '']+['- `'+x+'`' for x in data['outcomes']]
        lines += ['', '## Checks', '', '| Check | Purpose | Blocking prerequisites |', '| --- | --- | --- |']
        for row in data['checks']:
            lines.append('| '+cell(row['check_id'])+' | '+cell(row['purpose'])+' | '+cell(', '.join(row['blocked_by']) or 'None')+' |')
        lines += ['', '## Admission rule', '', data['admission_rule']]
    else:
        lines += ['## States', '']+['- `'+x+'`' for x in data['states']]
        lines += ['', '## Transitions', '', '| From | To | Gate | Effect |', '| --- | --- | --- | --- |']
        for row in data['transitions']:
            lines.append('| '+' | '.join(cell(row[x]) for x in ['from','to','gate','effect'])+' |')
        lines += ['', '## Separation invariants', '']+['- '+x for x in data['separation_invariants']]
    lines += ['', '## Claim ceiling', '', data['claim_ceiling']]
    return '\n'.join(lines).rstrip()+'\n'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise SystemExit('refuse existing projection target')
    args.output.write_text(render(json.loads(args.source.read_text(encoding='utf-8'))), encoding='utf-8')

if __name__ == '__main__': main()
