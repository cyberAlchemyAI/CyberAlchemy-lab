"""Actual legacy/source/report round trips and hostile provenance boundaries."""
from pathlib import Path
import copy
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
import audit
import bindings as b
sys.path.insert(0,str(HERE.parent/'execution'))
import support as s
from jsonschema import Draft202012Validator

controls=[]
def positive(name,fn):
    result=fn();controls.append({'name':name,'result':'pass','expected':'accepted'});return result
def negative(name,fn):
    try:fn()
    except Exception as e:controls.append({'name':name,'result':'pass','expected':'rejected','reason':str(e).splitlines()[0]});return
    raise AssertionError('unexpected acceptance '+name)

scalar={'type':'string','minLength':1};sha={'type':'string','pattern':'^[0-9a-f]{64}$'}
def obj(props):return {'type':'object','properties':props,'required':list(props),'additionalProperties':False}
def arr(item,**kw):return {'type':'array','items':item,**kw}
binding=s.read(HERE.parent/'p01/contracts/binding.schema.json');binding.pop('$schema');binding.pop('$id')
doc=obj({'id':scalar,'description':scalar,'capture':binding,'qualification_dependency':{'const':False}})
legacy=obj({'origin':scalar,'origin_sha256':sha,'selector':arr({'type':['string','integer']}),'captured_path':scalar,'captured_sha256':sha,'classification':scalar,'disposition':scalar,'qualification_dependency':{'const':False}})
schema={'$schema':'https://json-schema.org/draft/2020-12/schema',**obj({'schema':{'const':'relational.provenance-report/v3'},'result':{'const':'pass'},'verified_bindings':arr(binding),'documentary_entries':arr(doc),'captured_legacy_metadata':arr(legacy),'toolchain_documentary_copies':arr(obj({'original_toolchain_path':scalar,'recorded_digest':sha,'verified_binding':binding})),'external_input_leaves':arr(binding),'policy':obj({'required_roots':arr(binding),'legacy_scope_binding':binding,'proof_exceptions':arr(binding,maxItems=0)}),'counts':obj({k:{'type':'integer','minimum':0} for k in ['distinct_artifacts','hashes','memo_hits','legacy_metadata_occurrences']}),'failures':arr(obj({'reason':scalar}),maxItems=0),'claim_ceiling':scalar,'authority_effect':{'const':'none'}})}
s.write(HERE/'audit-report.schema.json',schema);Draft202012Validator.check_schema(schema)

root=b.repo(s.V2/'s10/qualification-audit.json')
policy=audit.AuditPolicy((root,))
report=positive('full-inherited-audit-closure',lambda:audit.audit_closure([root],policy))
Draft202012Validator(schema).validate(report)
s.write(HERE/'current-source-report.json',report)
print('Current inherited source/proof closure audited: '+str(report['counts']),flush=True)
report_ref=b.repo(HERE/'current-source-report.json')
roundtrip=positive('serialized-report-reread',lambda:audit.audit_closure([report_ref],audit.AuditPolicy((report_ref,))))
s.write(HERE/'roundtrip-report.json',roundtrip)
Draft202012Validator(schema).validate(roundtrip)
roots=b.repo(s.BASE/'p02/EvidenceControls.lean') if (s.BASE/'p02/EvidenceControls.lean').exists() else b.repo(s.BASE/'p00/EvidenceControls.lean')
negative('missing-proof-binding-hard-failure',lambda:audit.audit_closure([{**roots,'path':str((HERE/'missing-proof.lean').relative_to(s.ROOT))}],audit.AuditPolicy(({**roots,'path':str((HERE/'missing-proof.lean').relative_to(s.ROOT))},))))
negative('alternate-toolchain-root',lambda:b.Resolver(HERE))
resolver=b.Resolver();library='lib/lean/Init.olean';library_sha=b.digest(resolver.compiler_root/library)
tool=resolver.toolchain(library,library_sha)
positive('pinned-toolchain-binding',lambda:resolver.check(tool))
negative('toolchain-identity-substitution',lambda:resolver.check({**tool,'toolchain_identity':'0'*64}))
negative('toolchain-path-traversal',lambda:resolver.check({**tool,'path':'lib/lean/../../outside'}))
negative('relative-original-resolved-hash-mismatch',lambda:audit.audit_closure([{**root,'sha256':'0'*64}],audit.AuditPolicy(({**root,'sha256':'0'*64},))))
for path in ['../outside','/absolute','a/../outside','C:\\outside']:
    negative('reject-unsafe-path-'+path,lambda path=path:resolver.check({'kind':'repo','path':path,'sha256':'0'*64}))

scope=s.read(s.V2/'s10/scoped-provenance.json')['entries']
origin_refs=[b.repo(s.ROOT/path) for path in sorted({x['origin'] for x in scope})]
scope_report=positive('complete-exact-legacy-metadata-origin-closure',lambda:audit.audit_closure(origin_refs,audit.AuditPolicy(tuple(origin_refs))))
s.write(HERE/'legacy-scope-report.json',scope_report)
for i,x in enumerate(scope):
    positive('exact-legacy-metadata-scope-'+str(i),lambda x=x:s.require(any(y['selector']==x['selector'] and y['origin']==x['origin'] for y in scope_report['captured_legacy_metadata']),'legacy exception was not explicitly observed'))
negative('legacy-policy-substitution',lambda:audit.audit_closure([root],audit.AuditPolicy((root,),permitted_legacy_scope_binding={**audit.SCOPE_PIN,'sha256':'0'*64})))

history=HERE/'fixtures/history.json';s.write(history,{'schema':'historical-capture-test','old_reference':{'path':str((HERE/'no-longer-existing.json').relative_to(s.ROOT)),'sha256':'0'*64}})
document={'kind':'documentary','id':'historical-example','description':'A byte-bound historical record is not a current qualification dependency.','capture':b.repo(history)}
proof=b.repo(s.BASE/'p00/EvidenceSemantics.lean')
positive('explicit-authorized-documentary-capture',lambda:audit.audit_closure([proof,document],audit.AuditPolicy((proof,),documentary=(document,))))
negative('documentary-cannot-replace-required-proof',lambda:audit.audit_closure([document],audit.AuditPolicy((proof,),documentary=(document,))))
negative('unregistered-documentary-capture',lambda:audit.audit_closure([proof,document],audit.AuditPolicy((proof,))))
cycle=HERE/'fixtures/cycle.json';s.write(cycle,{'self':{'path':str(cycle.relative_to(s.ROOT)),'sha256':'0'*64}});cycle_ref=b.repo(cycle)
negative('artifact-cycle-detected',lambda:audit.audit_closure([cycle_ref],audit.AuditPolicy((cycle_ref,))))
for name,modify in [
    ('serialized-report-unknown-field',lambda v:v.update(unchecked=True)),
    ('serialized-report-dropped-required-root',lambda v:v.update(verified_bindings=[])),
    ('serialized-report-legacy-scope-expansion',lambda v:v['policy'].update(legacy_scope_binding={**audit.SCOPE_PIN,'sha256':'0'*64})),
]:
    changed=copy.deepcopy(report);modify(changed)
    path=HERE/'fixtures'/(name+'.json');s.write(path,changed);ref=b.repo(path)
    negative(name,lambda ref=ref:audit.audit_closure([ref],audit.AuditPolicy((ref,))))
before=resolver.hashes;resolver.check(tool);resolver.check(tool)
positive('canonical-path-digest-memoization',lambda:s.require(resolver.hashes==before and resolver.hits>=2,'memoization failed'))
s.write(HERE/'provenance-controls.json',{'result':'pass','controls':controls,'source_closure':s.binding(HERE/'current-source-report.json'),'roundtrip':s.binding(HERE/'roundtrip-report.json'),'inherited_metadata_policy':s.binding(s.V2/'s10/scoped-provenance.json'),'proof_exceptions':[],'authority_effect':'none'})
s.accept('P05',[
    'The actual inherited proof/source audit and the new serialized report both re-audit successfully through tagged bindings without a process-global reader patch.',
    'Missing/stale authoritative proof artifacts, alternate toolchains, path escape and documentary substitution remain hard failures; current proof roots cannot be replaced by metadata.',
    'External governance records remain exact-byte source leaves; all 24 existing origin/selector/path/hash metadata scopes are retained exactly and observed explicitly, with no new proof exception.'
],controls,extra=[HERE/'run_p05.py',HERE/'current-source-report.json',HERE/'roundtrip-report.json',HERE/'legacy-scope-report.json',history,cycle])
print('P05 accepted')
