"""Static input closure for frozen trusted caller0004, without invoking Source."""
import argparse,ast,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
CHECKOUT=HERE.parents[3]
API='product/lab/release-candidates/v1/interface/api-integration-v75-current-fixtures-0001'
CALLER=CHECKOUT/'implementation/lab-runtime/local-host/t03-installed-learning-caller-0004'
TEMPLATES={
 'authority/artifact-types/lesson-application/v1/fixtures/valid/record.json':'711d72999a4ca5a7abff8ba938d50387020583214c668de2859c056a157b9b12',
 'authority/artifact-types/lesson-outcome-assessment/v1/fixtures/valid/record.json':'fb14ca2e2ba2ed75b5c742318e8233b49b0458fe305c96b6645c77fc02e6e9bc'}
EPISODE={
 'product/lab/release-candidates/v1/interface/api-integration-v30/source-manifest.json':'cfd9a932d87c565c22b915234bbf2a18bfed23f163607b95b96f24b2533e3a16',
 'authority/project-state-transitions/current.json':'12937950af2a00ef329deb1a922275250c61ad199b8f6216eab448e06bf49984',
 'authority/admissions/lab-specialist-owner-bootstrap-v1-0003/instances/project-state.json':'cccf18d2966cf0dd494f7d88b054243bb635a91bc84fdcbf5c70709b7b6f8793',
 'authority/admissions/lab-specialist-owner-bootstrap-v1-0003/bundle.json':'8eb940493460ea2c10f50f677d5cbfbd5b898625868af036fb0e594ec9b1b220'}
sha=lambda b:hashlib.sha256(b).hexdigest()
def need(v,m):
 if not v:raise ValueError(m)
def audit(root,allow_missing_templates=False):
 root=Path(root);need(root.is_absolute()and root.is_dir()and not any(p.is_symlink()for p in(root,*root.parents)),'exact selected root required')
 def read(name):
  p=root/name;need(not any(x.is_symlink()for x in(p,*p.parents)),'linked selected dependency');return p.read_bytes()
 manifest=json.loads(read(API+'/source-manifest.json'));checked=[]
 for row in manifest['files']:
  need(sha(read(row['path']))==row['sha256'],'selected API dependency differs: '+row['path']);checked.append(row)
 direct={};caller_files=[]
 for p in sorted(CALLER.glob('*.py')):
  if p.name.startswith('test_'):continue
  caller_files.append({'path':str(p.relative_to(CHECKOUT)),'sha256':sha(p.read_bytes())})
  for node in ast.walk(ast.parse(p.read_bytes())):
   if isinstance(node,ast.Constant)and isinstance(node.value,str)and node.value.startswith(('authority/','product/','docs/','implementation/')):
    direct.setdefault(node.value,[]).append({'caller':p.name,'line':node.lineno})
 missing=[];direct_checked=[]
 for name,sites in sorted(direct.items()):
  if name.endswith('/'):
   need((root/name).is_dir(),'logical data prefix absent');continue
  if name in TEMPLATES and not(root/name).exists():missing.append({'path':name,'sha256':TEMPLATES[name],'read_sites':sites});continue
  raw=read(name);direct_checked.append({'path':name,'sha256':sha(raw),'read_sites':sites})
 need(allow_missing_templates or not missing,'missing trusted caller template inputs')
 for name,pin in EPISODE.items():need(sha(read(name))==pin,'episode transitive input differs: '+name)
 lookup=json.loads(read('authority/project-state-transitions/current.json'))
 need(lookup['admission_bundle']['sha256']==EPISODE[lookup['admission_bundle']['path']],'episode indirect bundle differs')
 software=json.loads((HERE/'margin-software.json').read_bytes())
 selected={r['path']:r['sha256']for r in manifest['files']}
 for row in software['files']:need(selected.get(row['path'])==row['sha256']==sha(read(row['path'])),'successor diagnostic software differs')
 schemas=[]
 for name,pin in TEMPLATES.items():
  schema=name.split('/fixtures/')[0]+'/schema.json';raw=read(schema)
  need(raw==(CHECKOUT/schema).read_bytes(),'template contract differs')
  template=(CHECKOUT/name).read_bytes();need(sha(template)==pin,'template input changed')
  body=json.loads(template);need(body['authority_effect']=='none'and body['lifecycle_state']=='candidate','template implies effects')
  schemas.append({'path':schema,'sha256':sha(raw)})
 return {'schema_version':'lab-trusted-learning-caller-static-input-audit/v1','result':'PASS-static-closure-with-exact-two-missing-templates'if missing else'PASS-static-learning-input-closure','authority_effect':'none','selected_root':str(root),'API_source_sha256':sha(read(API+'/source-manifest.json')),'checked_API_dependency_count':len(checked),'caller_bindings':caller_files,'direct_inputs':direct_checked,'missing_inputs':missing,'episode_indirect_inputs':EPISODE,'candidate_template_contracts':schemas,'successor_software_sha256':sha((HERE/'margin-software.json').read_bytes()),'dynamic_inputs':'Actual Source, policy, live private Vault, journals and actual Session originals are generated/checked by frozen caller and selected API at runtime; they are not static fixture prerequisites.','execution_proven':False,'scope':'All eight frozen caller runtime modules; their exact static repository literals; all selected API dependencies (including method/schema modules); four separately pinned episode inputs including indirect bundle; both candidate template contracts; all17 successor software entries. Historical unused API routes are outside this learning path.'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--allow-missing-templates',action='store_true');p.add_argument('--output',required=True);a=p.parse_args();result=audit(a.root,a.allow_missing_templates);Path(a.output).write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps({'result':result['result'],'missing':result['missing_inputs'],'sha256':sha(Path(a.output).read_bytes())}))
