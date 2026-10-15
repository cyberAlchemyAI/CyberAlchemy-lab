"""Support original contract evidence without inventing source admission."""
import json
from pathlib import Path
import shutil
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD=BASE/'api-v61';API=BASE/'api-v62'
def replace(p,a,b):
    value=p.read_text();assert value.count(a)==1,(p,a);p.write_text(value.replace(a,b,1))
def main():
    assert not API.exists() and not (BASE/'lesson-host-composition-v12').exists()
    ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json')
    shutil.copytree(OLD,API,ignore=ignore)
    shutil.copytree(BASE/'lesson-host-composition-v11',BASE/'lesson-host-composition-v12',ignore=ignore)
    replace(BASE/'lesson-host-composition-v12/host.py','api-v61/service.py','api-v62/service.py')
    replace(API/'lesson_selection.py','lesson-host-composition-v11','lesson-host-composition-v12')
    p=API/'challenge_submission.py'
    replace(p,'    def receipt(self,row):\n        selected=row[\'receipt_binding\'];path=ROOT/selected[\'path\']',
        '    def bound_original(self,selected):\n        path=ROOT/selected[\'path\']')
    replace(p,"raw=P.source.original(selected);proof=P.frame_parse(raw);W.privacy(proof)",
        "raw=P.source.original(selected);W.privacy(P.frame_parse(raw));return raw\n    def receipt(self,row):\n        selected=row['receipt_binding'];raw=self.bound_original(selected);proof=P.frame_parse(raw)")
    replace(p,'    def _plan(self,message,outer,key):', '''    def candidate_evidence(self,row):
        require(row['kind']=='evidence-set' and row['artifact'] is not None,'only explicit candidate Evidence Sets use this adapter')
        header=row['artifact'];raw=self.vault.material(row['binding']);body=P.frame_parse(raw);W.privacy(body)
        require(header['scope_ref']==self.service.channel.policy['scope_refs'][0] and header['byte_sha256']==sha(raw)
            and header['identity_ref']==body['node_id'] and header['version_ref'].startswith(body['node_id']+'@')
            and row['binding']==P.binding(header['version_ref'],raw),'independently selected candidate evidence header/body differs')
        require(body['kind']=='evidence-set' and body['lifecycle_state']=='candidate'
            and header['carrier_ref']=='cal.artifact-type.evidence-set/v1','candidate evidence carrier/posture differs')
        self.view.handle.operations.validate_record(body,header['carrier_ref'],self.view.data['projection'])
        return raw
    def original_evidence(self,row):
        require(row['kind'] in ('decision','evidence-set') and row['artifact'] is None,'unsupported bound-original evidence adapter')
        selected=row['original_binding'];raw=self.bound_original(selected);body=P.frame_parse(raw)
        require(row['binding']==P.binding(selected['path'],raw) and body['kind']==row['kind'],'original evidence identity or kind differs')
        self.view.handle.operations.validate_record(body,'cal.artifact-type.'+row['kind']+'/v1',self.view.data['projection'])
        return raw
    def _plan(self,message,outer,key):''')
    before="""            if row['kind']=='validation-receipt':
                require(row['artifact'] is None and row['receipt_binding'] is not None,'receipt evidence must use its actual source adapter')
                raw=self.receipt(row)
            else:
                require(row['artifact'] is not None and row['receipt_binding'] is None,'artifact evidence must use its actual source adapter')
                _,body,raw,_=self.source_record(row['artifact'],None if row['kind']=='source' else row['kind'],historical=row['kind']=='source')
                require(binding==P.binding(row['artifact']['version_ref'],raw),'artifact evidence original identity differs')
            require(self.vault.material(binding)==raw,'challenge evidence bytes differ from independently verified originals')
            selected.append({'kind':row['kind'],'binding':copy.deepcopy(binding)});originals.append(raw)"""
    after="""            if row['source_posture']=='completed-validation':
                require(row['kind']=='validation-receipt' and row['artifact'] is None and row['receipt_binding'] is not None
                    and row['original_binding'] is None,'receipt evidence must use its actual source adapter')
                raw=self.receipt(row)
            elif row['source_posture']=='bound-original':
                require(row['original_binding'] is not None and row['receipt_binding'] is None,'original evidence custody differs')
                raw=self.original_evidence(row)
            elif row['source_posture']=='candidate-original':
                require(row['original_binding'] is None and row['receipt_binding'] is None,'candidate evidence cannot claim a signed/current original')
                raw=self.candidate_evidence(row)
            else:
                require(row['source_posture']=='signed-source' and row['artifact'] is not None
                    and row['receipt_binding'] is None and row['original_binding'] is None,'artifact evidence must use its actual source adapter')
                _,body,raw,_=self.source_record(row['artifact'],None if row['kind']=='source' else row['kind'],historical=row['kind']=='source')
                require(binding==P.binding(row['artifact']['version_ref'],raw),'artifact evidence original identity differs')
            require(self.vault.material(binding)==raw,'challenge evidence bytes differ from independently verified originals')
            selected.append({'kind':row['kind'],'binding':copy.deepcopy(binding),'source_posture':row['source_posture']});originals.append(raw)"""
    replace(p,before,after)
    p=API/'challenge-routing.schema.json';schema=json.loads(p.read_bytes());row=schema['properties']['accepted_evidence']['items']
    row['properties']['source_posture']={'enum':['signed-source','candidate-original','bound-original','completed-validation']}
    row['properties']['original_binding']=row['properties']['receipt_binding'].copy()
    row['required']+=['source_posture','original_binding'];p.write_text(json.dumps(schema,indent=2,sort_keys=True)+'\n')
    p=API/'challenge_fixture.py'
    replace(p,"    evidence_set=pick(view,'evidence-set');decision=pick(view,'decision')\n",'')
    before="""    for kind,row in (('source',subject),('evidence-set',evidence_set),('decision',decision)):
        header=M.artifact_ref(view,row);raw=current_body(view,row);binding=P.binding(header['version_ref'],raw)
        accepted.append({'kind':kind,'binding':binding,'artifact':header,'receipt_binding':None});materials[binding['ref']]=raw"""
    after="""    header=subject_header;raw=current_body(view,subject);binding=P.binding(header['version_ref'],raw)
    accepted.append({'kind':'source','binding':binding,'artifact':header,'receipt_binding':None,'original_binding':None,'source_posture':'signed-source'});materials[binding['ref']]=raw
    evidence=P.frame_parse((ROOT/'authority/artifact-types/evidence-set/v1/fixtures/valid/record.json').read_bytes())
    evidence.update(node_id='evidence-set:R03-new-challenge:'+uuid.uuid4().hex,scope_ref=view.data['config']['scope_ref'],
        owner_ref=challenger['identity'],evidence_refs=[binding['ref'],receipt_binding['ref']],relation_refs=[],successor_refs=[],
        claim_ceiling='New unadmitted Evidence Set collects exact inputs. No ground adjudication, source admission or actual owner outcome.')
    evidence['payload'].update(item_refs=[binding['ref'],receipt_binding['ref']],source_refs=[binding['ref']],
        coverage_statement='Exact challenged original and independently executed rule receipt; no finding of factual ground validity.',
        limitations=['Candidate unadmitted collection','Receipt proves its own rule scope only','Owner adjudication remains pending'])
    raw=(json.dumps(evidence,indent=3)+'\\n').encode();version=evidence['node_id']+'@evidence.candidate.1'
    header={'scope_ref':view.data['config']['scope_ref'],'identity_ref':evidence['node_id'],'version_ref':version,
        'carrier_ref':'cal.artifact-type.evidence-set/v1','byte_sha256':P.source.sha(raw)};binding=P.binding(version,raw)
    accepted.append({'kind':'evidence-set','binding':binding,'artifact':header,'receipt_binding':None,'original_binding':None,'source_posture':'candidate-original'});materials[binding['ref']]=raw
    decision_path=ROOT/'authority/admissions/governance-transaction-surface/v1/instances/governance/decisions/decision-0074a.json'
    raw=decision_path.read_bytes();binding=P.binding(str(decision_path.relative_to(ROOT)),raw)
    accepted.append({'kind':'decision','binding':binding,'artifact':None,'receipt_binding':None,
        'original_binding':{'path':str(decision_path.relative_to(ROOT)),'sha256':P.source.sha(raw)},'source_posture':'bound-original'});materials[binding['ref']]=raw"""
    replace(p,before,after)
    replace(p,"'receipt_binding':{'path':str(receipt_path.relative_to(ROOT)),'sha256':P.source.sha(receipt_raw)}})",
        "'receipt_binding':{'path':str(receipt_path.relative_to(ROOT)),'sha256':P.source.sha(receipt_raw)},'original_binding':None,'source_posture':'completed-validation'})")
    replace(p,"evidence=[{'kind':r['kind'],'binding':r['binding']} for r in accepted]", "evidence=[{'kind':r['kind'],'binding':r['binding'],'source_posture':r['source_posture']} for r in accepted]")
    p=API/'CHALLENGE-SUBMISSION.md'
    with p.open('a') as stream:stream.write('''

Evidence has explicit source posture. Signed-source records retain actual native
eligibility. A new Evidence Set can be a candidate selected by the independent
host, with original schema/custody validation and no current/admitted claim.
Bound original Decision/Evidence Set documents must match an exact source file
in the frozen host manifest and their actual carrier contract; this adapter
claims original content, not source membership or authority. Completed validation
receipts retain their own executed check scope. The eligibility calculation
reports each posture and never adjudicates factual grounds.

API61's focused fixture stopped before any public call because it demanded a
current admitted Evidence Set absent from the selected source. Its error evidence
is preserved. API62 supports new evidence without assuming admission; the public
contract did not require every evidence material to be admitted-current. All
312 prior test methods remain unchanged; the fixture now selects an explicit
candidate collection and an actual bound original governance Decision.
''')
    freeze=(RUN/'freeze-API61-challenge-policy-0001.py').read_text()
    freeze=freeze.replace("OLD=BASE/'api-v60';API=BASE/'api-v61'","OLD=BASE/'api-v61';API=BASE/'api-v62'")
    freeze=freeze.replace("guard.verify('b1b9e42dd0912339ef4de23fc314733507bf9042a3c03a3f4f28a23d3dae301e')","guard.verify('786eaa0529d37b720c5142ae3515fd745f88d9f1315f04fb0bb3334f6b2428f8')")
    freeze=freeze.replace("BASE/'lesson-host-composition-v11'","BASE/'lesson-host-composition-v12'")
    freeze=freeze.replace("RUN/'author-API61-challenge-policy-0001.py',RUN/'API60-challenge-policy-static-diagnosis-0001.json',",
        "RUN/'author-API62-challenge-evidence-0001.py',OLD/'receipts/challenge-focused-checks-0001.json',OLD/'receipts/challenge-focused-0001.log',OLD/'receipts/challenge-focused-wire-0001.json',")
    with (RUN/'freeze-API62-challenge-evidence-0001.py').open('x') as stream:stream.write(freeze)
    print('Authored API62 evidence-posture adapters; current source, candidate collections, bound originals and executed receipts remain separate.',flush=True)
if __name__=='__main__':main()
