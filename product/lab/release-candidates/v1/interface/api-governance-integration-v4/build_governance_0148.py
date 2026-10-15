"""Seal only additive governance source; frozen parents are read-only inputs."""
import json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];BASE=HERE.parent/'api-integration-v6'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def row(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())}
def write(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def main():
 write(HERE/'contract-profile.json',{'schema_version':'lab-governance-contract-profile/v1-candidate','implemented_operations':['checkpoint.resolve','admission.apply','capability.adoption.prepare'],'base_source_binding':row(BASE/'source-manifest.json'),'base_contract_profile_binding':{'ref':(BASE/'contract-profile.json').relative_to(ROOT).as_posix(),'sha256':sha((BASE/'contract-profile.json').read_bytes())},'original_operation_catalog_binding':row(ROOT/'docs/proposals/0008-lab-api-contracts/api-contracts.json'),'authority_effect':'none','actual_owner_outcome':None,'canonical_admissions_applied':0,'runtime_activations':0,'claim_ceiling':'Additive independently scoped owned public candidate governance APIs only; no actual human outcome or repository authority.'})
 files=[p for p in HERE.iterdir() if p.is_file() and p.name!='source-manifest.json']
 files.extend(p for p in (HERE.parent/'runtime-byte-custody-v3/runtime').rglob('*') if p.is_file() and '__pycache__' not in p.parts)
 files.extend(p for p in (HERE.parent/'checkpoint-resolution-v1').iterdir() if p.is_file())
 for kind,version in [('principal','v1'),('role','v1'),('role-assignment','v1'),('decision-bundle','v1'),('decision-checkpoint','v1'),('workflow-decision-profile','v1'),('product-capability','v1'),('capability-realization-binding','v2'),('implementation','v1'),('agent-session','v1')]:
  files.extend(ROOT/f'authority/artifact-types/{kind}/{version}/{n}' for n in ('schema.json','fixtures/valid/record.json'))
 dependency_files=set()
 for name in ('schema-inputs.json','contract-profile.json','source-manifest.json','protocol.py','guard.py','source_bridge.py','jcs.py','workspace.py'):
  dependency_files.add(BASE/name)
 dependency_files.update(ROOT/r['path'] for r in json.loads((BASE/'schema-inputs.json').read_bytes())['files'])
 dependency_files.add(ROOT/'docs/proposals/0007-lab-integrated-schema-package/resources.py')
 dependency_files.update((ROOT/'docs/proposals/0008-lab-api-contracts').glob('*.json'))
 dependency_files.update((ROOT/'docs/proposals/0008-lab-api-contracts/schemas').glob('*.json'))
 dependency_files.update((BASE/'schemas').glob('*.json'))
 dependency_files.update(p for p in (HERE.parent/'source8-protocol-v2').rglob('*') if p.is_file() and '__pycache__' not in p.parts)
 dependency_files.add(HERE.parent/'inspection/lab_operator.py');dependency_files.add(HERE.parent/'corrections-v1/loader.py');dependency_files.add(HERE.parent/'coupling/loader.py')
 selection={'schema_version':'lab-governance-execution-dependency-selection/v1-candidate','base_source_sha256':sha((BASE/'source-manifest.json').read_bytes()),'base_profile_sha256':sha((BASE/'contract-profile.json').read_bytes()),'files':[row(p) for p in sorted(dependency_files)],'selection_reason':'Original public protocol/code/schema registry and selected Source8 resource overlays; governance execution uses original-json native publisher with its exact independently replayed signed store baseline. Unrelated historical receipts and fixtures are guarded in complete parent qualification entry/exit rather than every new owned operation.','file_use_closure':['exact original envelope and governance schemas','original resource registry and Source8 override selection','frozen parser/JCS/full file verification code','selected native profile publisher/signature/schema/custody modules','independent live source baseline is freshly rehashed by native replay','private selected owner/channel keys material index and policy are guarded at every host boundary'],'byte_permission_digest_cache':False,'authority_effect':'none'}
 write(HERE/'execution-dependency-selection.json',selection);files.append(HERE/'execution-dependency-selection.json');files.extend(dependency_files)
 files.append(ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json')
 write(HERE/'source-manifest.json',{'schema_version':'lab-governance-api-source/v1-candidate','base_source_sha256':sha((BASE/'source-manifest.json').read_bytes()),'base_profile_sha256':sha((BASE/'contract-profile.json').read_bytes()),'profile_sha256':sha((HERE/'contract-profile.json').read_bytes()),'files':[row(p) for p in sorted(set(files))],'authority_effect':'none','actual_owner_outcome':None,'canonical_admissions_applied':0,'runtime_activations':0})
 print(json.dumps({'source_sha256':sha((HERE/'source-manifest.json').read_bytes()),'profile_sha256':sha((HERE/'contract-profile.json').read_bytes())}))
if __name__=='__main__':main()
