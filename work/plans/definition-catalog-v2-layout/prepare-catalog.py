from pathlib import Path
import json,hashlib,copy,re
import jsonschema
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
def raw(v):return (json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw(v))
def bind(p,name=None):return dict(path=name or str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size,digest_kind='original-file-sha256')
baseline=json.loads((P/'BASELINE.json').read_text());assert json.loads((R/'authority/definitions/current.json').read_text())==baseline['selection'],'canonical-selection-changed: prepare a new reviewed rollout'
reg=json.loads((R/'authority/admissions/shared-definitions-records-0076/registry.json').read_text())
template=json.loads((P/'REQUEST-TEMPLATE.json').read_text())
schema=R/'authority/artifact-types/definition/v2/schema.json';generator=R/'authority/artifact-types/definition/v2/generator.py'
v=jsonschema.Draft202012Validator(json.loads(schema.read_text()))
selected=[e for e in reg['entries'] if reg['current_lookup'].get(e['definition_id'])==e['definition_id']+'@'+e['version']]
def home(did):
 if did=='CAV2-D20' or did.startswith('craft.definition.'):return 'workspaces/products/craft'
 if did in ['cal.definition.definition-pack','cal.definition.cyberalchemy-define']:return 'workspaces/products/define'
 if did in ['cal.definition.person','cal.definition.person-reference','cal.definition.team','cal.definition.team-membership']:return 'workspaces/products/people-and-teams'
 if did in ['cal.definition.ontology','cal.definition.ontology-cut','cal.definition.ontology-node','cal.definition.ontology-edge','cal.definition.ontology-manifest','cal.definition.ontology-view']:return 'workspaces/products/ontology'
 return '.'
def leaves(value,p=''):
 if isinstance(value,dict) and value:
  for k,x in value.items():yield from leaves(x,p+'/'+k.replace('~','~0').replace('/','~1'))
 elif isinstance(value,list) and value:
  for i,x in enumerate(value):yield from leaves(x,p+'/'+str(i))
 else:yield p,value
rows=[]
for e in selected:
 did=e['definition_id'];assert re.fullmatch(r'[A-Za-z0-9._-]+',did)
 original=R/e['body']['path'];source=json.loads(original.read_text());assert bind(original)['sha256']==e['body']['sha256']
 d=copy.deepcopy(source);converted=d['schema_version'].endswith('/v1')
 if converted:
  match=re.fullmatch(r'(.+)-candidate\.(\d+)',d['version']);assert match
  taken={x['version'] for x in reg['entries'] if x['definition_id']==did};n=int(match[2])+1
  while match[1]+'-candidate.'+str(n) in taken:n+=1
  d['version']=match[1]+'-candidate.'+str(n)
  d['schema_version']='cyberalchemy-lab-definition/v2'
  d['classification']['artifact_type_ref']='cal.artifact-type.definition/v2'
  d['schema_ref']='cal.schema.definition/v2';d['schema_digest']=bind(schema)['sha256']
  d['source_direction']['generator_ref']='cal.generator.definition-markdown/v2'
  d['source_direction']['generator_sha256']=bind(generator)['sha256']
  oldref=did+'@'+source['version'];newref=did+'@'+d['version']
  d['source_refs'].append(dict(source_ref=oldref,selector='whole-json',content_sha256=e['body']['sha256'],admission_posture='admitted',source_admission_ref=e['owner_disposition']['path']))
 assert d['voices']==source['voices'] and d['scope']==source['scope'] and d['boundaries']==source['boundaries']
 v.validate(d)
 work=P/'.local'/did;work.mkdir(parents=True,exist_ok=True)
 draft=work/'definition.json'
 if converted:put(draft,d)
 else:draft.write_bytes(original.read_bytes())
 oldbinding=bind(original,'original.json');draftbinding=bind(draft,'definition.json')
 # A separate, attributable metadata transformation is the source for changed leaves.
 oldleaves=dict(leaves(source))
 changed={selector:value for selector,value in leaves(d) if selector not in oldleaves or oldleaves[selector]!=value}
 transformation={'values':changed,'author':'agent:codex','authority_effect':'none','reason':'User-requested v2 representation and workspace placement; unchanged normative and explanatory voices; exact owner review remains separate.'}
 tf=work/'transformation.json';put(tf,transformation);tb=bind(tf,'transformation.json')
 oldleaves=dict(leaves(source));fields=[]
 for selector,value in leaves(d):
  preserved=selector in oldleaves and oldleaves[selector]==value
  fields.append(dict(target_selector=selector,source_binding=oldbinding if preserved else tb,source_selector=selector if preserved else '/values/'+selector.replace('~','~0').replace('/','~1')))
 lf=work/'field-lineage.json';put(lf,dict(schema_version='cal.define.field-lineage/v1',authored_by='agent:codex',authority_effect='none',claim_ceiling='Exact field custody and representation conversion; no owner acceptance.',fields=fields))
 request=copy.deepcopy(template);request.update(request_id='catalog-v2-'+did,goal='Generate the complete current Definition catalog in Definition/v2 and owning-workspace layout',originating_intent='Use the full agreed content and folder structure',context='Exact admitted original selected by the current shared registry; representation-only successor preparation, not semantic admission.',consumer='lab:shared-runtime',intended_use='materialize-candidate')
 concept=did
 request['required_concepts']=[dict(concept_id=concept,question='How is '+source['term']+' represented in the complete v2 contract?',scope=d['scope']['applicability'])]
 meaning=dict(meaning_id='working:'+did,revision=1,statement=d['voices']['scientific_formal']['normative_statement'],scope=d['scope']['applicability'],boundaries=d['boundaries'],parameters=[dict(name=x['symbol'],value_schema={'type':'string'},required=False,interpretation=x['meaning'])for x in d['voices']['scientific_formal']['notation']],ownership_posture='Exact existing semantic owner retained; new representation requires exact review, not inferred admission.',lineage=[oldbinding,draftbinding],status='local-proposed',authority_effect='none')
 request['handling']=[dict(concept_id=concept,disposition='propose',payload=dict(working_meaning=meaning,applicability=d['scope']['applicability']))]
 meaning_hash=hashlib.sha256(raw(meaning)).hexdigest()
 mr=dict(kind='embedded',pack_id=request['request_id'],pack_revision=1,entry_kind='working-meaning',entry_id=meaning['meaning_id'],revision=1,selector='/working_meanings/0',sha256=meaning_hash)
 parent=dict(kind='external',input_id='original.json',identity=did,revision=source['version'],carrier_ref=source['classification']['artifact_type_ref'],selector='',sha256=hashlib.sha256(raw(source)).hexdigest())
 request['source_bindings']=[oldbinding,draftbinding,tb,bind(lf,'field-lineage.json')]
 request['materialization_selection']=[dict(meaning_ref=mr,definition_binding=draftbinding,field_lineage_binding=bind(lf,'field-lineage.json'),authority_scope=d['scope']['authority_scope_ref'],owner_route=d['semantic_owner_ref'],identity_intention='successor' if converted else 'new-identity',parent_ref=parent if converted else None,purpose='Exact representation-only conversion and complete v2 placement' if converted else 'Byte-exact placement of already admitted v2 body; no new identity/admission')]
 request['validation_scope']=dict(required_checks=['Full Definition/v2','Exact original voice preservation','Complete field lineage','Deterministic original projection','Owning workspace versioned layout'],evidence_scope='Selected current catalog; no archived noncurrent rollout',claim_ceiling='Candidate representation and technical verification; no new semantic owner decision or publication authority.')
 put(work/'request.json',request)
 # Original input retained once by path reference and copied only into disposable capture.
 (work/'original.json').write_bytes(original.read_bytes())
 row=dict(definition_id=did,term=d['term'],source=e,workspace_home=home(did),version=d['version'],converted=converted,folder_name=re.sub('[^a-z0-9]+','-',d['term'].lower()).strip('-'),target=str(Path(home(did))/'authority/definitions'/re.sub('[^a-z0-9]+','-',d['term'].lower()).strip('-')/d['version']),work=str(work.relative_to(R)),candidate_binding=bind(draft))
 rows.append(row)
put(P/'MAPPING.json',dict(status='prepared',current=188,converted=sum(x['converted']for x in rows),already_v2=sum(not x['converted']for x in rows),ownership_rule='Maintenance placement only; semantic owner/scope unchanged. Product-specific Craft, Define, Person/Team and Ontology families use their product home; shared vocabulary remains Lab-owned.',entries=rows))
print(json.dumps({'current':len(rows),'converted':sum(x['converted']for x in rows),'workspaces':sorted(set(x['workspace_home']for x in rows))}))
