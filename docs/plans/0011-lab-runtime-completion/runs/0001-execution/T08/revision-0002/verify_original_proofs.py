"""Exact retained API16 public proof inputs; no path remapping or authority."""
import base64
from datetime import datetime,timedelta,timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import time
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[6]
COMPONENT=ROOT/'product/lab/release-candidates/v1/interface/release-proof-inputs-v2-completion-0001'
sys.path.insert(0,str(COMPONENT));import test_inputs as T
P=T.P
SOURCE='product/lab/release-candidates/v1/interface/api-integration-v16/source-manifest.json'
PROFILE='product/lab/release-candidates/v1/interface/api-integration-v16/contract-profile.json'
ENV='product/lab/release-candidates/v1/release-validation/0001/runtime16-draft-0276/environment-contract.json'
DEPENDENCIES='product/lab/release-candidates/v1/interface/api-integration-v16/SCHEMA-EXECUTION-DEPENDENCIES.json'
PINS={SOURCE:'8ac40a51e23b8e528178807792b8ae477aa9c46cd50d92a5b1522c82945413c7',PROFILE:'8cc29da16d3881d8816cdc45c55358d9229fcaf226d1b9a757402ebc8675d18c',DEPENDENCIES:'949f9c888740d40c6d94fcdedf7f2bc19dddc950cba8831d18c8b00f8bcf832b',ENV:'79393346ec5b58517febe7518d4268ea1804fba1bf2061f4b3bcc69b44de3506'}

def main():
    started=datetime.now(timezone.utc).isoformat();report_path=RUN/'original-proof-attempt-0001.json'
    if report_path.exists():raise RuntimeError('original proof evidence already exists')
    documents={};selected={};tables=[]
    for path in (SOURCE,PROFILE,ENV,DEPENDENCIES):
        raw=(ROOT/path).read_bytes();sha=P.digest(raw)
        if path in PINS:P.need(sha==PINS[path],'independent original API16 table pin differs')
        selected[path]=sha;documents[path]=P.parse(raw)
    env=documents[ENV]
    P.need(env['API_source_binding']=={'path':SOURCE,'sha256':PINS[SOURCE]} and env['API_profile_binding']=={'path':PROFILE,'sha256':PINS[PROFILE]},'original composite is not API16')
    P.need(env['complete_source_bindings']==documents[SOURCE]['files'] and env['complete_profile_bindings']==documents[PROFILE]['files'] and env['schema_execution_bindings']==documents[DEPENDENCIES]['files'],'original composite proof rows differ')
    original={};row_occurrences=[]
    for doc,key in [(SOURCE,'files'),(PROFILE,'files'),(PROFILE,'external_execution_dependency_bindings'),(ENV,'complete_source_bindings'),(ENV,'complete_profile_bindings'),(ENV,'schema_execution_bindings'),(ENV,'host_native_binding'),(ENV,'host_ABI_library_bindings'),(ENV,'offline_environment_wheel_bindings')]:
        rows=[documents[doc][key]] if key=='host_native_binding' else documents[doc][key];tables.append((doc,key,rows))
        for index,row in enumerate(rows):
            P.closed(row,('path','sha256'),'original proof row')
            if row['path']in original:P.need(original[row['path']]==row['sha256'],'original conflicting row digest')
            original[row['path']]=row['sha256'];row_occurrences.append({'table':doc,'selector':'/'+key,'index':index,**row})
    for path,sha in selected.items():original[path]=sha
    host_rows=[env['host_native_binding']]+env['host_ABI_library_bindings']+env['offline_environment_wheel_bindings']
    for row in host_rows:
        P.closed(row,('path','sha256'),'original host binding');original[row['path']]=row['sha256']
    omitted=[];rows=[];by_path={};roots={'repo':dict(id='repo',path=str(ROOT),**P.metadata(ROOT.stat()))}
    with tempfile.TemporaryDirectory(prefix='owned-original-proof-',dir=RUN)as scratch:
        own=Path(scratch);own.chmod(0o700);roots['owned']=dict(id='owned',path=str(own),**P.metadata(own.stat()))
        for path,sha in sorted(original.items()):
            logical=path;target=Path(path)if path.startswith('/')else ROOT/path
            # Original manifests are public inventories, never permission to
            # open an original key, credential, or live database.
            if target.suffix.lower()in('.key','.pem','.p12','.pfx','.db','.sqlite','.sqlite3')or target.name=='.env' or any(x in target.parts for x in('.ssh','.gnupg','private-state','private-keys')):
                omitted.append({'path':logical,'sha256':sha,'status':'REFUSED-PRIVATE-OR-LIVE-INPUT'});continue
            try:info=target.lstat()
            except FileNotFoundError:
                omitted.append({'path':logical,'sha256':sha,'status':'MISSING-ORIGINAL-LOCATOR'});continue
            if not stat.S_ISREG(info.st_mode):
                omitted.append({'path':logical,'sha256':sha,'status':'REFUSED-NONREGULAR-OR-SYMLINK'});continue
            if target.is_relative_to(ROOT):rid='repo';relative=str(target.relative_to(ROOT))
            else:
                rid='external-'+str(len(roots));parent=target.parent
                roots[rid]=dict(id=rid,path=str(parent),**P.metadata(parent.stat()));relative=target.name
            fid='original-'+str(len(rows));kind={SOURCE:'source-manifest',PROFILE:'contract-profile',ENV:'environment-contract',DEPENDENCIES:'execution-selection'}.get(path,'host-dependency'if path.startswith('/')else'public-package')
            row=dict(id=fid,root_id=rid,path=relative,logical_path=logical,kind=kind,sha256=sha,size=info.st_size,**P.metadata(info));rows.append(row);by_path[path]=fid
        state={'schema_version':'lab-protected-input-custody-state/v1-candidate','principal_ref':'technical:T08-original-proof-reader','revoked':False,'authority_effect':'none'}
        T.save(own/'state',P.canonical(state));info=(own/'state').stat();rows.append(dict(id='state',root_id='owned',path='state',logical_path='technical:T08/state',kind='custody-state',sha256=P.digest(P.canonical(state)),size=info.st_size,**P.metadata(info)))
        # Keep each original table intact. Incomplete coverage is explicitly
        # selected as counterevidence and must fail the reader's exact closure.
        table_entries=[]
        for doc,key,body in tables:
            tables_entry={'file_id':by_path[doc],'row_selector':'/'+key,'coverage_file_ids':[by_path[r['path']]for r in body if r['path']in by_path]}
            table_entries.append(tables_entry)
        sb={'ref':SOURCE,'sha256':PINS[SOURCE]};pb={'ref':PROFILE,'sha256':PINS[PROFILE]}
        cut={'branch_ref':'technical:T08-readonly-original-proof','store_ref':'technical:T08-no-live-store','commit_sequence':0,'commit_sha256':P.digest(b'T08-no-native-cut-claim'),'source_profile_sha256':PINS[PROFILE],'streams':[]}
        selector={'schema_version':'lab-protected-input-selector/v1-candidate','source_binding':sb,'profile_binding':pb,'source_cut':cut,'principal_ref':state['principal_ref'],'operation':'release.prepare','roots':list(roots.values()),'files':rows,'proof_tables':table_entries,'custody_state_file_id':'state','authority_effect':'none'}
        raw=P.canonical(selector);T.save(own/'selector',raw);sel={'ref':'technical:T08/selector','sha256':P.digest(raw)}
        key=Ed25519PrivateKey.generate();public=base64.b64encode(key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)).decode();clock=datetime.now(timezone.utc)
        payload={'schema_version':'lab-protected-input-custody-grant/v1-candidate','selector_binding':sel,'source_binding':sb,'profile_binding':pb,'source_cut':cut,'principal_ref':state['principal_ref'],'operation':'release.prepare','not_before':(clock-timedelta(seconds=1)).isoformat(),'expires_at':(clock+timedelta(seconds=300)).isoformat(),'authority_effect':'none'}
        grant=P.canonical({'payload':payload,'signature_b64':base64.b64encode(key.sign(P.canonical(payload))).decode()});T.save(own/'grant',grant);del key
        anchor=P.CustodyAnchor(state['principal_ref'],public,sb,pb,cut,'release.prepare',sel,{'ref':'technical:T08/grant','sha256':P.digest(grant)},T.locator(own/'selector','owned'),T.locator(own/'grant','owned'))
        reader=P.ProtectedReader(raw,grant,anchor);observed=[];verified_bytes=0
        reader.authority()
        for row in rows:
            try:reader._read(row);observed.append({'path':row['logical_path'],'sha256':row['sha256'],'status':'EXACT-BYTES'});verified_bytes+=row['size']
            except P.Refusal:observed.append({'path':row['logical_path'],'sha256':row['sha256'],'status':'REFUSED-FRESH-BYTES-OR-ATTACHMENT'})
        reader.authority();closure={}
        try:closure={'status':'PASS','result':reader.verify()}
        except P.Refusal as exc:closure={'status':'REFUSED','reason':str(exc)}
        report={'schema_version':'lab-original-proof-reader-observation/v1','started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'table_bindings':selected,'original_table_bytes':sum((ROOT/p).stat().st_size for p in selected),'original_table_row_occurrences':len(row_occurrences),'original_unique_inputs':len(original),'original_row_occurrences':row_occurrences,'unavailable_or_refused_original_inputs':omitted,'fresh_input_observations':observed,'verified_bytes':verified_bytes,'protected_reader_full_closure':closure,'selector_sha256':P.digest(raw),'component_sha256':P.digest((COMPONENT/'protected_inputs.py').read_bytes()),'native_engine_or_live_store_claim':False,'authority_effect':'none','original_locators_remapped':False,'original_tables_truncated':False,'public_evidence_only':True}
    report['owned_scratch_cleaned']=not own.exists();report_path.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'report':str(report_path),'closure':closure['status'],'unavailable_or_refused':len(omitted),'exact':sum(r['status']=='EXACT-BYTES'for r in observed),'refused_bytes':sum(r['status']!='EXACT-BYTES'for r in observed),'verified_bytes':verified_bytes}))
    return 0 # Observation completed; closure status remains independently REFUSED/PASS.

if __name__=='__main__':sys.exit(main())
