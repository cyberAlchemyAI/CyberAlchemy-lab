"""Exact declared integrated closure; no directory glob can add package inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import stat
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
API = ROOT/'product/lab/release-candidates/v1/interface/api-integration-v73-t15-learning-selector-0001'
SOURCE = '5127caa2d6a829303f12af398912eeb98bb2b52580af40614e4925080224f4e7'
PROFILE = '131fdcaafdf59c082546fdf94567fc7f39cc09d302466866f83b2d06eeccb6c5'
INSTALL = Path('/home/vlad_/.local/share/cyberalchemy-lab/native-install/t22-0001')
SUPPORT = ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001'
DEPENDENCY = ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
DEPENDENCY_SHA = '2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
sha = lambda raw:hashlib.sha256(raw).hexdigest()


def need(value, reason):
    if not value:
        raise ValueError(reason)


def binding(path):
    return {'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())}


def forbidden(path):
    return (path.suffix in ('.key','.pem','.p12','.pfx','.pyc') or
            any(part in ('.ssh','.aws','__pycache__') or part=='.env' or part.startswith('.env.')
                for part in path.parts))


def collect(*, verify=False):
    need(sha((API/'source-manifest.json').read_bytes())==SOURCE
         and sha((API/'contract-profile.json').read_bytes())==PROFILE,'integrated seed differs')
    source = json.loads((API/'source-manifest.json').read_bytes())
    profile = json.loads((API/'contract-profile.json').read_bytes())
    declared_external = {row['path'] for row in profile['files'] if Path(row['path']).is_absolute()}
    family = (ROOT/source['family_source_manifest_binding']['path']).parent.parent
    engine = (ROOT/source['engine_profile_binding']['path']).parent.parent
    rows = {}
    reasons = {}
    dynamic_host = []
    provenance = []
    archive_handle = json.loads((family/'source/packages/0001/archive-handle.json').read_bytes())
    metadata = []
    def add(row, reason, *, active=True):
        need(type(row) is dict and set(row)=={'path','sha256'},'closed package input binding required')
        path = Path(row['path'])
        if str(path)==archive_handle['path']:
            dynamic_host.append({'path':str(path),'sha256':row['sha256'],'classification':'private-fixture-archive-reference-not-public-payload'})
            return
        if not active and row['path'] in rows and rows[row['path']]!=row['sha256']:
            provenance.append({**row,'disposition':'historical-provenance-not-an-active-filesystem-input'})
            return
        if not active and (forbidden(path) or '..' in path.parts or
            (path.is_absolute() and not str(path).startswith(('/usr/','/home/vlad_/.cargo/','/home/vlad_/.rustup/')))):
            provenance.append({**row,'disposition':'historical-private-or-cache-reference-not-read-or-packaged'})
            return
        need(path.as_posix()==row['path'] and '..' not in path.parts and not forbidden(path),
             'unsafe or secret-looking declared package input: '+str(path))
        if path==INSTALL/'installation.json':
            dynamic_host.append(row)
            return
        previous = rows.setdefault(row['path'],row['sha256'])
        need(previous==row['sha256'],'conflicting declared package input: '+row['path'])
        reasons.setdefault(row['path'],set()).add(reason)
    for row in source['files']:
        add(row,'integrated-source-member')
    for row in profile['files']:
        add(row,'declared-profile-member')
    add(binding(API/'source-manifest.json'),'integrated-source-selection')
    add(binding(API/'contract-profile.json'),'integrated-profile-selection')
    metadata.append((API/'source-manifest.json',SOURCE))
    # Expand only metadata selected by the current Source/engine manifests.
    # Historical fixtures remain exact data; their deliberately invalid test
    # manifests are never parsed or used as discovery instructions.
    for key,row in source.items():
        if type(row) is dict and set(row)=={'path','sha256'}:
            add(row,'integrated-'+key)
            if key.startswith('family_') or key=='engine_profile_binding':
                metadata.append((ROOT/row['path'],row['sha256']))
    seen = set()
    def walk(value):
        if type(value) is dict:
            if '$schema' in value:
                return  # A schema's properties are data, not file locators.
            if 'kind' in value and 'node_id' in value:
                return  # Artifact bodies contain provenance, not import edges.
            if (set(value)=={'path','sha256'} and type(value['path']) is str
                and type(value['sha256']) is str):
                add(value,'current-family-closed-reference',active=False)
                path = ROOT/value['path']
                if (not Path(value['path']).is_absolute() and path.suffix=='.json'
                    and (path.is_relative_to(family) or path.is_relative_to(engine))):
                    metadata.append((path,value['sha256']))
            else:
                for item in value.values():
                    walk(item)
        elif type(value) is list:
            for item in value:
                walk(item)
    while metadata:
        path,pin = metadata.pop()
        if (str(path),pin) in seen:
            continue
        seen.add((str(path),pin))
        need(path.is_file() and not path.is_symlink(),'selected current metadata missing or linked')
        raw = path.read_bytes()
        need(sha(raw)==pin,'selected current metadata bytes differ')
        try:
            value = json.loads(raw)
        except (ValueError,UnicodeError):
            # Binary public artifacts and invalid historical fixtures can be
            # exact selected data, but cannot expand the metadata graph.
            continue
        walk(value)
    sys.path.insert(0,str(SUPPORT))
    import closure_hardened_0003 as dependencies
    selected,_ = dependencies.load_selection(DEPENDENCY,DEPENDENCY_SHA)
    native = dependencies.installed_files(selected)
    need(len(native)==1010,'original native payload count differs')
    result = []
    for locator,pin in sorted(rows.items()):
        path = Path(locator)
        if path.is_absolute():
            need(str(path) in declared_external or str(path).startswith(('/usr/','/home/vlad_/.cargo/','/home/vlad_/.rustup/')),
                 'undeclared private/external input cannot enter package: '+str(path))
            destination = 'host-inputs/'+path.as_posix().lstrip('/')
            classification = 'public-host-input-snapshot'
        else:
            path = ROOT/path
            destination = 'repository/'+locator
            classification = 'public-repository-input'
        info = path.lstat()
        original_link = None
        if stat.S_ISLNK(info.st_mode) and locator in declared_external:
            # Some inactive toolchain declarations name a public executable
            # alias. Preserve the exact selected target bytes as an ordinary
            # snapshot member; never recreate an untrusted archive symlink or
            # present its old host inode as a fresh installation attestation.
            original_link = str(path)
            path = path.resolve(strict=True)
            info = path.lstat()
        need(stat.S_ISREG(info.st_mode),'declared package input absent, linked or nonregular: '+str(path))
        if verify:
            need(sha(path.read_bytes())==pin,'declared package input hash differs: '+str(path))
        result.append({'member':destination,'input_path':str(path),'sha256':pin,
                       'size_bytes':info.st_size,'mode':stat.S_IMODE(info.st_mode),
                       'classification':classification,'selection_reasons':sorted(reasons[locator]),
                       'declared_public_alias_materialized_as_data':original_link})
    for name,row in sorted(native.items()):
        path = INSTALL/name
        info = path.lstat()
        need(stat.S_ISREG(info.st_mode) and info.st_size==row['size_bytes']
             and stat.S_IMODE(info.st_mode)==row['mode'],'native member metadata differs')
        if verify:
            need(sha(path.read_bytes())==row['sha256'],'native member bytes differ')
        result.append({'member':'native-payload/'+name,'input_path':str(path),**row,
                       'classification':'public-native-payload',
                       'selection_reasons':['original-exact-1010-native-closure']})
    need(len({row['member'] for row in result})==len(result),'duplicate package member')
    return {'schema_version':'lab-integrated-declared-closure/v1','authority_effect':'none',
            'api_source_binding':binding(API/'source-manifest.json'),
            'api_profile_binding':binding(API/'contract-profile.json'),
            'dependency_selection_binding':binding(DEPENDENCY),
            'dataset':{'family':'legacy-local-4636eca980a5d94d',
                       'store':'completion-legacy-local-4636eca980a5d94d',
                       'scope':'project:cyberalchemy-v2-to-lab-migration'},
            'members':sorted(result,key=lambda row:row['member']),
            'member_count':len(result),'payload_size_bytes':sum(row['size_bytes'] for row in result),
            'native_payload_files':1010,'byte_verification_completed':verify,
            'generated_host_receipts_excluded':dynamic_host,
            'historical_provenance_not_import_edges':provenance,
            'private_fixture_archive_included':False,
            'installed_API_executed':False,'portable_successor_required':True,
            'claim_ceiling':'Exact declared byte inventory only. Fresh host metadata, fixture archive reconstruction and executable portable successor remain separate.'}


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify',action='store_true')
    args = parser.parse_args()
    value = collect(verify=args.verify)
    output = HERE/('DECLARED-CLOSURE-VERIFIED-0001.json' if args.verify else 'DECLARED-CLOSURE-0001.json')
    with output.open('x') as stream:
        stream.write(json.dumps(value,sort_keys=True,indent=2)+'\n')
    print(json.dumps({key:value[key] for key in ('member_count','payload_size_bytes','native_payload_files',
          'byte_verification_completed','installed_API_executed')},sort_keys=True))
