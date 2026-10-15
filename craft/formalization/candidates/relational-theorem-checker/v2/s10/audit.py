"""Exact recursive binding audit and policy checks for qualified evidence/build reuse."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'execution'));import support as s

def binding_closure(paths):
 pending=[Path(p).resolve() for p in paths];seen={};bindings={};toolchain_bindings=[];toolchain_root=None;captured=[];external_leaves=[]
 scope_file=Path(__file__).resolve().parent/'scoped-provenance.json'
 scopes=s.read(scope_file)['entries']
 def scan(x,origin,selector=()):
  nonlocal toolchain_root
  if isinstance(x,dict):
   if isinstance(x.get('path'),str) and isinstance(x.get('sha256'),str) and len(x['sha256'])==64:
    scoped=next((z for z in scopes if z['origin']==str(origin.relative_to(s.ROOT)) and z['selector']==list(selector) and z['captured_path']==x['path'] and z['captured_sha256']==x['sha256']),None)
    if scoped:
     s.require(s.digest(origin)==scoped['origin_sha256'],'historical metadata origin changed')
     cls=scoped['classification'];v1=str(s.V1.relative_to(s.ROOT))+'/'
     permitted=(cls=='historical-temporary-shadow-state' and str(origin.relative_to(s.ROOT)).startswith(v1+'workflow/application-adapter/') and x['path'].startswith(v1+'workflow/application-adapter/shadow/controlled-lt65489q/')) or (cls=='intentional-hostile-input' and origin in [s.V1/'workflow/cli/cases/stale-proof.json',s.V1/'workflow/cli/cases/stale-bundle.json'] and x['sha256']=='0'*64) or (cls=='historical-task-context-plan' and origin in [s.V1/'workflow/evidence/context-pack.json',s.V1/'workflow/proof-verifier/context-pack.json'] and selector[0]=='sources' and x['path']=='docs/plans/relational-theorem-checker/PLAN-SOURCE.json') or (cls=='dynamic-navigation-link' and origin==s.BASE/'s08/docs-audit.json' and selector[0]=='links' and x['path'] in [str((s.BASE/'execution/status.json').relative_to(s.ROOT)),str(s.PLAN.relative_to(s.ROOT))])
     s.require(permitted,'forbidden proof binding exclusion');target=s.ROOT/x['path']
     if cls=='dynamic-navigation-link':s.require(target.is_file(),'missing current navigation target')
     captured.append({**scoped,'current_file_exists':target.is_file(),'observed_sha256':s.digest(target) if target.is_file() else None,'proof_discharge':False});return
    b=x
    if x['path'].startswith('lib/lean/'):
     s.require(origin in [s.V1/'formal/proofs/l0/statement-and-axiom-audit.json',s.V1/'relation-stress/v1/implementation/audit.json'] and selector[0]=='standard_library_imports','unscoped toolchain-relative binding '+str(origin)+' '+str(selector))
     relative=Path(x['path']);s.require('..' not in relative.parts,'unsafe toolchain-relative binding')
     if toolchain_root is None:toolchain_root=s.lean_path().parent.parent
     p=toolchain_root/relative;b={'path':str(p.relative_to(s.ROOT)),'sha256':x['sha256']};toolchain_bindings.append({'original':x,'resolved':b})
    p=s.check(b);key=b['path'];s.require(key not in bindings or bindings[key]==b['sha256'],'conflicting source bindings '+key);bindings[key]=b['sha256'];pending.append(p.resolve())
   for k,v in x.items():scan(v,origin,selector+(k,))
  elif isinstance(x,list):
   for i,v in enumerate(x):scan(v,origin,selector+(i,))
 while pending:
  p=pending.pop()
  if p in seen:continue
  seen[p]=s.binding(p)
  if p.suffix=='.json':
   if p.is_relative_to(s.V1) or p.is_relative_to(s.BASE):scan(s.read(p),p)
   else:external_leaves.append(s.binding(p))
 return {'bindings':list(seen.values()),'distinct_artifacts':len(seen),'distinct_embedded_bindings':len(bindings),'scoped_provenance_policy':s.binding(scope_file),'captured_nonqualification_metadata':captured,'external_source_leaves':external_leaves,'scope':'Recursively verify theorem-checker proof/source/receipt bindings. External source documents are exact-byte input leaves; their historical governance graphs are not qualification imports. Only the enumerated immutable historical contexts, hostile fixtures, temporary shadow captures and dynamic navigation links are nonqualification metadata. No proof module/evidence exclusions are permitted.','toolchain_relative_bindings':toolchain_bindings,'toolchain_resolution':'Only the original bound F0 statement and stress audits standard_library_imports entries resolve relative to the pinned compiler root; every hash is checked, including official private/server parts.','result':'pass'}

def build_policy(build):
 build=Path(build);mods=list(build.glob('*.olean'))
 for p in mods:
  # Core-only generated builds must not have unbound private/server module parts.
  for suffix in ['.olean.private','.olean.server']:
   s.require(not p.with_suffix(suffix).exists(),'unbound auxiliary Lean module part '+str(p.with_suffix(suffix)))
  src=p.with_suffix('.lean');s.require(src.is_file(),'object lacks source '+str(p))
 return {'result':'pass','module_count':len(mods),'auxiliary_parts':'absent; introduced unbound parts rejected'}
