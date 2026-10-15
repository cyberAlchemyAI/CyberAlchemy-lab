"""Readable operator explanations; exact JSON report remains available."""
import json


def readable(report):
    lines = [f"Lab {report['command']} — {report['selected_source']}",
        f"Scope: {report['scope_ref']}", f"Currentness: {report['currentness']['status']}",
        f"Source cut: {report['source_cut']['baseline_snapshot_digest']}",
        f"Signed HEAD: {report['source_cut']['signed_head']}",
        'Visibility: private candidate evidence', '']
    if report['currentness']['changed']:
        lines += ['Changed source bindings:'] + ['  ' + p for p in report['currentness']['changed']] + ['']
    command = report['command']
    if command == 'status':
        lines += ['Definitions: ' + ', '.join(f'{v} {k}' for k,v in sorted(report['definition_counts'].items())),
            f"Catalog versions: {report['catalog_versions']}",
            f"Observed local applications: {report['local_application_count']}",
            'Repository runtime activation: not observed', 'API handlers: 0 of 34 implemented by this CLI', '', 'Open gaps:']
        lines += ['  ' + g for g in report['gaps']]
    elif command == 'definitions':
        lines += [f"Definitions: {report['total']} selected; page starts at {report['offset']}", '']
        for row in report['items']:
            lines += [f"{row['version_ref']}  [{row['status_facets']['admission']}]",
                '  ' + row['name'], '  Source: ' + row['source_binding']['path'],
                '  SHA256: ' + row['source_binding']['sha256'], '  Decision: ' + str(row['decision_ref'])]
        lines += ['', 'Next offset: ' + str(report['next_offset']), report['coverage']]
    elif command == 'inspect':
        row=report['artifact']; lines += [row['version_ref'], row['name'], 'Independent status facets:']
        lines += ['  ' + k + ': ' + str(v) for k,v in row['status_facets'].items() if k != 'inference_rule']
        lines += ['Source: ' + row['source_binding']['path'], 'Source binding SHA256: ' + row['source_binding']['sha256'],
            'Record structural SHA256: ' + report['record_structural_sha256'],
            'Authority reference: ' + str(report['authority']['selected_decision_ref']),
            'Authority resolution: ' + report['authority']['resolution_posture'], '', 'Open residue:']
        lines += ['  ' + str(g) for g in report['gaps']] or ['  No recorded residue in this selected body.']
        if report['body_included']:
            lines += ['', 'Exact parsed content:', json.dumps(report['body'], indent=2, ensure_ascii=False)]
    elif command == 'connections':
        lines += [report['artifact']['version_ref'], 'Typed connections:']
        for row in report['connections']:
            lines += [f"  {row['source'].get('version_ref')} — {row['relation_kind_ref']} → {row['target'].get('version_ref')}",
                '    ' + row['validation_posture'], '    Qualifiers: ' + json.dumps(row['qualifiers'], sort_keys=True)]
            for view in row['endpoint_views']:
                lines += [f"    Carrier {view['carrier_kind']} represents endpoint {view['represented_endpoint_kind']}"]
            if row['gap']:lines += ['    Gap: ' + row['gap']]
        if not report['connections']:lines += ['  No exact connections in this selected cut.']
        lines += ['  Connections grant no action permission.']
    elif command == 'review':
        lines += ['Recorded review before isolated local application', f"Targets: {report['target_count']}"]
        for row in report['targets']:
            lines += ['', row['operation'] + ': ' + row['target_ref'], 'Predecessor: ' + str(row['predecessor_ref']),
                'Status before application: candidate-unadmitted', 'Structural diff:']
            lines += [json.dumps(d, ensure_ascii=False, sort_keys=True) for d in row['structural_diff']]
            lines += ['Decision core:', json.dumps(row['decision_core'], indent=2, ensure_ascii=False)]
        lines += ['', 'Recorded local effects:', json.dumps(report['effects'], indent=2),
            'Final owner review: absent', report['decision_prompt']]
    else:
        lines += ['Original transaction file SHA256: ' + report['transaction_file_sha256'],
            'Transaction digest: ' + report['transaction_digest'], 'Application receipt:',
            json.dumps(report['application_receipt'], indent=2), 'Why-path:']
        lines += ['  ' + json.dumps(step, sort_keys=True) for step in report['why_path']]
    lines += ['', report['claim_ceiling']]
    return '\n'.join(lines) + '\n'
