"""Retain isolated input captures and independently replay exact candidate checks."""
import base64
import copy
import json
import sys
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[7];UNIT=Path(__file__).resolve().parent
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1';sys.path[:0]=[str(IMPL),str(IMPL/'tests')]
import test_E03 as controls
v=controls.v


def capture_case(root,bundle_ref,selection_ref):
    # Fixed isolated test root census, without installing fixture authority in Lab.
    files=[]
    for file in sorted(root.rglob('*')):
        if file.is_file():
            raw=file.read_bytes();files.append({'path':file.relative_to(root).as_posix(),'sha256':v.r.digest(raw),'content_base64':base64.b64encode(raw).decode()})
    actual=v.verify(root,bundle_ref,selection_ref)
    return {'bundle_ref':bundle_ref,'selection_ref':selection_ref,'files':files,'actual':actual}


def replay(case):
    with tempfile.TemporaryDirectory(prefix='assurance_E03_replay_') as directory:
        root=Path(directory)
        for row in case['files']:
            v.r.components(row['path']);raw=base64.b64decode(row['content_base64'],validate=True)
            if v.r.digest(raw)!=row['sha256']:raise ValueError('Corrupt retained control input')
            file=root/row['path'];file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(raw)
        actual=v.verify(root,case['bundle_ref'],case['selection_ref'])
        if not v.r.same_json(actual,case['actual']):raise ValueError('Independent control replay changed')
        return {'result':'PASS','status':actual['status'],'semantic_ready':actual['semantic_ready']}


def main():
    records=[]
    fixture,bundle,required,put,selection=controls.setup_selection();root=fixture.root
    def save(case_id):
        out=v.b.publish(root,bundle,required,v.b.BASE+'/units/E03/controlled')
        if out['status']!='published-candidate':raise ValueError(out)
        selection_ref=put('selected/selection.json',selection)
        records.append({'case_id':case_id,**capture_case(root,out['bundle_ref'],selection_ref)})
    try:
        save('complete-denominator-missing-evidence')
        row,request,native,names=controls.add_witness(bundle,put,selection,root,identity='query:joint-population');save('checked-joint-population-witness')
        native['witness']['model']['predicates'][names['P']]=[];native['witness']['model_sha256']=v.ir.digest(native['witness']['model']);ref=put('candidate/native.json',native);row['native_result']['binding']=ref;row['result']['evidence_refs']=[ref];save('rehashed-false-population-witness')
    finally:fixture.doCleanups()
    expected=['verified-candidate-accounting','verified-candidate-accounting','verification-rejected']
    if [row['actual']['status'] for row in records]!=expected:raise ValueError('Incorrect worked-control outcomes')
    replays=[{'case_id':row['case_id'],**replay(row)} for row in records]
    value={'schema_version':'definition-assurance-verifier-worked-cases/v1-candidate','authority_effect':'none','goal_status':'active','source_scope':'Isolated synthetic admitted-byte fixtures retained as serialized captures. No fixture definition/admission installed in canonical Lab paths.','current_lab_definition_proofs':0,'records':records,'replays':replays}
    path=UNIT/'worked-verifications.json'
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'PASS','cases':len(records),'independent_replays':len(replays),'checked_witnesses':1,'denied_rehashed_witnesses':1,'semantic_ready':False}))


if __name__=='__main__':main()
