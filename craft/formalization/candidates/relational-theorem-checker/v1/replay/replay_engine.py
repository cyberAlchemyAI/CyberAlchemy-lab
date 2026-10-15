"""Full replay of the named baseline; timestamps never determine currentness."""
from copy import deepcopy
import hashlib
import importlib
import importlib.metadata
import json
from pathlib import Path
import sys
import sysconfig
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'references'))
import resolver as r
s=r.s
BASE=Path(__file__).resolve().parent
PROFILE='f0-three-kind-with-complete-registry-bindings/v1'


def canonical(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()


def seed_paths():
    lean=s.lean_path()
    return ([s.ROOT/s.task('C05')['validation']['acceptance_ref']['path'],
            s.BASE/'demonstrations/l0/demonstration-receipt.json',s.BASE/'demonstrations/l0/input.json',
            s.BASE/'input/normal-form-schema.json',s.BASE/'registry/normalized-registry.json',
            s.BASE/'references/reference-policy.json',s.BASE/'references/resolver.py',
            s.FORMAL/'toolchain-lock.json',lean,lean.parent.parent/'lib/lean/libleanshared.so',
            s.BASE/'execution/support.py',Path(__file__)]+
           sorted((s.BASE/'interfaces/schemas').glob('*.schema.json')))


def dependency_closure():
    discovered={};pending=list(seed_paths())
    lean=s.lean_path();lean_root=lean.parent.parent
    def locate(path,origin):
        p=Path(path)
        s.require(not p.is_absolute() and '..' not in p.parts,'unsafe dependency path: '+path)
        candidates=[s.ROOT/p,s.FORMAL/p,lean_root/p,origin.parent/p]
        found=next((c.resolve() for c in candidates if c.is_file()),None)
        s.require(found is not None,'unresolved dependency: '+path+' in '+str(origin))
        s.require(found.is_relative_to(s.ROOT),'dependency outside project closure')
        return found
    def visit(value,origin):
        if isinstance(value,dict):
            if isinstance(value.get('path'),str) and isinstance(value.get('sha256'),str):
                target=locate(value['path'],origin)
                s.require(s.digest(target)==value['sha256'],'stale nested binding: '+str(target))
                pending.append(target)
            if isinstance(value.get('source_path'),str) and isinstance(value.get('source_sha256'),str):
                target=locate(value['source_path'],origin)
                s.require(s.digest(target)==value['source_sha256'],'stale module binding')
                pending.append(target)
            for child in value.values():visit(child,origin)
        elif isinstance(value,list):
            for child in value:visit(child,origin)
    while pending:
        path=Path(pending.pop()).resolve()
        s.require(path.is_relative_to(s.ROOT),'seed scope escape')
        relative=str(path.relative_to(s.ROOT))
        if relative in discovered:continue
        discovered[relative]=s.binding(path)
        # Accepted execution manifests resolve current sources explicitly. Raw
        # authority documents are bound leaf inputs: historical receipts may
        # describe former canonical output paths legitimately superseded later.
        # Recursively treating those payload claims as current bindings would
        # silently change the selected snapshot's dependency semantics.
        if path.suffix=='.json' and path.is_relative_to(s.BASE):visit(s.read(path),path)
    return [discovered[key] for key in sorted(discovered)]


def runtime_dependencies():
    modules=['json','jsonschema','referencing','attrs','attr','rpds','jsonschema_specifications','typing_extensions']
    files={str(Path(sys.executable).resolve())}
    versions={}
    for name in modules:
        module=importlib.import_module(name);module_path=Path(module.__file__).resolve();root=module_path.parent
        if module_path.name=='__init__.py':
            files.update(str(p) for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
        else:files.add(str(module_path))
        if name!='json':versions[name]=importlib.metadata.version({'rpds':'rpds-py','attr':'attrs'}.get(name,name.replace('_','-')))
    stdlib=Path(sysconfig.get_paths()['stdlib'])
    files.update(str(p) for p in stdlib.rglob('*') if p.is_file() and p.suffix in {'.py','.so'}
                 and not {'site-packages','dist-packages','__pycache__'}.intersection(p.relative_to(stdlib).parts))
    # Pin the standard-library implementations involved in host projection and
    # execution. Their correctness, the OS and supplied truth remain assumptions.
    for name in ['hashlib','pathlib','subprocess','tempfile','shutil','importlib','argparse']:
        module=importlib.import_module(name);path=Path(module.__file__).resolve()
        if path.name=='__init__.py':files.update(str(p) for p in path.parent.rglob('*.py') if '__pycache__' not in p.parts)
        else:files.add(str(path))
    return {'python_version':sys.version,'packages':versions,
            'files':[{'absolute_path':p,'sha256':s.digest(p)} for p in sorted(files)]}


def manifest():
    value={'schema':'relational.replay-dependencies/v1','profile':PROFILE,
           'normalization_version':'source-order-closed-string-qualifiers/v1',
           'roots':[s.binding(p) for p in seed_paths()], 'dependencies':dependency_closure(),
           'host_runtime':runtime_dependencies(),'authority_effect':'none',
           'trust':['source interpretation','host runtime and OS correctness','hash function','external assessment and authority truth'],
           'rechecking':'full; no incremental invalidation or timestamp-based currency'}
    value['dependency_identity']=canonical(value)
    return value


def verify(bound, executed_at=None):
    # An optional operational annotation cannot establish semantic currentness.
    # It is deliberately excluded from the independently recomputed manifest.
    expected=manifest()
    s.require(bound==expected,'dependency manifest stale, incomplete or from another profile')
    return True


def replay(bound):
    verify(bound)
    raw=(s.BASE/'demonstrations/l0/input.json').read_bytes()
    normal=r.d.normalize(r.d.decode(raw));registry=s.read(s.BASE/'registry/normalized-registry.json')
    references=r.resolve(r.from_decoder(raw),registry)
    s.require(references['status']=='supported','baseline reference resolution failed')
    with tempfile.TemporaryDirectory(prefix='deterministic-replay-') as folder:
        build=Path(folder);modules=s.compile_lean(build,r.d.core_modules());evaluation=r.d.check(normal,build)
    semantic={'profile':PROFILE,'normal_form_sha256':evaluation['normal_form_sha256'],
              'accepted_base':evaluation['accepted_base'],'accepted_result':evaluation['accepted_result'],
              'proof_method':evaluation['proof_method'],'axioms':evaluation['axiom_report'],
              'references':references,'dependency_identity':bound['dependency_identity']}
    # Recheck after computation so a changed source cannot inherit this result.
    verify(bound)
    return {'result':semantic,'result_identity':canonical(semantic),'fresh_modules':modules,
            'evaluation_artifacts':{k:evaluation[k] for k in ['query_sha256','evaluation_source_sha256','evaluation_olean_sha256']},
            'authority_effect':'none'}
