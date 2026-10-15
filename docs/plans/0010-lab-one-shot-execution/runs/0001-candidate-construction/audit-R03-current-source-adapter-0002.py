"""Independent wire-original and same-cut checks for the new source adapter."""
import argparse
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
HERE=ROOT/'product/lab/release-candidates/v1/interface/current-source-adapter-v1'
SOURCE=RUN/'current-source-adapter-audit-source-0002.json'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes())}
def main():
    p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);args=p.parse_args()
    assert sha(SOURCE.read_bytes())==args.source_sha256,'independent audit source differs'
    frozen=json.loads(SOURCE.read_bytes())
    def guard():
        for row in frozen['files']:assert bind(ROOT/row['path'])==row,row['path']
    guard()
    name='_cal_independent_current_source_adapter_0001'
    spec=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    reader_module=__import__(name+'.reader',fromlist=['*']);B=__import__(name+'.base',fromlist=['*'])
    reader=reader_module.SelectedReader(frozen['adapter_source_binding']['sha256'])
    checks=[]
    def need(condition,label):
        assert condition,label
        checks.append(label)
    archive=json.loads((B.PRODUCER_ROOT/'packages/0001/branch.snapshot').read_bytes())
    files={k:base64.b64decode(v['base64_original_bytes'],validate=True) for k,v in archive['files'].items()}
    old=B.PRODUCER_ROOT.parent/'custody-participation-v1/packages/0001/period.json';old_raw=old.read_bytes()
    before_roots=set(Path(tempfile.gettempdir()).glob('cal-R03-current-episode-cold-0001-*'))
    with reader.open_signed(B.SOURCE_PIN,B.PACKAGE_PIN) as selected:
        view=selected.view
        owned_roots=set(Path(tempfile.gettempdir()).glob('cal-R03-current-episode-cold-0001-*'))-before_roots
        need(len(owned_roots)==1,'actual independently owned cold source root')
        need(selected.source_cut['commit_sha256']==json.loads(files['HEAD.json'])['transaction_digest'],'same signed source head')
        need(selected.source_cut['commit_sequence']==json.loads(files['HEAD.json'])['sequence'],'same signed source sequence')
        originals=[s for s in view.subjects.values() if s['source'].get('encoding')==view.handle.custody.ENCODING]
        need(len(originals)==23,'all23 encoded original bodies retained')
        selected_by_ref={r.artifact['version_ref']:r for r in selected.records}
        observed=[]
        for subject in originals:
            locator=subject['source'];value=json.loads(files[locator['path']])
            for token in locator['record_selector'].removesuffix('/record').split('/')[1:]:
                token=token.replace('~1','/').replace('~0','~');value=value[int(token)] if isinstance(value,list) else value[token]
            raw=base64.b64decode(value['content']['data'],validate=True)
            need(sha(raw)==locator['sha256'] and json.loads(raw)==subject['record'],'independent byte extraction '+subject['version_ref'])
            if subject['version_ref'] in selected_by_ref:
                row=selected_by_ref[subject['version_ref']]
                need(row.original==raw and row.artifact['byte_sha256']==sha(raw),'participation bytes match signed original '+subject['version_ref'])
                observed.append({'version_ref':subject['version_ref'],'byte_sha256':sha(raw)})
        need(B.records.PRINCIPAL+'@'+B.records.VERSION in selected_by_ref,'new Principal is selected')
        need(B.records.ASSIGNMENT+'@'+B.records.VERSION in selected_by_ref,'new Assignment is selected')
        need(not any(B.records.PREFIX in r.artifact['identity_ref'] and r.artifact['carrier_ref'] in ['cal.artifact-type.agent-instance/v1','cal.artifact-type.agent-session/v1'] for r in selected.records),'new episode creates no Agent or Session')
        need(selected.view.custody_signed_sources is selected,'head inspection selects actual guarded source adapter')
        report=selected.closure_report()
        need(report['accounted_subjects']==len(view.subjects),'all source subjects accounted')
        need(report['authority_effect']=='none' and report['actual_owner_outcome'] is None and not report['fresh_Session_participation_established'],'source facts supply no current host permission')
        source_cut=selected.source_cut.copy()
    need(selected.closed,'adapter is closed after context exit')
    need(old.read_bytes()==old_raw,'original expired period preserved')
    need(all(not root.exists() for root in owned_roots),'actual owned cold source removed')
    guard()
    value={'schema_version':'lab-current-source-adapter-independent-observation/v1-candidate','result':'PASS','checks':len(checks),'check_names':checks,'source_binding':bind(SOURCE),'source_cut':source_cut,'original_body_count':len(originals),'participation_originals':observed,'current_Agent_qualified':False,'authority_effect':'none','actual_owner_outcome':None,'goal_complete':False}
    out=RUN/'current-source-adapter-independent-observations-0002.json'
    with out.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'PASS','checks':len(checks),'original_bodies':len(originals),'observation_binding':bind(out)}),flush=True)
if __name__=='__main__':main()
