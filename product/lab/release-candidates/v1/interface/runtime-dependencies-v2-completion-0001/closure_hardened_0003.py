"""Revision 3: require complete original proof bindings before any input read."""
from pathlib import Path
import re
import closure as BASE

require=BASE.require
sha=BASE.sha
ROOT=BASE.ROOT
EXPECTED_BINDINGS={
 'product/lab/release-candidates/v1/packaging/R02/packages/0003/selection.json':'3a33fa50ec0e8be7525e8b8a034f8794a240a6f9aff57799953fdcdeb974c9f4',
 'product/lab/release-candidates/v1/boundary-review/0008/native-remediation.json':'57ad3b04cf58c72094d5704f790bfc5c1832826475188485e32ea273e5c270b6',
 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/dependency-selection.json':'ec9e0c2d10e4aca3e54e9a1538c1a6f583d7d4e2059da750c0c8418cd1b61cae',
 'product/lab/release-candidates/v1/interface/runtime-dependencies-v1-completion-0001/source-manifest.json':'ad4b0e91db27ea16cc6481230942e128839d9ec1b16b2105be07525c3513f2a3',
 'product/lab/release-candidates/v1/interface/api-integration-v16/source-manifest.json':'8ac40a51e23b8e528178807792b8ae477aa9c46cd50d92a5b1522c82945413c7',
}

def strict_structure(selection):
    BASE.validate_structure(selection)
    bindings=selection['original_bindings']
    require(all(set(r)=={'path','sha256'} for r in bindings),'closed original binding required')
    require(len(bindings)==len(EXPECTED_BINDINGS) and {r['path']:r['sha256'] for r in bindings}==EXPECTED_BINDINGS,'complete exact original bindings required')
    original=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/dependency-selection.json'
    raw=original.read_bytes();require(sha(raw)==EXPECTED_BINDINGS[original.relative_to(ROOT).as_posix()],'independent original execution selection differs')
    old=BASE.IO.parse(raw)
    expected_wheels={r['path']:r for r in old['inputs'] if r['kind']=='wheel'}
    require(len({r['path'] for r in selection['inputs'] if r['kind']=='wheel'})==8,'duplicate original wheel input')
    for row in selection['inputs']:
        require(isinstance(row['sha256'],str) and re.fullmatch('[a-f0-9]{64}',row['sha256']) is not None,'invalid input digest')
        require(type(row['size_bytes']) is int and row['size_bytes']>=0 and type(row['mode']) is int and 0<=row['mode']<=0o777,'invalid input size/mode')
        p=Path(row['path']);require(p.suffix not in {'.key','.pem','.pyc'} and '..' not in p.parts and not any(x=='.env' or x.startswith('.env.') for x in p.parts),'protected/cache input outside public closure')
        if row['kind']=='wheel':
            require(row['path'] in expected_wheels and all(row[f]==expected_wheels[row['path']][f] for f in ['sha256','size_bytes','mode']),'original wheel digest/size/mode differs')
        elif row['kind']=='interpreter':require(row['sha256']==selection['environment']['interpreter_sha256'],'original interpreter digest differs')
        elif row['kind']=='native-executable':require(row['sha256']=='fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c','original native digest differs')
        elif row['kind']=='host-abi':require(BASE.resolve_soname(row['soname'])==p,'host ABI soname target differs')
    tool=selection['inspection_tool']
    require(set(tool)=={'kind','path','sha256','size_bytes','mode','destination','classification'} and tool['kind']=='inspection-tool' and tool['path']==str(BASE.READELF) and tool['destination'] is None and tool['classification']=='public-installation-bytes','closed exact inspection tool required')
    members=selection['wheel_members'];bindings=selection['wheel_elf_bindings']
    require(len(bindings)==len({r['destination'] for r in bindings}),'duplicate wheel ELF binding')
    for row in bindings:
        require(set(row)=={'path','sha256','size_bytes','mode','destination'},'closed wheel ELF binding required')
        require(row['destination'] in members and row['path']==str(BASE.V1/'installations/0001'/row['destination']) and {f:row[f] for f in ['sha256','size_bytes','mode']}==members[row['destination']],'wheel ELF original provenance differs')
    require(all(set(row)=={'sha256','size_bytes','mode'} and isinstance(n,str) and n.startswith('deps/') and '..' not in Path(n).parts for n,row in members.items()),'closed original wheel member required')
    return selection

def load_selection(path,pin):
    selection,raw=BASE.load_selection(path,pin)
    strict_structure(selection)
    return selection,raw

def build_selection(previous):
    paths,_=BASE.stdlib_files()
    # Refuse protected-looking files by name before discovery reads any bytes.
    for p in paths:require(p.suffix not in {'.key','.pem','.pyc'} and not any(x=='.env' or x.startswith('.env.') for x in p.parts),'protected/cache file in public stdlib discovery')
    selection=BASE.build_selection(previous);strict_structure(selection);return selection

def preflight(path,pin):
    selection,raw=load_selection(path,pin)
    result=BASE.preflight(path,pin)
    require(Path(path).read_bytes()==raw,'selection changed during strict preflight')
    result['complete_original_bindings_required']=True
    result['revision']='strict-original-provenance-0003'
    return result

def install(path,pin,parent,parent_identity,name):
    preflight(path,pin)
    result=BASE.install(path,pin,parent,parent_identity,name)
    preflight(path,pin)
    return result

def cold_probe(destination,selection):
    strict_structure(selection)
    return BASE.cold_probe(destination,selection)

def verify_installed(destination,selection):
    strict_structure(selection)
    return BASE.verify_installed(destination,selection)

installed_files=BASE.installed_files
python_command=BASE.python_command
