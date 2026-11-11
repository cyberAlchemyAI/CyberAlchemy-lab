from pathlib import Path
import json,hashlib,subprocess,re
R=Path('/home/vlad_/projects/CyberAlchemy-lab');O=R/'work/plans/shared-definitions-records';A=R/'work/audits/shared-lab-design/20261110'
def read(p):return json.loads(p.read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(name,x):assert x,name;checks.append(name)
m=read(O/'MANIFEST.json')
for e in m['files']:
 p=O/e['path'];check('original-design-byte-identical:'+e['path'],p.is_file()and digest(p)==e['sha256']and p.stat().st_size==e['bytes'])
findings=read(A/'FINDINGS.json')['findings'];w=read(A/'COUNTEREXAMPLES.json');names={x['name']for x in w['observations']}
check('nine-new-witnesses-reproduced',w['status']=='REPRODUCED'and len(names)==9)
for f in findings:
 for p in f['locations']:
  check('source-anchor:'+f['id']+':'+str(p['line']),(R/p['path']).is_file() and len((R/p['path']).read_text().splitlines())>=p['line'])
 for witness in f['counterexamples']:check('witness-linked:'+witness,witness in names)
selection=read(O/'DEFINITION-SELECTION.json')['bindings'];check('selection46-exceeds-review24',len({e['definition_id']+'@'+e['version'] for e in selection} | {e['version'] for e in read(O/'DEFINITION-SELECTION.json')['pending_definition_targets']})==46 and 'definitions List<DefinitionReview,24>'in (O/'alchlang/contracts.alch').read_text())
for e in selection:check('selected-definition-bytes:'+e['definition_id'],digest(R/e['path'])==e['sha256'])
for e in read(A/'DEFINITION-CONTRACT-COVERAGE.json')['existing_definitions_to_reuse_or_assess']:
 b=e['source'];check('reusable-definition:'+e['definition_id'],digest(R/b['path'])==b['sha256'])
for e in read(A/'INDEX.json').values():
 if isinstance(e,str)and e.endswith(('.json','.md','.mjs'))and e!='AUDIT-VERIFICATION.json':check('audit-index:'+e,(A/e).is_file())
check('ten-findings-six-P1-four-P2',len(findings)==10 and sum(f['priority']=='P1'for f in findings)==6)
check('no-tracked-source-or-staged-change',subprocess.check_output(['git','diff','HEAD','--name-only'],cwd=R,text=True)=='')
check('original-source-fingerprint',w['source']==read(O/'DESIGN-VERIFICATION.json')['source'])
receipt={'status':'PASS','design_verdict':'CHANGES-REQUIRED','scope':'Audit evidence integrity and read-only design/source checks, not design correctness or production qualification','checks':checks,'check_count':len(checks),'original_design_files_unchanged':len(m['files']),'reproduced_counterexamples':len(names),'findings':len(findings),'canonical_definitions_updated':0,'runtime_implementation_changed':False,'actual_owner_responses_recorded':0}
(A/'AUDIT-VERIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n')
files=[p for p in A.iterdir()if p.is_file()and p.name!='MANIFEST.json']
(A/'MANIFEST.json').write_text(json.dumps({'scope':'Own audit package; this manifest excluded','files':[{'path':p.name,'sha256':digest(p),'bytes':p.stat().st_size}for p in sorted(files)]},indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items()if k!='checks'}))
