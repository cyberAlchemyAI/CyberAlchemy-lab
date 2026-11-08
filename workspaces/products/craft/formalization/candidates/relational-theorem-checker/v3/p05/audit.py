"""Strict current-source closure with typed, nonqualifying documentary records."""
from dataclasses import dataclass,field
from pathlib import Path
import json
import sys
sys.dont_write_bytecode=True
from bindings import BASE,ROOT,Resolver,require,repo,legacy,plain,digest

V1=BASE.parent/'v1';V2=BASE.parent/'v2'
SCOPE=V2/'s10/scoped-provenance.json'
SCOPE_PIN={'kind':'repo','path':str(SCOPE.relative_to(ROOT)),'sha256':'ce05f885582122c3e322ac85058ef1b45cf863206a6a5e237295aa83679d6657'}
ORIGINAL_STDLIB={V1/'formal/proofs/l0/statement-and-axiom-audit.json',V1/'relation-stress/v1/implementation/audit.json'}


@dataclass(frozen=True)
class AuditPolicy:
    required_roots: tuple
    input_leaves: tuple=()
    documentary: tuple=()
    permitted_legacy_scope_binding: dict=field(default_factory=lambda:dict(SCOPE_PIN))


def audit_closure(inputs,policy):
    require(policy.permitted_legacy_scope_binding==SCOPE_PIN,'legacy exception policy substitution')
    resolver=Resolver();resolver.check(policy.permitted_legacy_scope_binding)
    scope=json.loads(SCOPE.read_text())['entries'];require(len(scope)==24,'legacy scope count drift')
    required=list(policy.required_roots)
    require(all(x.get('kind') in ['repo','toolchain'] for x in required),'required roots must be authoritative')
    authoritative=[x for x in inputs if x.get('kind')!='documentary']
    require(authoritative==required,'required authoritative root inventory was shrunk/relabelled/reordered')
    pending=list(inputs);verified={};active=set();seen=set();documents=[];captured=[];toolchain_copies=[];external=[];cycles=[]
    leaves={json.dumps(x,sort_keys=True) for x in policy.input_leaves}
    def visit(ref):
        if ref.get('kind')=='documentary':
            documents.append(resolver.documentary(ref,policy.documentary));return
        path=resolver.locate(ref)
        if str(path) in active:
            cycles.append(str(path));raise ValueError('cyclic artifact reference '+str(path))
        path=resolver.check(ref);key=(str(path),ref['sha256'])
        verified[json.dumps(ref,sort_keys=True)]=ref
        if key in seen:return
        seen.add(key)
        if path.suffix!='.json':return
        if json.dumps(ref,sort_keys=True) in leaves:
            external.append(ref);return
        # External governance objects are exact-byte source inputs, not imports
        # of their historical authority graph. This boundary is repository-owned.
        if not any(path.is_relative_to(p) for p in [V1,V2,BASE]):
            external.append(ref);return
        active.add(str(path))
        try:scan(json.loads(path.read_text()),path,())
        finally:active.remove(str(path))

    def historical(entry,origin,selector):
        exact=next((x for x in scope if x['origin']==str(origin.relative_to(ROOT)) and x['selector']==list(selector) and x['captured_path']==entry['path'] and x['captured_sha256']==entry['sha256']),None)
        if exact is None:return False
        require(digest(origin)==exact['origin_sha256'],'changed legacy exception origin')
        require(not (entry['path'].endswith('.lean') or entry['path'].endswith('.olean')),'proof exception forbidden')
        captured.append({**exact,'qualification_dependency':False});return True

    def scan(value,origin,selector):
        if isinstance(value,list):
            for i,x in enumerate(value):scan(x,origin,selector+(i,))
            return
        if not isinstance(value,dict):return
        if value.get('kind')=='documentary':
            visit(value);return
        if value.get('schema')=='relational.provenance-report/v3':
            from jsonschema import Draft202012Validator
            schema=json.loads((BASE/'p05/audit-report.schema.json').read_text())
            Draft202012Validator(schema).validate(value)
            require(value['authority_effect']=='none' and value['result']=='pass','invalid captured audit report')
            require(value['policy']['legacy_scope_binding']==SCOPE_PIN and not value['policy']['proof_exceptions'],'captured report expands legacy scope')
            require(all(ref in value['verified_bindings'] for ref in value['policy']['required_roots']),'captured report dropped a required root')
            for item in value['captured_legacy_metadata']:
                require({k:v for k,v in item.items() if k!='qualification_dependency'} in scope,'unscoped captured legacy metadata')
                require(digest(ROOT/item['origin'])==item['origin_sha256'],'changed captured legacy origin')
            for item in value['toolchain_documentary_copies']:
                expected=resolver.toolchain(item['original_toolchain_path'],item['recorded_digest'])
                require(item['verified_binding']==expected,'captured toolchain copy mismatch')
            # Authoritative entries remain checked on report reread; documentary
            # entries are explicitly authorized, never substitutes for roots.
            for ref in value['verified_bindings']:visit(ref)
            for doc in value['documentary_entries']:
                original=next((x for x in policy.documentary if x['id']==doc['id'] and x['capture']==doc['capture']),None)
                require(original is not None,'unauthorized documentary report entry')
                visit(original)
            return
        if 'toolchain_relative_bindings' in value:
            for item in value['toolchain_relative_bindings']:
                original,resolved=item['original'],item['resolved']
                ref=resolver.toolchain(original['path'],original['sha256'])
                canonical=plain(repo(resolver.locate(ref)))
                require(resolved==canonical,'original/resolved toolchain copy mismatch')
                toolchain_copies.append({'original_toolchain_path':original['path'],'recorded_digest':original['sha256'],'verified_binding':ref})
            value={k:v for k,v in value.items() if k!='toolchain_relative_bindings'}
        if value.get('kind') in ['repo','toolchain']:
            visit(value);return
        # JSON Schema property maps also contain keys named path and sha256;
        # their values are schemas, not artifact references.
        if set(value)>={'path','sha256'} and isinstance(value['path'],str) and isinstance(value['sha256'],str):
            if historical(value,origin,selector):return
            if value.get('kind') in ['repo','toolchain']:
                visit(value);return
            if value['path'].startswith('lib/lean/'):
                require(origin in ORIGINAL_STDLIB and selector[0]=='standard_library_imports','unscoped relative toolchain binding')
                visit(resolver.toolchain(value['path'],value['sha256']));return
            visit(legacy(value))
            # Additional context annotations can themselves carry dependencies.
            for k,v in value.items():
                if k not in ['path','sha256']:scan(v,origin,selector+(k,))
            return
        for k,v in value.items():scan(v,origin,selector+(k,))

    for ref in pending:visit(ref)
    return {'schema':'relational.provenance-report/v3','result':'pass','verified_bindings':list(verified.values()),'documentary_entries':documents,'captured_legacy_metadata':captured,'toolchain_documentary_copies':toolchain_copies,'external_input_leaves':external,'policy':{'required_roots':required,'legacy_scope_binding':policy.permitted_legacy_scope_binding,'proof_exceptions':[]},'counts':{'distinct_artifacts':len(seen),'hashes':resolver.hashes,'memo_hits':resolver.hits,'legacy_metadata_occurrences':len(captured)},'failures':[],'claim_ceiling':'Exact current byte bindings and selected source closure; no authenticated issuer truth or historical governance graph proof.','authority_effect':'none'}
