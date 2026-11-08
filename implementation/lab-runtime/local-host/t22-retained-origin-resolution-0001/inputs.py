"""Closed retained native-origin data; no old signer or runtime dependency."""
import base64
import hashlib
import json
import os
from pathlib import Path
import stat
ROOT=Path(__file__).resolve().parents[4]
PUBLIC_SEED_SHA='491052937d701601b105eaa30b451358f7a2f4e00cc3a0d943ebd63e7370a005'
PINS={
 'native-submission.json':'ac9bb4baa9a295cab8b6cbbb80a2ed16b350c36786677c602350f5dc25284cf4',
 'native-call-observation.json':'acbacb89c0c69adc3fd02c1d29a3208cc30c1ee37b9fffda7eeb31c49aac7970',
 'native-candidate.json':'71be1ed90197329e7405bd3ad709721a440d8617b19076edc396f3bd4767d9e8',
 'native-request.json':'b8bce552c5a1866a652543885bf523a7774f5cda8959f13586356ace3ab380b6',
 'original-work.json':'ea1da27067e2cc3b280cf7f9b9818c06bae48100ba1a87c97e8d7e70c64cc474',
 'original-contract.json':'a18f4cf08925fa12f893853fa9443af0a81ce4f04ef35a04c0d2e65d9b569a6b'}
def need(ok,reason):
    if not ok:raise ValueError(reason)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def enc(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def read(path):
    need(not path.is_symlink() and not any(p.is_symlink() for p in path.parents),'linked origin member')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        st=os.fstat(fd);need(stat.S_ISREG(st.st_mode) and st.st_uid==os.getuid() and stat.S_IMODE(st.st_mode)==0o600
          and st.st_nlink==1 and st.st_size<16*1024*1024,'private bounded origin member required')
        with os.fdopen(fd,'rb',closefd=False) as stream:raw=stream.read(16*1024*1024)
        need(len(raw)==st.st_size,'origin member changed during read');return raw
    finally:os.close(fd)
def write(path,raw):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
def read_bundle(path):
    """Only the independently audited exact seed may be publicly readable."""
    need(not path.is_symlink() and not any(p.is_symlink() for p in path.parents),'linked origin bundle')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        st=os.fstat(fd);need(stat.S_ISREG(st.st_mode) and st.st_nlink==1 and st.st_size<1024*1024
          and not (stat.S_IMODE(st.st_mode)&0o022),'bounded nonwritable seed required')
        with os.fdopen(fd,'rb',closefd=False) as stream:raw=stream.read(1024*1024)
        need(len(raw)==st.st_size,'origin bundle changed during read')
        private=st.st_uid==os.getuid() and stat.S_IMODE(st.st_mode)==0o600
        need(private or sha(raw)==PUBLIC_SEED_SHA,'private bounded bundle or exact audited public seed required')
        return raw
    finally:os.close(fd)
def load(root):
    root=Path(root).absolute();need(root.resolve()==root and root.is_dir() and not root.is_relative_to(ROOT)
      and root.stat().st_uid==os.getuid() and stat.S_IMODE(root.stat().st_mode)==0o700,'private external native origin root required')
    need(set(p.name for p in root.iterdir())==set(PINS)|{'manifest.json'},'closed native origin data inventory required')
    manifest=json.loads(read(root/'manifest.json'))
    need(set(manifest)=={'schema_version','members','actual_owner_outcome','authority_effect'} and manifest['schema_version']=='lab-retained-native-origin71/v1'
      and manifest['members']==PINS and manifest['actual_owner_outcome'] is None and manifest['authority_effect']=='none','independent actual origin pins differ')
    rows={name:read(root/name) for name in PINS}
    need({name:sha(raw) for name,raw in rows.items()}==PINS,'actual native origin original bytes changed')
    request=json.loads(rows['native-request.json']);work=json.loads(rows['original-work.json']);contract=json.loads(rows['original-contract.json'])
    need(request['subject']['byte_sha256']==sha(rows['original-work.json']) and request['challenge_contract']['byte_sha256']==sha(rows['original-contract.json'])
      and request['subject']['identity_ref']==work['node_id'] and request['challenge_contract']['identity_ref']==contract['node_id'],
      'actual native request original Work/Contract join differs')
    return rows
def collect(destination):
    """One-time trusted collection; fixture bodies remain private and unmodified."""
    destination=Path(destination).absolute();need(not destination.exists() and not destination.is_relative_to(ROOT),'fresh private origin destination required')
    old=ROOT/'implementation/lab-runtime/local-host/t22-native-agent-contest-0001'
    private=Path.home()/'.local/share/cyberalchemy-lab/t22-native-agent-diagnostics/91755e756e7543e6a42e664fafa744b2'
    rows={'native-submission.json':(old/'LIVE-NATIVE-AGENT-COLD-API71-0001.json').read_bytes(),
      'native-call-observation.json':(old/'NATIVE-AGENT-COLD-CALL-API71-0002.json').read_bytes(),
      'native-candidate.json':read(private/'candidate.json'),'native-request.json':read(private/'request.json')}
    source=ROOT/'implementation/lab-runtime/local-host/t15-integrated-fixture-0001/instances/legacy-local-4636eca980a5d94d/source/packages/0001'
    index=json.loads((source/'record-index.json').read_bytes());request=json.loads(rows['native-request.json'])
    for name,header in [('original-work.json',request['subject']),('original-contract.json',request['challenge_contract'])]:
        selected=[r for r in index if r['version_ref']==header['version_ref']]
        need(len(selected)==1,'exact original native source input locator missing')
        row=selected[0]['original_binding'];raw=(ROOT/row['path']).read_bytes();need(sha(raw)==row['sha256']==header['byte_sha256'],'actual source original differs');rows[name]=raw
    need({name:sha(raw) for name,raw in rows.items()}==PINS,'selected native collection bytes differ')
    destination.mkdir(mode=0o700,parents=True)
    for name,raw in rows.items():write(destination/name,raw)
    write(destination/'manifest.json',enc({'schema_version':'lab-retained-native-origin71/v1','members':PINS,'actual_owner_outcome':None,'authority_effect':'none'}));load(destination)
    return {'private_root':str(destination),'members':PINS,'no_signer_or_credentials_copied':True,'actual_owner_outcome':None,'authority_effect':'none'}
def wrapper(capsule,rows,current_cut):
    need({name:sha(raw) for name,raw in rows.items()}==PINS,'retained source wrapper inputs changed')
    return {'schema_version':'lab-local-retained-Agent-resolution/v1-fixture','original_signed_source':capsule,
      'original_source_records':{'work':base64.b64encode(rows['original-work.json']).decode(),'challenge-contract':base64.b64encode(rows['original-contract.json']).decode()},
      'coordinating_source_cut':current_cut,'original_source_posture':'historical-verified-native-origin','authority_effect':'none'}
def package(root,destination,*,public_seed=False):
    """Retain owner-only custody; an audited explicit seed may ship in the artifact."""
    rows=load(root);body={'schema_version':'lab-private-retained-origin71-bundle/v1','members':PINS,
      'originals_base64':{name:base64.b64encode(raw).decode() for name,raw in rows.items()},
      'data_classification':('SYNTHETIC-retained-native-origin-fixture-public-seed-eligible' if public_seed else 'synthetic-fixture-and-public-protocol-metadata-retained-owner-only'),'authority_effect':'none'}
    raw=enc(body);destination=Path(destination).absolute();need(not destination.is_relative_to(ROOT),'private bundle must remain outside repository')
    write(destination,raw);return {'path':str(destination),'sha256':sha(raw),'size_bytes':len(raw),'no_signer_or_credentials':True}
def provision(bundle,destination):
    """Trusted installer phase provisions closed data under its private root."""
    raw=read_bundle(Path(bundle).absolute());body=json.loads(raw)
    need(set(body)=={'schema_version','members','originals_base64','data_classification','authority_effect'}
      and body['schema_version']=='lab-private-retained-origin71-bundle/v1' and body['members']==PINS
      and body['authority_effect']=='none' and body['data_classification'] in ('synthetic-fixture-and-public-protocol-metadata-retained-owner-only','SYNTHETIC-retained-native-origin-fixture-public-seed-eligible')
      and type(body['originals_base64']) is dict and set(body['originals_base64'])==set(PINS),'closed classified fixture bundle required')
    rows={name:base64.b64decode(encoded,validate=True) for name,encoded in body['originals_base64'].items()}
    need({name:sha(raw) for name,raw in rows.items()}==PINS,'private fixture payload changed')
    destination=Path(destination).absolute();need(not destination.is_relative_to(ROOT) and '..' not in destination.parts,'external canonical private destination required')
    if destination.exists():load(destination);return {'result':'already-provisioned-exact-fixture-origin','private_root':str(destination),'bundle_sha256':sha(raw)}
    need(not any(p.is_symlink() for p in destination.parents),'linked fixture destination ancestor')
    destination.mkdir(mode=0o700,parents=True)
    for name,raw_member in rows.items():write(destination/name,raw_member)
    write(destination/'manifest.json',enc({'schema_version':'lab-retained-native-origin71/v1','members':PINS,'actual_owner_outcome':None,'authority_effect':'none'}))
    load(destination);return {'result':'provisioned-exact-fixture-origin','private_root':str(destination),'bundle_sha256':sha(raw),'no_old_signer_or_runtime_required':True,'authority_effect':'none'}
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='mode',required=True)
    collect_parser=sub.add_parser('collect');collect_parser.add_argument('destination',type=Path)
    package_parser=sub.add_parser('package');package_parser.add_argument('origin_root',type=Path);package_parser.add_argument('destination',type=Path)
    package_parser.add_argument('--public-seed',action='store_true')
    provision_parser=sub.add_parser('provision');provision_parser.add_argument('bundle',type=Path);provision_parser.add_argument('destination',type=Path)
    args=p.parse_args()
    value=collect(args.destination) if args.mode=='collect' else package(args.origin_root,args.destination,public_seed=args.public_seed) if args.mode=='package' else provision(args.bundle,args.destination)
    print(json.dumps(value,sort_keys=True))
