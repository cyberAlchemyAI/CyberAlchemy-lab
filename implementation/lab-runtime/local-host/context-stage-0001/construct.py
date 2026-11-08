"""Pure Context stage/role selection; never creates the selected stage or Context effect."""
from __future__ import annotations
import json
import os
from pathlib import Path
import stage as S
import roles as R

FAMILY_SELECTION=S.LOCAL/'context-family-0001/selection.json'
NATIVE=Path('/tmp/cal-mapper-only-dev-20261020-0001-release3/input/lab-context-native-reader')
NATIVE_SHA='fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
CONTEXT_REL=S.INTERFACE+'/docker-context-20261020-0001'

def encoded(value):return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()

def construct():
    family=json.loads(S.held_read(S.REPO,FAMILY_SELECTION.relative_to(S.REPO).as_posix(),
                                  R.FAMILY_SELECTION_SHA,capture=True)['bytes'])
    S.require(family['context_launch']=='REFUSED' and
              family['selected_existing_root']==str(S.ROOT) and
              family['future_exclusive_stage_created'] is False and
              family['family']['native_executable_container_path']==
                  '/attempt/input/lab-context-native-reader',
              'reviewed family selection differs')
    future=Path(family['future_exclusive_stage_root'])
    S.require(future.is_absolute() and not os.path.lexists(future.parent),
              'future exclusive Context stage name occupied')
    inventory=S.verify_inventory()
    native=S.held_read(NATIVE.parent,NATIVE.name,NATIVE_SHA,limit=32*1024*1024)
    S.require(native['mode']=='0755' and native['uid']==os.geteuid() and
              native['gid']==os.getegid() and native['size']==20243600,
              'selected native mount input differs')
    projected,role_proof=R.project()
    api=[]
    for item in family['projected_api']:
        name=Path(item['path']).name
        path=S.LOCAL/'context-family-0001/generated/api-v25'/name
        raw=S.held_read(S.REPO,path.relative_to(S.REPO).as_posix(),
                        item['sha256'],capture=True)['bytes']
        S.require(len(raw)==item['size'],'projected API file size differs')
        api.append({'path':item['path'],'sha256':item['sha256'],'size':len(raw),
                    'source':'reviewed_context_family_projection'})
    public=[]
    for item in family['staged_public_partition']['copy_exact_public_from_checkout']:
        info=S.held_read(S.REPO,item['path'],item['sha256'])
        public.append({'path':item['path'],'sha256':item['sha256'],'size':info['size'],
                       'mode':info['mode'],'source':'exact_public_checkout'})
    S.require(len(public)==512 and len(api)==5 and len(projected)==6,
              'future stage additive closure differs')
    binding=R.implementation_binding()
    generated=[{'path':CONTEXT_REL+'/'+name,'sha256':S.sha(raw),'size':len(raw),
                'source':'effect_disabled_context_role'} for name,raw in sorted(projected.items())]
    generated.append({'path':CONTEXT_REL+'/implementation-binding.json',
                      'sha256':S.sha(binding),'size':len(binding),
                      'source':'same_family_reader_metadata'})
    existing=[{'path':x['path'],'sha256':x['sha256'],'source':'reviewed_mapper_family'}
              for x in inventory['reader_stage_public']+inventory['mapper_source_files']+
                       inventory['mapper_package_members']+[inventory['mapper_package_manifest']]]
    private={'path':S.ARCHIVE,'sha256':inventory['reader_stage_protected_binding']['sha256'],
             'source':'PROTECTED_REVIEWED_BINDING_BODY_UNREAD_UNCOPIED'}
    names=[x['path'] for x in existing+[private]+public+api+generated]
    S.require(len(names)==len(set(names))==1570 and len(existing)==1045,
              'Context staged file namespace collision or gap')
    selection={'schema_version':'lab-context-stage-role-selection/v1-candidate',
        'status':'EFFECT_DISABLED_NO_PRIVATE_COPY_OR_CONTEXT_IMPORT',
        'source_family_root':str(S.ROOT),'future_exclusive_stage_root':str(future),
        'container_root':'/workspace','container_native_path':'/attempt/input/lab-context-native-reader',
        'native_source_path':str(NATIVE),'native_sha256':NATIVE_SHA,
        'root_mount_mode':'ro','context_output_mount':
            '/workspace/'+CONTEXT_REL+'/packages',
        'context_output_mount_mode':'rw','native_mount_mode':'ro',
        'existing_family_public':existing,
        'protected_family_binding':private,
        'exact_public_checkout_additions':public,
        'projected_api_additions':api,
        'projected_context_additions':generated,
        'selected_root_files_including_protected':1046,
        'future_root_file_count_if_protected_copied_under_separate_effect':1570,
        'protected_archive_metadata':inventory['reader_stage_protected_binding'],
        'mapper_package_files':55,
        'role_projection_proof_sha256':S.sha(encoded(role_proof)),
        'source_reader_mapper_bindings':'REVIEWED_SAME_FAMILY',
        'public_api_schema_closure':'REVIEWED_STATIC_NOT_IMPORTED',
        'source_view_dynamic_schema_join':'DEFERRED_TO_SIGNED_CONTEXT_EFFECT',
        'authorization_sha256':'DUMMY_UNMINTED',
        'policy_sha256':'DUMMY_UNMINTED',
        'original_context_build_provision':'STILL_UNPROJECTED_EFFECT_SITE',
        'context_source_manifest':'REFUSED','context_import':'REFUSED',
        'context_launch':'REFUSED','protected_body_read':False,
        'protected_body_copied':False,'effect':'NOT_RUN'}
    return selection,projected,role_proof,binding

def final_context_manifest(*_args,**_kwargs):raise S.Refused('protected copy, JIT and runtime import absent')
def launch(*_args,**_kwargs):raise S.Refused('effect-disabled stage/role candidate')

if __name__=='__main__':
    value,*_=construct()
    print(json.dumps({'status':value['status'],'selected_root_files':1046,
                      'future_root_files':1570,'private_body':'UNREAD_UNCOPIED',
                      'context_launch':'REFUSED'},sort_keys=True))
