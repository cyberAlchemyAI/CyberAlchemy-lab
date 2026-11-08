"""Pure exact-byte Context role projection; every effect remains refused."""
from __future__ import annotations
import ast
import json
from pathlib import Path
import stage as S

LOCAL=S.LOCAL
RENDER=LOCAL/'context-construction-0003/rendered'
RENDER_FREEZE_SHA='33f253a6bb71c6f7188eb8f966d3d80ca414c3c2321e0d94c0e8efbde4a64d3a'
RENDER_REVIEW_SHA='29c2fdd5a637c2003b25d08c092e7d0bb82b4b5a03ee598935c61fbc6f8b700b'
POLICY_PROJECTOR=LOCAL/'context-policy-0002/projector.py'
POLICY_PROJECTOR_SHA='0b69facfe76975dfc366f14226c1798bb96eb371c98bb4d216b2bb632ec0d1ff'
POLICY_FREEZE_SHA='9aedc04a6f25c2380330223da9a94453aee851a7affcf178f908ed2160aafed6'
POLICY_REVIEW_SHA='6959f5f5dd82addca8827d2a322e92554639a24fba0ca5ee99d886c6377b5416'
FAMILY_SELECTION_SHA='fb91d4d37a1c6183e2edcf08fed39f1e88e9a99582a304b3f0d4dd13c49d8d0a'
ROLES={'__init__.py':'7f3b05a3e452e6794df35715c6f68f98022be7ea6ed3ee5beec00ac95cbd0d69',
       'base.py':'df247c331a17939a7b7e2b9229e2ef6850f4b8fe52973cff388642bbfca5b415',
       'build.py':'f465f1f1f8b9c8269935d9590f4a6006633d8c335416e3b46703a6c190e0711b',
       'control.py':'a8b1ea219f74d085b9d8355e27a0c11444388774e5b76199d7e565efad4d53ba',
       'generation.py':'3a6e41afb837af7a1388491bf6ac98fb9a0289216a3189fdb5404a8e3b0635f4',
       'lifetime-policy.json':'57f1a7b4757b551aefd05ed6efeada6ce416988d14b3aab73a4119f2b3f31e4a'}
SOURCE_SHA='7e0938e70ac00b5308851b5a5a7c7bdb92041efab3be17296998acb4160395c1'
SOURCE_PACKAGE_SHA='f132b3e1908e9e116464ad29c3db7f56ca17d4dee080e60ffa62547dd9588a5b'
READER_SHA='4b61293453ec763f1c3567d3dac114e0d0782a2c58b85bc941ca34a0c974d251'
READER_CODE_SHA='f93a1f218238c05b18a7c355f9bc1363bbf42d2b1d442d03e191e121f8e9c9b9'
MAPPER_SHA='0bd6696a1e33750bca01cdeae65d3a5ae977b433c0e0b608009422161b3c1358'
MAPPER_PACKAGE_SHA=S.MAPPER_MANIFEST_SHA
API_PROFILE_SHA='2ef0657841ba21ba2b68c7987654817ea39deda669bf89207fa406aa89279d64'
AUTH_DUMMY='a'*64
POLICY_DUMMY='b'*64

def sub_once(raw,old,new,role):
    old=old if isinstance(old,bytes) else old.encode()
    new=new if isinstance(new,bytes) else new.encode()
    S.require(raw.count(old)==1,'projection site count differs: '+role)
    projected=raw.replace(old,new,1)
    S.require(projected.replace(new,old,1)==raw,'projection inverse differs: '+role)
    return projected

def policy_control():
    S.held_read(S.REPO,(LOCAL/'context-policy-0002/freeze.json').relative_to(S.REPO).as_posix(),POLICY_FREEZE_SHA)
    S.held_read(S.REPO,(LOCAL/'CONTEXT-POLICY-INDEPENDENT-STATIC-REVIEW-0002.md').relative_to(S.REPO).as_posix(),POLICY_REVIEW_SHA)
    source=S.held_read(S.REPO,POLICY_PROJECTOR.relative_to(S.REPO).as_posix(),
                       POLICY_PROJECTOR_SHA,capture=True)['bytes']
    namespace={'__file__':str(POLICY_PROJECTOR),'__name__':'_pinned_context_policy_projector'}
    exec(compile(source,str(POLICY_PROJECTOR),'exec'),namespace)
    value,proof=namespace['project_control'](AUTH_DUMMY,POLICY_DUMMY)
    S.require(proof['byte_inverse'] is True and proof['auth_projection_proof']['byte_inverse'] is True and
              S.sha(value)==proof['projected_sha256'] and
              value.count(b"AUTH = ROOT / 'authorization/context-development.json'")==1 and
              value.count(b'def read_auth_bytes(')==1 and value.count(b'def read_policy_bytes(')==1,
              'reviewed held AUTH/policy projection differs')
    return value,proof

def project():
    S.held_read(S.REPO,(LOCAL/'context-construction-0003/freeze.json').relative_to(S.REPO).as_posix(),RENDER_FREEZE_SHA)
    S.held_read(S.REPO,(LOCAL/'CONTEXT-CONSTRUCTION-INDEPENDENT-STATIC-REVIEW-0003.md').relative_to(S.REPO).as_posix(),RENDER_REVIEW_SHA)
    S.held_read(S.REPO,(LOCAL/'context-family-0001/selection.json').relative_to(S.REPO).as_posix(),FAMILY_SELECTION_SHA)
    rendered={name:S.held_read(S.REPO,(RENDER/name).relative_to(S.REPO).as_posix(),pin,capture=True)['bytes']
              for name,pin in ROLES.items()}
    guarded_control,guard_proof=policy_control()
    # The reviewed projector must start from precisely the selected v3 role.
    S.require(guarded_control.count(b'_t35_effect_refused()')>=1 and
              rendered['control.py'].count(b'AUTH.read_bytes()')==2,
              'Context v3 control projection basis differs')
    rendered['control.py']=guarded_control
    old_family="PurePosixPath('/tmp/cal-context-construction-20261020-0003/family/legacy-context-dev-20261020-0003')"
    old_snapshot="PurePosixPath('/tmp/cal-context-construction-20261020-0003/snapshot')"
    projected={};ledger=[]
    for name,raw in rendered.items():
        start=raw
        if name.endswith('.py'):
            raw=sub_once(raw,old_family,'PurePosixPath(Path(__file__).resolve().parent)',name+' family')
            raw=sub_once(raw,old_snapshot,'PurePosixPath(Path(__file__).resolve().parent.parents[5])',name+' snapshot')
        if name=='base.py':
            raw=sub_once(raw,"ROOT = Path('/tmp/cal-context-construction-20261020-0003/snapshot')",
                         'ROOT = HERE.parents[5]',name+' root')
            raw=sub_once(raw,"HERE.parent / 'mapped'","HERE.parent / 'docker-mapped-20261020-0001'",name+' mapper')
            for key,old,new in [('MAPPED_PIN','04a22ae3cd37ee70f2e2eb4dcf9a6b2d164fd08382a90c50e2d6a26be8f3f73c',MAPPER_SHA),
                                ('MAPPED_PACKAGE_PIN','ba99b0023708613af17196ff4d5ed3ef9f2e9ddb68de06ab14d374182f5a5b94',MAPPER_PACKAGE_SHA),
                                ('API_PROFILE_PIN','c9b9d88e37ff0e9514727bd71ac0091e0dd4dc59c707fb6b07e713503922d33d',API_PROFILE_SHA)]:
                raw=sub_once(raw,key+" = '"+old+"'",key+" = '"+new+"'",name+' '+key)
        elif name=='build.py':
            for key,old,new in [('SOURCE_PIN','f3cbec21c32dce3938460a1203e6e3f3575608f463aa3f3fffae9f9338a798f2',SOURCE_SHA),
                                ('SOURCE_PACKAGE','8e7b675666308e0e73fb23962b310ea3a89baa48ad6bf2c9cf1c5c9ce9e96964',SOURCE_PACKAGE_SHA)]:
                raw=sub_once(raw,key+" = '"+old+"'",key+" = '"+new+"'",name+' '+key)
        elif name=='generation.py':
            raw=sub_once(raw,"MAPPED_SOURCE_SHA = '04a22ae3cd37ee70f2e2eb4dcf9a6b2d164fd08382a90c50e2d6a26be8f3f73c'",
                         "MAPPED_SOURCE_SHA = '"+MAPPER_SHA+"'",name+' Mapper pin')
        if name.endswith('.py'):
            ast.parse(raw,filename=name)
            S.require(raw.count(b'def _t35_effect_refused():')==1 and
                      raw.count(b"raise RuntimeError('Generated T35 role effects require the uninstalled T02 custody gate')")==1,
                      'effect refusal lost: '+name)
        else:json.loads(raw)
        projected[name]=raw
        ledger.append({'path':name,'selected_preimage_sha256':ROLES[name],
                       'projection_basis_sha256':S.sha(start),
                       'projected_sha256':S.sha(raw),
                       'guarded_auth_policy':name=='control.py'})
    S.require(b'AUTH.read_bytes()' not in projected['control.py'] and
              b'self.path.read_bytes()' not in projected['control.py'] and
              b"AUTH_SHA = '"+AUTH_DUMMY.encode()+b"'" in projected['control.py'] and
              b"MAPPED_PIN = '"+MAPPER_SHA.encode()+b"'" in projected['base.py'],
              'effect-disabled role pins or custody guard differ')
    return projected,{'schema_version':'lab-context-role-projection-proof/v1-candidate',
        'status':'PURE_EFFECT_DISABLED_ROLES_WITH_DUMMY_JIT_PINS',
        'ledger':ledger,'held_auth_policy_proof':guard_proof,
        'dummy_authorization_sha256':AUTH_DUMMY,'dummy_policy_sha256':POLICY_DUMMY,
        'source_sha256':SOURCE_SHA,'source_package_sha256':SOURCE_PACKAGE_SHA,
        'reader_sha256':READER_SHA,'mapper_source_sha256':MAPPER_SHA,
        'mapper_package_sha256':MAPPER_PACKAGE_SHA,'api_profile_sha256':API_PROFILE_SHA,
        'context_source_manifest':'REFUSED','context_launch':'REFUSED','effect':'NOT_RUN'}

def implementation_binding():
    ref='/workspace/'+S.INTERFACE+'/docker-reader-20261020-0001/reader.py'
    return (json.dumps({'schema_version':'lab-original-reader-implementation-evidence/v1-candidate',
        'code_binding':{'ref':ref,'sha256':READER_CODE_SHA},
        'entrypoint_ref':ref+'#SelectedReader.open_signed',
        'environment':{'python':'3.14.4','jsonschema':'4.23.0','cryptography':'46.0.5'},
        'environment_contract_ref':'protocol:R03-selected-R02-reader-environment',
        'authority_effect':'none','actual_owner_outcome':None,
        'claim_ceiling':'Same-family Reader code selection only; JIT issuer and Context effect unrun.'},
        sort_keys=True,separators=(',',':'))+'\n').encode()

def final_context_manifest(*_args,**_kwargs):raise S.Refused('dummy JIT pins and protected stage remain')
def launch(*_args,**_kwargs):raise S.Refused('effect-disabled Context stage/role projection')

if __name__=='__main__':
    files,proof=project()
    print(json.dumps({'roles':len(files),'status':proof['status'],'context_launch':'REFUSED'},sort_keys=True))
