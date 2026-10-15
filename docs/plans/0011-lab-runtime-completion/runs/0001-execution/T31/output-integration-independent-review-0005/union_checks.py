"""Independent data-only union audit; no capture writer, API or Source guard imports."""
import hashlib,json,stat
from pathlib import Path
from collections import Counter
R=Path('/home/vlad_/projects/CyberAlchemy-lab');RUN=R/'docs/plans/0011-lab-runtime-completion/runs/0001-execution';P=RUN/'T07/final-capture6-union-input-proposal-0002';O=RUN/'T31/output-integration-independent-review-0005';checks=[]
def need(v,w):
 if not v:raise AssertionError(w)
 checks.append(w)
def raw(p):return Path(p).read_bytes()
def sha(p):return hashlib.sha256(raw(p)).hexdigest()
def obj(p):return json.loads(raw(p))
def b(row):
 p=R/row['path'];need(sha(p)==row['sha256'],'binding '+row['path'])
 if 'size_bytes'in row:need(p.stat().st_size==row['size_bytes'],'size '+row['path'])
 if 'mode'in row:need(stat.S_IMODE(p.stat().st_mode)==row['mode'],'mode '+row['path'])
 return p
for name,pin in [('HANDOFF.json','ddc078b2d98a9c24afcb977f374f9c46356d5fa6fcff8c92140639fb4cdcb8e0'),('source-manifest.json','44406746fad55b813aafb0b583ec646a43fb6cf820b0330da7cf688a31d40cc1'),('union.json','6e43c97543bfd9d3c7a7f08e1d72bc231201938c59f0a37f77537372b1737666')]:need(sha(P/name)==pin,'independent selected '+name)
mf=obj(P/'source-manifest.json');[b(x)for x in mf['files']];u=obj(P/'union.json');plan=obj(P/'input-plan.json');m=obj(P/'component-declaration-map.json');ext=obj(P/'external-inputs.json');[b(x)for x in ext['bindings']]
need(not u['active']and not u['actual_capture_run']and u['actual_full_Source_count']is None,'data union remains inactive and unexecuted')
need(len(u['rows'])==38 and len({x['target']for x in u['rows']})==38 and not u['physical_target_duplicates'],'38 unique exact target union')
existing=0;table={}
for row in u['rows']:
 target=R/row['target'];post=row['postimage_binding'];need(post['path']==row['target']and post['sha256']==row['postimage_source_binding']['sha256'],'postimage target/source SHA correspondence '+row['target']);b(row['postimage_source_binding']);table[row['target']]=post['sha256']
 if row['preimage_binding']is None:need(not target.exists(),'new target remains absent '+row['target'])
 else:
  existing+=1;b(row['preimage_binding']);b(row['held_preimage_binding']);need(row['preimage_binding']['sha256']==row['held_preimage_binding']['sha256'],'held exact old bytes '+row['target'])
 need(row['accepted']is False and row['apply_performed']is False,'no adoption implicit '+row['target'])
need(existing==6 and len(u['rows'])-existing==32,'six existing and32 absent')
for name,component in u['components'].items():
 for key in ('handoff','manifest','adoption'):b(component[key])
 ad=obj(R/component['adoption']['path'])
 if name=='T31-v5':need(len(ad['rows'])==26 and component['independent_peer']is None,'exact v5 stage selected peerpending')
# Existing closed Source metadata is read only as declared public JSON, never verified as a runtime proof here.
API='product/lab/release-candidates/v1/interface/api-integration-v17/';source=obj(R/API/'source-manifest.json');oldapi={x['path']:x['sha256']for x in source['files']if x['path'].startswith(API)and Path(x['path']).name not in {'contract-profile.json','SCHEMA-EXECUTION-DEPENDENCIES.json'}};need(len(oldapi)==165,'actual retained closed165 API code/body members excluding two generated metadata inputs')
future=dict(oldapi);future.update(table);need(len(future)==197 and future=={x['path']:x['sha256']for x in u['proposed_API_expected_files']},'exact proposed197 equals original165 plus32 new and6 replacements')
svc=obj(RUN/'T31/output-integration-preparation-0005/service-code-inventory.json');need(u['Service_union']==svc and svc['count']==103,'same103 union exact v5 inventory')
need(set(svc['final_names'])==set(svc['original_names'])|set(svc['T31_additional_names'])|set(svc['separate_required_T15_names']),'original71 plus24 T31 plus8 separate T15 names')
need(all(API+n in future for n in svc['final_names']),'all103 Service selected filenames present in exact future API inventory')
# Preserve every declaration index and original bytes, using held old bodies
# at true paths for each future-mutated original, never relabel original paths.
need(len(m['declarations'])==524 and m['mapped_historical_declarations']==10,'all524 declaration rows and10 historical mappings')
counts=Counter();history=0;physical=set()
for row in m['declarations']:
 original=row['original_declaration'];cm=row['component_manifest'];key=(cm['path'],cm['sha256']);declared=obj(R/cm['path'])['files'];need(declared[row['declaration_index']]==original,'original declaration index exact '+str(key)+' '+str(row['declaration_index']));counts[key]+=1
 chosen=row['selected_physical_binding'];b(chosen);need(chosen['sha256']==original['sha256'],'same original body digest '+original['path']);need((R/chosen['path']).stat().st_size==original['size_bytes'],'same original body size '+original['path']);physical.add((chosen['path'],chosen['sha256']))
 if row['disposition']=='unchanged-declaration':need(chosen['path']==original['path'],'unchanged origin not relabeled '+original['path'])
 else:
  history+=1;need(chosen['path']!=original['path'] and row['original_origin_reinterpreted_as_current']is False,'historical origin explicit nonalias '+original['path']);need(original['path']in table and table[original['path']]!=original['sha256'],'held preimage for genuinely future changed row '+original['path'])
need(sorted(counts.values())==[8,33,483]and history==10 and len(physical)==511,'all483/33/8 rows retained and511 deduplicated physical bindings')
need(m['future_aggregate_manifest']is None and m['future_aggregate_peer']is None,'active aggregate writer/peer pending')
sw=plan['software3'];oldsw=obj(b(sw['historical_software2_binding']))['files'];newsw=sw['exact_same_16_selected_origins'];need(len(oldsw)==len(newsw)==16 and {x['path']for x in oldsw}=={x['path']for x in newsw},'same16 runtime software origins retained');changed=[x for x in newsw if x not in oldsw];need(len(changed)==1 and changed[0]['path']==API+'service.py'and changed[0]['sha256']==table[API+'service.py'],'only actual future Service changes in proposed software3')
for x in newsw:
 if x['path']not in table:b(x)
need(sw['new_binding']is None and sw['new_peer']is None,'software3 actual postunion selection/peer absent')
need(len(plan['predecessor_metadata'])==4,'all four captured metadata preservation obligations')
for name,row in plan['predecessor_metadata'].items():b(row['original_binding']);need(row['snapshot_binding']['sha256']==row['original_binding']['sha256'],'exact snapshot byte pin '+name)
need(plan['current_consumption_conclusions']['profile_updates_default']==[],'no blanket profile binding reinterpretation')
need('not full closure'in plan['current_consumption_conclusions']['transitive_result'],'partial consumed-callback audit remains explicit gate')
need(plan['Root_packet_and_selection']['T31_v5_peer_binding']is None and plan['Root_packet_and_selection']['final_root_packet_binding']is None,'Root final input packet/peer remains pending')
need(any(x['target']==API+'release_readiness.py'and 'independently bind'in x['standing']for x in u['semantic_composition_overlaps']),'T15 new readiness code actual late-control binding retained as gate')
for x in plan['required_public_direct_inputs']:b(x)
for key in ('reuse_exact_frozen_writer','reuse_preparation_handoff','reuse_preparation_manifest','reuse_preparation_scoped_review'):b(plan[key])
need(plan['conserved_predecessor_counts']['original_source']==24497 and plan['conserved_predecessor_counts']['original_profile']==24496 and plan['conserved_predecessor_counts']['unavailable_REFUSED']==25,'original24497/24496 and25REFUSED retained')
[b(x)for x in mf['files']]
res={'schema_version':'lab-Source6-data-union-independent-checks/v1','result':'PASS-inactive-data-proposal-only','checks':checks,'check_count':len(checks),'targets':38,'existing':6,'new_absent':32,'future_API_members':197,'Service_names':103,'mapped_declarations':524,'historical_preimage_mappings':10,'physical_bindings':511,'software_origins':16,'actual_Root_union_aggregate_software3_snapshots_packet_capture_and_callback_closure_pending':True,'Source_API_capture_writer_native_runtime_or_guard_executed':False,'authority_effect':'none'};(O/'union-result.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in res.items()if k!='checks'},sort_keys=True))
