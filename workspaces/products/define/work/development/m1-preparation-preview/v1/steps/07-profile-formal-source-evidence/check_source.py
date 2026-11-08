#!/usr/bin/env python3
"""Exact local source/selector/admission closure and rejection controls.

No source admissions, owner decisions or authority writes. Existing decision
and registry standing is inspected, not fabricated from original status labels.
"""
from pathlib import Path
import copy
import hashlib
import json

STEP=Path(__file__).resolve().parent
ROOT=STEP.parents[5]


def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads(Path(path).read_bytes())
def pointer(value,s):
    if not isinstance(s,str) or not s.startswith('/'):
        raise ValueError('unsupported or empty selector in this closed input')
    for k in s[1:].split('/'):
        k=k.replace('~1','/').replace('~0','~')
        value=value[int(k)] if isinstance(value,list) else value[k]
    return value


def main():
    freeze=load(STEP/'source-selection.json')
    for row in freeze['files']:
        if sha((ROOT/row['path']).read_bytes())!=row['sha256']:raise ValueError('changed source: '+row['path'])
    registry=load(ROOT/'authority/definitions/registry.json')
    entries={e['definition_id']+'@'+e['version']:e for e in registry['entries']}
    D13=load(ROOT/'docs/decisions/0013-foundation-01-admission/decision.json')
    records={e['record_id']:e for e in D13['admitted_records']}
    decisions={}
    for row in load(STEP/'source-closure.json')['bindings']:
        decisions[row['decision_ref']]=load(ROOT/row['decision_path'])

    def audit(ref,decision_override=None):
        if ref['admission_posture']!='admitted':raise ValueError('non-admitted premise')
        if ref['source_ref'] in records:
            e=records[ref['source_ref']];decision_ref=D13['decision_id']
        else:
            e=entries[ref['source_ref']];decision_ref=e['admission_decision_ref']
        if decision_ref!=ref['source_admission_ref']:raise ValueError('wrong admission reference')
        decision=decision_override or decisions[decision_ref]
        if decision.get('status')!='owner-admitted':raise ValueError('source decision is not admitted')
        raw=(ROOT/e['path']).read_bytes()
        if sha(raw)!=ref['content_sha256'] or e['sha256']!=ref['content_sha256']:raise ValueError('source integrity mismatch')
        selected=pointer(json.loads(raw),ref['selector'])
        if selected is None:raise ValueError('empty source selection')
        return {'source_ref':ref['source_ref'],'selector':ref['selector'],'result':'PASS'}

    refs=[]
    for target in load(STEP/'targets.json')['targets']:
        value=load(ROOT/target['path'])
        refs+=value['source_refs']
    checked=[audit(ref) for ref in refs]
    seed=next(r for r in refs if r['source_ref'].startswith('cal.definition.'))
    controls=[]
    def reject(name,changes=None,decision=None):
        value=copy.deepcopy(seed);value.update(changes or {})
        try:audit(value,decision)
        except (KeyError,ValueError,IndexError,TypeError) as e:
            controls.append({'case':name,'result':'PASS','rejected':True,'reason':str(e)});return
        raise ValueError('bad source accepted: '+name)
    reject('changed-whole-file-digest',{'content_sha256':'0'*64})
    reject('unknown-source-identity',{'source_ref':'cal.definition.not-in-registry@1.0.0'})
    reject('unknown-member-selector',{'selector':'/missing-clause'})
    reject('slash-is-not-whole-document',{'selector':'/'})
    reject('unadmitted-premise-tag',{'admission_posture':'candidate-unadmitted'})
    reject('wrong-decision-reference',{'source_admission_ref':'CAL-NOT-AN-ADMISSION'})
    wrong_decision=copy.deepcopy(decisions[seed['source_admission_ref']]);wrong_decision['status']='candidate-unadmitted'
    reject('unadmitted-decision-record',decision=wrong_decision)
    profile_ref=next(r for r in refs if r['source_ref']=='CAL-EVALUATION-DEFINITION-V1')
    if load(ROOT/records[profile_ref['source_ref']]['path'])['status']!='candidate-unadmitted':raise ValueError('original status control changed')
    audit(profile_ref)
    controls.append({'case':'original-candidate-label-with-admitted-overlay','result':'PASS','observation':'Exact D13 admitted record and digest establish effective source standing; original status label alone does not.'})
    result={'schema_version':'cal.define-profile-source-check-results/v1','authority_effect':'none','checked_bindings':len(checked),'source_checks':checked,'controls':controls,'source_reference_gaps':0,'new_source_admissions':0,'claim_ceiling':'Exact local provenance/reference and recorded admission overlay only. Proposed source interpretation, wider scope fidelity and real principal authenticity still need owner judgment.'}
    with (STEP/'source-check-results.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
    for row in freeze['files']:
        if sha((ROOT/row['path']).read_bytes())!=row['sha256']:raise ValueError('source changed during closure: '+row['path'])
    print(json.dumps({'source_bindings':len(checked),'rejection_and_overlay_controls':len(controls),'remaining_reference_gaps':0,'source_admissions_created':0,'authority_effect':'none'},indent=2))


if __name__=='__main__':main()
