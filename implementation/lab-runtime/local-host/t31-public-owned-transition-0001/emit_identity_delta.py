"""Add original kindless input identity axes without changing selected cuts."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
HELPER='''
def original_identity(body,header):
    """Use the original carrier's declared identity axis after schema validation."""
    fields={'cal.artifact-type.goal/v1':'goal_id',
            'cal.artifact-type.coordination-context/v2':'coordination_context_id',
            'cal.artifact-type.project-identity/v1':'project_id',
            'cal.artifact-type.project-identity/v2':'project_id',
            'cal.artifact-type.product-identity/v2':'product_id',
            'cal.artifact-type.repository-migration-manifest/v1':'migration_manifest_id'}
    field=fields.get(header['carrier_ref'],'node_id')
    identity=body.get(field)
    need(type(identity) is str and bool(identity) and identity==header['identity_ref']
         and header['version_ref'].startswith(identity+'@'),'semantic exact identity/revision differs')
    return identity
'''
def emit(out):
    base=HERE/'api73-reference-overlay-0002';need=lambda ok:None if ok else (_ for _ in ()).throw(ValueError('exact reviewed predecessor required'))
    originals={name:(base/name).read_bytes() for name in ('service.py','owned_workflow_transition.py','owned_workflow_semantics.py')}
    need(hashlib.sha256(originals['owned_workflow_transition.py']).hexdigest()=='a9dc894b127a0054d28852b94f085858a63789f5b4ac349ce2d5a5e35848d5cb')
    need(hashlib.sha256(originals['owned_workflow_semantics.py']).hexdigest()=='1f099731a57f852664926fc0a0ae0e4a03c88618e62ea0648820b2332b22730a')
    old="""            identity=body.get('node_id',body.get('goal_id',body.get('coordination_context_id',body.get('project_id'))))
            need(identity==h['identity_ref'] and h['version_ref'].startswith(identity+'@') and body.get('authority_effect')=='none','semantic exact identity/authority differs')"""
    text=originals['owned_workflow_transition.py'].decode();need(text.count(old)==1)
    text=text.replace(old,"            SEM.original_identity(body,h)\n            need(body.get('authority_effect')=='none','semantic exact authority differs')",1)
    sem=originals['owned_workflow_semantics.py'].decode()+HELPER
    ast.parse(text);ast.parse(sem);out.mkdir(mode=0o700,parents=True,exist_ok=False)
    (out/'service.py').write_bytes(originals['service.py']);(out/'owned_workflow_transition.py').write_text(text);(out/'owned_workflow_semantics.py').write_text(sem)
    result={'predecessor_overlay':'api73-reference-overlay-0002','changes':['carrier-selected original kindless ProductIdentity/product_id and RepositoryMigrationManifest/migration_manifest_id axes','Goal/Coordination/Project explicit original identity axes; all ordinary node_id carriers unchanged'],
      'original_schema_validation_before_identity_unchanged':True,'Source_permission_UTC_actual_object_guards_unchanged':True,
      'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir()},'actual_API_call_qualified':False,'authority_effect':'none'}
    (out/'IDENTITY-DELTA-PINS.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);print(json.dumps(emit(p.parse_args().output),sort_keys=True))
