"""Emit an O_EXCL public family pin manifest only after all native/audit passes."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
NAME='legacy-local-4636eca980a5d94d';FAMILY=HERE/'instances'/NAME
EXPECTED_REPORTS={
 'source':'71425736b22ac9eec4cf9a6f1f1f63757f759b0951e66e849b43bc5aa82812ef',
 'cold':'ae31849b29f2b25cca3ba7c547f6794645527e25c52b4f59941fdb17a50f1dc6',
 'reader':'d74145a950b66be05019cc7d583698cc9c5cb333d74ca01d70349de10b96b0fb',
 'mapped':'22c84fde92b20091e96a840985b8d4985eb4c21b9ec1d436c8ccc1d05dd50041',
 'context':'b130a6d95f63e96c327fa6ee6b7c86be6509a57d0c0c9ada9c3c697499d85f62',
}
def require(ok,message):
    if not ok:raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def parse(p):return json.loads(p.read_bytes())
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())}
def main():
    reports={}
    for phase,pin in EXPECTED_REPORTS.items():
        p=HERE/'reports'/(NAME+'-'+phase+'-attempt0002.json')
        require(sha(p.read_bytes())==pin and parse(p)['result']=='PASS','observed actual phase receipt differs '+phase)
        reports[phase]=binding(p)
    p=HERE/'reports'/(NAME+'-independent-closure-audit-0004.json');audit=parse(p)
    expected={'signed_subjects':619,'baseline_materials':859,'source_records':26,'signed_transaction_targets':[2,26],'original_targets':28,'current_Lessons':1}
    require(audit['result']=='PASS' and audit['counts']==expected and audit['mapper_nodes']==18
            and audit['mapper_edges']==12 and audit['semantic_governance_cursor']==30
            and audit['Context_carriers']==35,'actual independent closure audit differs')
    reports['independent_actual_closure']=binding(p)
    roles={role:{'source':binding(FAMILY/role/'source-manifest.json')} for role in ('source','reader','mapped','context')}
    for role in ('source','mapped','context'):
        roles[role]['package']=binding(FAMILY/role/'packages/0001/manifest.json')
    require(roles['source']['source']['sha256']=='f07c87624a5cc133e00f36737674685e3aa5a5635a112a79319101b6d5f27ff2'
            and roles['source']['package']['sha256']=='da4d09f2f2953044859daad8a8830ecbb0fd198164ad10e5611d6c491056d0ee','independent actual Source pins differ')
    for row in roles.values():
        for kind,b in row.items():
            require(sha((ROOT/b['path']).read_bytes())==b['sha256'],'selected manifest changed')
            for member in parse(ROOT/b['path'])['files']:
                path=Path(member['path']);path=path if path.is_absolute() else ROOT/path
                require(path.is_file() and not path.is_symlink() and sha(path.read_bytes())==member['sha256'],'selected member changed '+member['path'])
    engine=HERE/'engine-v3';spec=importlib.util.spec_from_file_location('_integrated_seal_engine',engine/'loader.py');m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    m.verify_engine(m.EnginePins(**parse(engine/'pins.json')))
    engine_pins={name:binding(engine/path) for name,path in [('loader','loader.py'),('manifest','engine-manifest.json'),('pins','pins.json'),('profile','runtime/profile.json')]}
    install=Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001'
    period=parse(FAMILY/'source/packages/0001/period.json');prefix='completion-'+NAME
    result={'schema_version':'lab-integrated-fixture-family-pins/v1-candidate','result':'PASS-native-construction-and-independent-cold-audit',
      'family':FAMILY.relative_to(ROOT).as_posix(),'source_name':'completion-legacy:'+NAME,'period_binding':binding(FAMILY/'source/packages/0001/period.json'),
      'not_before':period['not_before'],'expires_at':period['expires_at'],'roles':roles,'engine':engine_pins,
      'native_installation_receipt':{'path':str(install/'installation.json'),'sha256':sha((install/'installation.json').read_bytes())},
      'ABI':{'python':'3.14.4','jsonschema':'4.23.0','cryptography':'46.0.5'},'counts':expected,
      'mapper':{'nodes':18,'edges':12,'semantic_governance_cursor':30},'Context_carriers':35,
      'source_cut':parse(FAMILY/'mapped/packages/0001/mapping.json')['source_cut'],
      'current_identities':{'Principal':'principal:'+prefix,'Profile':'agent-profile:'+prefix,'Assignment':'agent-assignment:'+prefix,'Work':'work:'+prefix,'Context':'context:'+prefix,'Agent_Contract':'challenge-contract:'+prefix+'-agent-contest','Lesson':'operational-lesson:'+prefix+'-bounded-Session-review'},
      'signed_baseline_input_bindings':audit['signed_baseline_input_bindings'],'retained_witnesses':audit['retained_witnesses'],'receipts':reports,
      'claim_ceiling':'Construction and actual cold closure only. No integrated API regression, new native challenge or final-family resolution has run yet. Prior API60 origin pins cannot be relabelled as this family. Historical witness retained, no Session memory rehydration.',
      'fixture_only':True,'authority_effect':'none','actual_owner_outcome':None,'shared_API_qualified':False}
    raw=(json.dumps(result,indent=2,sort_keys=True)+'\n').encode();p=HERE/'INTEGRATED-FAMILY-PINS-0001.json';fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    print(json.dumps({'result':'PASS','binding':binding(p)},sort_keys=True),flush=True)
if __name__=='__main__':main()
