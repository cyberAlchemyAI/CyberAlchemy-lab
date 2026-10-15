"""Read-only source binding, sealed-file preservation and worked-case replay."""
import hashlib
import json
import sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6]
sys.path.insert(0,str(UNIT));import pilot_spec as p
sys.path.insert(0,str(UNIT.parent/'A04'));import correspondence as cc
BASE=UNIT.parent.parent


def check_file(row):
    if hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Stale candidate bytes: '+row['path'])


def main():
    counts={}
    for path in [BASE/'units/E03/delivery-manifest.json',UNIT/'delivery-manifest.json']:
        rows=json.loads(path.read_text())['files']
        if len({row['path'] for row in rows})!=len(rows):raise ValueError('Duplicate delivery identity')
        for row in rows:check_file(row)
        counts[path.relative_to(ROOT).as_posix()]=len(rows)
    receipt=json.loads((UNIT/'receipt.json').read_text());context=json.loads((UNIT/'context.json').read_text())
    for row in receipt['inputs']+receipt['outputs']+context['sources']:check_file(row)
    if receipt['unit_id']!='A07.1' or receipt['authority_effect']!='none' or receipt['goal_status']!='active':raise ValueError('False authority/completion boundary')
    spec=json.loads((BASE/'pilot-v2/interpretation.json').read_text());source=p.bind_sources(spec,ROOT);snapshot=json.loads((ROOT/spec['snapshot_ref']['path']).read_text());accounted=0
    if spec['selected_coupling']['query_binding']!=p.ADMISSION_CONTEXT:raise ValueError('Coupling scope mismatch')
    for row in spec['source_packets']:
        check_file(row['packet_ref']);check_file(row['check_ref']);packet=json.loads((ROOT/row['packet_ref']['path']).read_text());required=[v['finding_id'] for v in packet['source_precedence']['conflicts']];report=cc.check(packet,snapshot,required_conflicts=required);stored=json.loads((ROOT/row['check_ref']['path']).read_text())
        if not p.r.same_json(report,stored) or report['semantic_ready'] or not report['character_accounting_complete']:raise ValueError('Source accounting replay mismatch')
        accounted+=report['source_units']
    ref=spec['worked_examples_ref'];check_file(ref);worked=json.loads((ROOT/ref['path']).read_text());states=0;moves=0
    for row in worked['states']:
        if not p.r.same_json(row['actual'],p.inspect_state(row['state'],'admission-use-requires-trace')):raise ValueError('State replay mismatch')
        states+=1
    for row in worked['moves']:
        if not p.r.same_json(row['actual'],p.check_move(row['move'],row['before'],row['after'])):raise ValueError('Move replay mismatch')
        moves+=1
    if (accounted,states,moves)!=(166,11,1):raise ValueError('Replay denominator mismatch')
    print(json.dumps({'result':'PASS','authority_effect':'none','delivery_manifests':counts,'source_binding':source,'source_units_accounted':accounted,'worked_states':states,'worked_moves':moves,'test_count':receipt['test_count'],'source_fidelity':'pending','semantic_dependency_closure':'unresolved','owner_accepted_whole_definition_translations':0,'whole_definition_proofs':0,'goal_status':'active','full_project_completion':'not-established'},indent=2,sort_keys=True))


if __name__=='__main__':main()
