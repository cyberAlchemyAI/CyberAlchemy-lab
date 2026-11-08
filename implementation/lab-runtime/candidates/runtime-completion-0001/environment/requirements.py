"""Pure metadata adapter for the complete original T07 executable closure.

No referenced source is opened, imported or executed here. Independent original
bytes select the prior wheel/proof origins. Actual byte/mode/ELF observation and
installation are separate required consumers, never inferred from this result.
"""
from pathlib import PurePosixPath
from lab_contracts.codec import Refusal, need, closed, sha
from lab_selectors.anchors import relative
from .body_json import parse_original

CONFIG = {'locale':'C','python_flags':['-I','-X','utf8','-B','-S'],
          'loader_cache':False,'ambient_environment_inherited':False}
VERSIONS = {'attrs':'25.4.0','cffi':'2.0.0','cryptography':'46.0.5',
    'jsonschema':'4.23.0','jsonschema-specifications':'2023.12.1',
    'pycparser':'2.23','referencing':'0.36.2','rpds-py':'0.27.1'}
LOADER = 'ld-linux-x86-64.so.2'
SOURCE_SHA = '8ac40a51e23b8e528178807792b8ae477aa9c46cd50d92a5b1522c82945413c7'
ORIGINAL_SELECTION_SHA = '2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
ORIGINAL_BINDINGS = {
 'product/lab/release-candidates/v1/packaging/R02/packages/0003/selection.json':'3a33fa50ec0e8be7525e8b8a034f8794a240a6f9aff57799953fdcdeb974c9f4',
 'product/lab/release-candidates/v1/boundary-review/0008/native-remediation.json':'57ad3b04cf58c72094d5704f790bfc5c1832826475188485e32ea273e5c270b6',
 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/dependency-selection.json':'ec9e0c2d10e4aca3e54e9a1538c1a6f583d7d4e2059da750c0c8418cd1b61cae',
 'product/lab/release-candidates/v1/interface/runtime-dependencies-v1-completion-0001/source-manifest.json':'ad4b0e91db27ea16cc6481230942e128839d9ec1b16b2105be07525c3513f2a3',
 'product/lab/release-candidates/v1/interface/api-integration-v16/source-manifest.json':SOURCE_SHA,
}
PRIOR_PATH = 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/dependency-selection.json'
INPUT_FIELDS = ('kind','path','sha256','size_bytes','mode','destination','classification')

def digest(value):
    need(type(value) is str and len(value)==64 and all(c in '0123456789abcdef' for c in value), 'ORIGIN_DIGEST')

def content(row):
    digest(row['sha256'])
    need(type(row['size_bytes']) is int and 0<=row['size_bytes']<2**63, 'ORIGIN_SIZE')
    need(type(row['mode']) is int and 0<=row['mode']<=0o777, 'ORIGIN_MODE')

def absolute(value):
    need(type(value) is str and value.startswith('/'), 'ORIGIN_ABSOLUTE')
    relative(value[1:])
    need(str(PurePosixPath(value))==value, 'ORIGIN_EXACT_PATH')
    return PurePosixPath(value)

def soname(value):
    need(type(value) is str and value and '/' not in value and '\\' not in value
         and '\0' not in value and value not in ('.','..'), 'ABI_SONAME')

def inspect_execution_requirements(raw, expected_sha256, *, prior_raw, repository):
    """Select exact original closure metadata. This is never a runtime guard.

    Caller selects expected_sha256 independently before obtaining raw. Prior
    original selection has a fixed historical digest; a coherent candidate edit
    cannot repin its original wheels or source-proof identity.
    """
    try:
        digest(expected_sha256)
        need(expected_sha256==ORIGINAL_SELECTION_SHA and sha(raw)==ORIGINAL_SELECTION_SHA,
             'ORIGINAL_COMPLETE_SELECTION')
        need(sha(prior_raw)==ORIGINAL_BINDINGS[PRIOR_PATH], 'PRIOR_SELECTION')
        root=absolute(repository)
        value=parse_original(raw);prior=parse_original(prior_raw)
        closed(value,('schema_version','authority_effect','actual_owner_outcome','environment',
            'execution_configuration','versions','inputs','elf_graph','wheel_members',
            'wheel_elf_bindings','inspection_tool','original_bindings','excluded_stdlib_inputs',
            'original_full_proof','excluded_protected_inputs','supported_scope','old_disposable_locators'))
        need(value['schema_version']=='lab-runtime-dependency-closure/v2-candidate'
             and value['authority_effect']=='none' and value['actual_owner_outcome'] is None, 'CLOSURE_DOMAIN')
        env=value['environment']
        need(env=={'system':'Linux','machine':'x86_64','implementation':'CPython',
            'python_version':'3.14.4','libc':['glibc','2.43'],'sqlite_version':'3.46.1',
            'interpreter_sha256':'52e0a13e60a981d8c4b6478be2ba5176f69da07948a056bf49cf6f077e30cb41'}, 'R02_ENVIRONMENT')
        need(value['execution_configuration']==CONFIG and value['versions']==VERSIONS, 'EXECUTION_CONFIGURATION')
        old_wheels={row['path']:row for row in prior['inputs'] if row['kind']=='wheel'}
        need(len(old_wheels)==8, 'ORIGINAL_WHEELS')
        inputs=value['inputs'];need(type(inputs) is list and 1<=len(inputs)<=100000, 'INPUT_BOUND')
        destinations={};source_kinds=set();wheel_paths=set();counts={}
        v1=root/'product/lab/release-candidates/v1/interface/runtime-dependencies-v1-completion-0001'
        wheel_root=root/'product/lab/release-candidates/v1/packaging/R02/packages/0003/wheels'
        for row in inputs:
            need(type(row) is dict and type(row.get('kind')) is str, 'ORIGIN_KIND')
            kind=row['kind'];need(kind in ('wheel','interpreter','native-executable','stdlib','host-abi'), 'ORIGIN_KIND')
            closed(row,(*INPUT_FIELDS,*(['soname'] if kind=='host-abi' else [])))
            content(row);path=absolute(row['path']);dest=row['destination'];relative(dest)
            need(dest not in destinations and (kind,row['path']) not in source_kinds, 'ORIGIN_DUPLICATE')
            need(path.suffix not in ('.key','.pem','.pyc') and not any(p=='.env' or p.startswith('.env.') for p in path.parts), 'PROTECTED_ORIGIN')
            need(row['classification']==('host-dependency-public-system-bytes' if kind=='host-abi' else 'public-installation-bytes'), 'ORIGIN_CLASS')
            if kind=='wheel':
                need(path.parent==wheel_root and dest=='wheels/'+path.name and row['path'] in old_wheels, 'WHEEL_ORIGIN')
                need(all(row[k]==old_wheels[row['path']][k] for k in ('sha256','size_bytes','mode')), 'WHEEL_CONTENT')
                wheel_paths.add(row['path'])
            elif kind=='stdlib':
                need(path.is_relative_to('/usr/lib/python3.14') and dest=='lib/python3.14/'+path.relative_to('/usr/lib/python3.14').as_posix(), 'STDLIB_ORIGIN')
            elif kind=='host-abi':
                soname(row['soname'])
                need(path.parent==PurePosixPath('/usr/lib/x86_64-linux-gnu') and dest=='lib/abi/'+row['soname'], 'ABI_ORIGIN')
            else:
                name='python' if kind=='interpreter' else 'lab-context-native-reader'
                need(path==v1/'installations/0001/bin'/name and dest=='bin/'+name and row['mode']==0o755, 'EXECUTABLE_ORIGIN')
                need(row['sha256']==(env['interpreter_sha256'] if kind=='interpreter' else
                    'fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'), 'EXECUTABLE_CONTENT')
            destinations[dest]=row;source_kinds.add((kind,row['path']));counts[kind]=counts.get(kind,0)+1
        need(wheel_paths==set(old_wheels) and counts.get('wheel')==8 and counts.get('interpreter')==1
             and counts.get('native-executable')==1, 'EXECUTABLE_COVERAGE')
        need('lib/python3.14/lib-dynload/_sqlite3.cpython-314-x86_64-linux-gnu.so' in destinations
             and 'lib/abi/libsqlite3.so.0' in destinations, 'SQLITE_COVERAGE')
        bindings=value['original_bindings'];need(type(bindings) is list and len(bindings)==len(ORIGINAL_BINDINGS), 'ORIGINAL_BINDINGS')
        for row in bindings:closed(row,('path','sha256'))
        need({row['path']:row['sha256'] for row in bindings}==ORIGINAL_BINDINGS, 'ORIGINAL_BINDINGS')
        need(value['original_full_proof']=={'source_manifest_sha256':SOURCE_SHA,'rows':24497,
            'retained_original_manifest':True,'rows_elided':False,'private_original_paths_opened':False}, 'ORIGINAL_PROOF')
        tool=value['inspection_tool'];closed(tool,INPUT_FIELDS);content(tool)
        need(tool['kind']=='inspection-tool' and tool['path']=='/usr/bin/x86_64-linux-gnu-readelf'
             and tool['destination'] is None and tool['classification']=='public-installation-bytes', 'INSPECTION_ORIGIN')
        members=value['wheel_members'];need(type(members) is dict and len(members)<=100000, 'WHEEL_MEMBERS')
        for name,row in members.items():
            relative(name);need(name.startswith('deps/') and name not in destinations, 'WHEEL_MEMBER_COLLISION')
            closed(row,('sha256','size_bytes','mode'));content(row)
            need(row['mode']==0o644, 'WHEEL_MEMBER_MODE')
        wheel_elf=set()
        for row in value['wheel_elf_bindings']:
            closed(row,('path','sha256','size_bytes','mode','destination'));content(row)
            name=row['destination'];need(name in members and name not in wheel_elf, 'WHEEL_ELF_SELECTION')
            need(row['path']==str(v1/'installations/0001'/name)
                 and {k:row[k] for k in ('sha256','size_bytes','mode')}==members[name], 'WHEEL_ELF_ORIGIN')
            wheel_elf.add(name)
        graph=value['elf_graph'];need(type(graph) is dict and len(graph)<=100000, 'ELF_GRAPH')
        need({'bin/python','bin/lab-context-native-reader',*wheel_elf}.issubset(graph), 'ELF_COVERAGE')
        need({name for name in graph if name.startswith('deps/')}==wheel_elf, 'WHEEL_ELF_COVERAGE')
        need({row['destination'] for row in inputs if row['kind']=='host-abi'}.issubset(graph), 'ABI_COVERAGE')
        for name,info in graph.items():
            need(name in destinations or name in members, 'ELF_ORIGIN');closed(info,('needed','interpreter'))
            need(type(info['needed']) is list and len(info['needed'])==len(set(info['needed'])) and len(info['needed'])<=1000, 'ELF_NEEDED')
            need(info['interpreter'] is None or info['interpreter']==LOADER, 'ELF_INTERPRETER')
            for target in info['needed']+([LOADER] if info['interpreter'] else []):
                soname(target);need('lib/abi/'+target in graph, 'ELF_TRANSITIVE_ORIGIN')
        need(type(value['supported_scope']) is str and value['supported_scope'], 'SCOPE_CEILING')
        need(value['excluded_protected_inputs']==['private signing keys','Reader grants and custody secrets','live databases','operator state'], 'PROTECTED_EXCLUSIONS')
        for row in value['excluded_stdlib_inputs']:
            closed(row,('path','reason'));absolute(row['path']);need(type(row['reason']) is str and row['reason'], 'EXCLUDED_STDLIB')
        for row in value['old_disposable_locators']:
            closed(row,('path','currently_present','original_digest'));absolute(row['path']);digest(row['original_digest'])
            need(type(row['currently_present']) is bool, 'HISTORICAL_LOCATOR_OBSERVATION')
        return {'schema_version':'lab-execution-requirements/v1','selection_sha256':expected_sha256,
            'original_value':value,'counts':counts,'elf_nodes':len(graph),'wheel_members':len(members),
            'authority_effect':'none','member_bodies_read':0,'runtime_verified':False,
            'remaining':['actual complete bytes/modes/origins','actual ELF graph/ABI and SONAME observation',
              'exact wheel archive membership','complete native semantic closure','installation qualification']}
    except Exception:
        raise Refusal('EXECUTION_REQUIREMENTS_REFUSED') from None
