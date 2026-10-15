"""Freeze only owned website candidate artifacts; no shared effect."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[6]
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def row(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes()),'size_bytes':p.stat().st_size}
def write(p,value):
 if p.exists():raise ValueError('Frozen destination already exists: '+str(p))
 p.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
# Own generated output inventory authenticates exact prototype and retained diagnostics.
folders=['prototype','diagnostic-generation-0001','counterevidence','.playwright-cli','output/playwright']
artifacts=[]
for name in folders:
 for p in sorted((HERE/name).rglob('*')):
  if not p.is_file() or p.suffix=='.pyc' or '__pycache__' in p.parts:continue
  if p.is_symlink():raise ValueError('Regular owned artifacts only')
  artifacts.append(row(p))
write(HERE/'owned-artifact-inventory.json',{'schema_version':'lab-T21-owned-website-artifact-inventory/v1','authority_effect':'none','files':artifacts,'scope':'Explicit website-only prototype and actual retained generated observations; no private/live/native tree.'})
files=[]
for p in sorted(HERE.iterdir()):
 if p.is_file() and p.name not in ['source-manifest.json','HANDOFF.json']:files.append(row(p))
for folder in ['preimages','postimages','output/playwright']:
 for p in sorted((HERE/folder).rglob('*')):
  if p.is_file() and p.suffix!='.pyc' and '__pycache__' not in p.parts:files.append(row(p))
# Deduplicate only identical true path rows, with no provenance reinterpretation.
unique={r['path']:r for r in files};files=sorted(unique.values(),key=lambda r:r['path'])
packet=json.loads((HERE/'reviewed-doc2-input-packet.json').read_text())
external=[{'key':key,**packet[key]} for key in ['narrative_binding','source_map_binding','review_binding','owner_manifest_binding','owner_handoff_binding']]
for r in external:
 if sha((ROOT/r['path']).read_bytes())!=r['sha256']:raise ValueError('Independently pinned owner input changed')
manifest={'schema_version':'lab-T21-website-integration-source-manifest/v1-candidate','authority_effect':'none','files':files,'external_inputs':external,'rows':len(files),'shared_applied':False,'published':False,'full_T21_complete':False,'artifact_inventory':row(HERE/'owned-artifact-inventory.json')}
write(HERE/'source-manifest.json',manifest)
report=json.loads((HERE/'implementation-report.json').read_text())
handoff={'schema_version':'lab-T21-website-integration-handoff/v1-candidate','authority_effect':'none','result':report['result'],'source_manifest_sha256':sha((HERE/'source-manifest.json').read_bytes()),'source_manifest_rows':len(files),'artifact_inventory_sha256':sha((HERE/'owned-artifact-inventory.json').read_bytes()),'artifact_inventory_rows':len(artifacts),'implementation_report_sha256':sha((HERE/'implementation-report.json').read_bytes()),'postimage_selection_sha256':sha((HERE/'postimage-selection.json').read_bytes()),'reviewed_input_packet_sha256':sha((HERE/'reviewed-doc2-input-packet.json').read_bytes()),'runtime_selector_sha256':report['selector_sha256'],'website_archive_sha256':report['actual_build']['archive_sha256'],'runtime_renderer_sha256':sha((HERE/'postimages/website/source/governance-lab-series/runtime_docs.py').read_bytes()),'runtime_css_sha256':sha((HERE/'postimages/website/source/governance-lab-series/runtime/runtime.css').read_bytes()),'counts':{'runtime_pages':14,'sections':67,'public_resources':74,'site_files':report['actual_build']['files'],'imported_pages':507,'browser_views_passed':28,'pipeline_assertions':4391,'original_deployed_pages':478,'original_pre_blocks':550},'browser_first_failure_and_retry_preserved':True,'markdown_resource_scope':'16 explanatory targets resolve in actual repository;102 inert direct snapshot outbound references unexpanded; no full recursive closure claim.','shared_applied':False,'published':False,'runtime_executed':False,'full_T21_complete':False,'remaining':report['remaining']}
write(HERE/'HANDOFF.json',handoff)
print(json.dumps({'handoff_sha256':sha((HERE/'HANDOFF.json').read_bytes()),**handoff},sort_keys=True))
