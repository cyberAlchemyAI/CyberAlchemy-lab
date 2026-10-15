"""Owned prototype selection updater; independently pinned edition only."""
import argparse,hashlib,json,re,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[6]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def exact(row):
 if type(row) is not dict or set(row)!={'path','sha256'}:raise ValueError('closed independent binding required')
 rel=Path(row['path'])
 if rel.is_absolute() or rel.as_posix()!=row['path'] or '..' in rel.parts:raise ValueError('canonical selected origin required')
 path=ROOT/rel
 if not path.is_file() or path.is_symlink() or any(p.is_symlink() for p in path.parents):raise ValueError('regular selected input required')
 raw=path.read_bytes()
 if sha(raw)!=row['sha256']:raise ValueError('explicit selected bytes changed')
 return raw
def write(path,raw):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('xb') as f:f.write(raw)
def main():
 p=argparse.ArgumentParser();p.add_argument('--packet',required=True);p.add_argument('--packet-sha256',required=True);a=p.parse_args()
 packet=json.loads(exact({'path':a.packet,'sha256':a.packet_sha256}))
 fields={'schema_version','authority_effect','edition_id','standing','narrative_binding','source_map_binding','review_binding','owner_manifest_binding','owner_handoff_binding','expected_review_result','page_count','section_count','public_source_count','final_publication_qualified'}
 if set(packet)!=fields or packet['schema_version']!='lab-T21-reviewed-runtime-documentation-inputs/v1-candidate' or packet['authority_effect']!='none' or re.fullmatch('[a-z0-9-]+',packet['edition_id']) is None:raise ValueError('closed reviewed Root input packet required')
 inputs={key:exact(packet[key]) for key in ['narrative_binding','source_map_binding','review_binding','owner_manifest_binding','owner_handoff_binding']}
 narrative=json.loads(inputs['narrative_binding']);sources=json.loads(inputs['source_map_binding']);review=json.loads(inputs['review_binding'])
 if review['result']!=packet['expected_review_result'] or not review['result'].startswith('PASS') or review['bindings']['narrative.json']!=packet['narrative_binding']['sha256'] or review['bindings']['source-map.json']!=packet['source_map_binding']['sha256']:raise ValueError('exact narrative/source-map review required')
 if len(narrative['pages'])!=packet['page_count'] or sum(len(p['sections']) for p in narrative['pages'])!=packet['section_count'] or len(sources['source_bindings'])!=packet['public_source_count']:raise ValueError('complete reviewed prose/evidence required')
 rows=[]
 for row in sources['source_bindings'].values():
  raw=exact({'path':row['snapshot_path'],'sha256':row['sha256']})
  if len(raw)!=row['size_bytes']:raise ValueError('complete public input required')
  original=Path(row['original_path'])
  if original.is_absolute() or '..' in original.parts or original.as_posix()!=row['original_path']:raise ValueError('public evidence route escape')
  rows.append((row,raw))
 proto=HERE/'prototype';web=proto/'website';lab=web/'source/governance-lab-series';runtime=lab/'runtime'
 if proto.is_symlink() or not proto.is_dir() or any(p.is_symlink() for p in proto.parents):raise ValueError('owned actual prototype required')
 archive=HERE/'diagnostic-generation-0001'
 if archive.exists():raise ValueError('initial generation archive already exists')
 archive.mkdir()
 for path,target in [(web/'dist',archive/'site'),(web/'artifacts',archive/'artifacts'),(web/'.build/logs',archive/'logs'),(proto/'docs/lab',archive/'markdown')]:
  if path.exists():path.replace(target)
 retained=archive/'runtime-inputs';retained.mkdir()
 for name in ['selection.json','narrative.json','source-map.json','independent-review-0001.json']:shutil.copy2(runtime/name,retained/name)
 prefix='research/sources/runtime/'+packet['edition_id']+'/'
 for row,raw in rows:write(lab/prefix/row['original_path'],raw)
 for key,name in [('narrative_binding','narrative.json'),('source_map_binding','source-map.json'),('review_binding','independent-review-0001.json'),('owner_manifest_binding','owner-manifest.json'),('owner_handoff_binding','owner-handoff.json')]:
  (runtime/name).write_bytes(inputs[key])
 selection={key:packet[key] for key in ['edition_id','standing','expected_review_result','page_count','section_count','final_publication_qualified']};selection.update(schema_version='lab-runtime-documentation-selection/v1-candidate',authority_effect='none',evidence_prefix=prefix)
 for key,name in [('narrative_binding','narrative.json'),('source_map_binding','source-map.json'),('review_binding','independent-review-0001.json')]:selection[key]={'path':name,'sha256':packet[key]['sha256']}
 raw=(json.dumps(selection,sort_keys=True,indent=2)+'\n').encode();(runtime/'selection.json').write_bytes(raw)
 config=json.loads((web/'site.json').read_text());config['runtime_documentation_selection']={'path':'source/governance-lab-series/runtime/selection.json','sha256':sha(raw)};(web/'site.json').write_text(json.dumps(config,sort_keys=True,indent=2)+'\n')
 sys.path.insert(0,str(lab));from runtime.body import Renderer;from build_site_search import Document
 corpus=json.loads((web/'editorial-copy.json').read_text());corpus['entries']=[entry for entry in corpus['entries'] if not entry['page'].startswith('governance-lab-series/runtime-')]
 renderer=Renderer(narrative,sources,prefix)
 for page in narrative['pages']:
  for paragraph in Document(renderer.body(page,'fragment',lab)).root.all(lambda n:n.tag=='p'):
   text=' '.join(paragraph.text().split())
   if text:corpus['entries'].append({'page':'governance-lab-series/'+page['site_file'],'original':text,'editorial':text,'review_basis':'Exact independently reviewed '+packet['edition_id']+' narrative owner; no paraphrase of formal/code bodies.'})
 (web/'editorial-copy.json').write_text(json.dumps(corpus,ensure_ascii=False,indent=2)+'\n')
 maintenance=proto/'docs/lab/MAINTENANCE.md';maintenance.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(HERE/'postimages/docs/lab/MAINTENANCE.md',maintenance)
 (HERE/'doc2-stage-receipt.json').write_text(json.dumps({'schema_version':'lab-T21-owned-review-input-staging/v1-candidate','authority_effect':'none','packet_binding':{'path':a.packet,'sha256':a.packet_sha256},'selector_sha256':sha(raw),'edition_id':packet['edition_id'],'pages':packet['page_count'],'sections':packet['section_count'],'public_source_files':len(rows),'prior_diagnostic_generation_retained':True,'shared_mutation_or_runtime_execution':False},sort_keys=True,indent=2)+'\n')
 print(json.dumps({'result':'STAGED-exact-reviewed-runtime-doc2-inputs','selector_sha256':sha(raw),'public_sources':len(rows),'shared_mutation':False}))
if __name__=='__main__':main()
