"""Assemble an aspect-based full delivery explanation from verified typed and consumer evidence."""
from pathlib import Path
import json,re
p=Path(__file__).resolve().parent;root=Path.cwd();unit=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.coordination-context';load=lambda name:json.loads((unit/name).read_bytes())
fresh=load('fresh-command-results.json');assert len(fresh)==6 and all(row['exit_code']==0 and not(unit/row['stderr']).read_bytes() for row in fresh)
inventory=load('current-inventory.json');graph=load('current-dependency-graph.json');local=load('dependency-graph.json');consumer=load('carrier-consumer-inspection.json');lineage=load('consumer-lineage-checks.json');profile=load('authority-profile-checks.json');core=load('t.json')['payload']
typed_text=(unit/'REVIEW.md').read_text();parts=re.split(r'(?m)^## ([0-9]+)\. ([^\n]+)\n',typed_text);paragraphs=(unit/'CONSUMER-REVIEW.md').read_text().split('\n\n');assert len(paragraphs)==23
assign={1:[2,3],2:[15],3:[4,19],4:[5,6],5:[7,8],6:[11,12],7:[10],8:[13],9:[14],10:[16],11:[17,18],12:[9],13:[1,20,21,22]}
header=f'''# Coordination Context full candidate delivery review

This review explains the full partial-candidate delivery evidence for cal.definition.coordination-context@1.0.0-candidate.1. The source remains C18-admitted with SHA-256 547a714a9552f83985de78b2ce228421f5102c40cacf8c1edfb48ef46366a8aa. Canonical Definitions alone control normative meaning. Prepared and native source/build/model checks, independent source checks, three fresh typed checks, typed freeze and separate typed audit completed successfully before the full delivery work. Six fresh full checks now have actual exit zero, empty stderr and stdout equality. The full seal and separate full audit are the next two gates; their terminal captures determine subsequent closure.

The bounded evidence includes 174 declarations, seven primitive theory formulas, 198 supplied controls, 32 nonentailment queries, 86 source checks and 74 exact-span source-query obligations. Consumer inspection adds 288 checks, 25 proposed coordinate maps, 56 carrier probes, 11 Definition probes and 30 fresh hypothetical T/I comparisons. Thirty-eight authority profiles reject 37 unsupported variants; 148 unaccepted-map frames reject 147 variants. All 47 map obligations remain pending. Fifty independent historical-lineage checks replay 22 cases and six lifecycle cases, retaining five historical v1 blind spots. No actual carrier writer, package validator main, native consumer or live runtime is executed.

Whole inventory has {inventory['partial_drafts']} partial theories and {len(inventory['missing_current_drafts'])} current identities without T drafts. Its newly evaluated independent supplied T/I witnesses establish only the reported per-theory behavior. Aggregate source counts are {json.dumps(inventory['counts'],sort_keys=True)}. The joint declared graph contains {len(graph['nodes'])} nodes, {len(graph['edges'])} edges, {len(graph['missing_or_quarantined_interpretations'])} missing counterparts and {len(graph['cycle_reviews'])} unresolved cycle classification. The local reachable graph contains {len(local['nodes'])} nodes and {len(local['edges'])} edges with {len(local['missing_or_quarantined_interpretations'])} missing counterparts. Execution-plan acyclicity does not resolve those semantic questions.

The original scope remains 183 identities, 189 versions, 201 source files, 121 tasks, 511 planning edges, 797 work units and 36 frontiers, including T/O/E/R/J and the final complete episode explanation. Accepted whole translations and whole-definition proofs remain zero. source_fidelity is pending and semantic_ready is false. This review is candidate evidence rather than an owner decision, admission or whole-definition proof.

'''
review=header
for i in range(1,len(parts),3):
 number=int(parts[i]);title=parts[i+1];body=parts[i+2]
 body=body.replace('A fresh typed-input freeze and a separate audit are still required to close this bounded stage.','The typed-input freeze and separate audit completed with actual exit zero; their seventeen inputs and five checker bindings remain unchanged.')
 body=body.replace('Full consumer inspection, authority-profile observations, static snapshot reuse, reachable dependencies, whole-inventory refresh, six fresh full-delivery checks, a full delivery review, sealing and a separate delivery audit remain required after the typed stage.','Consumer inspection, authority-profile observations, static snapshot reuse, reachable dependencies, whole-inventory refresh and six fresh full-delivery checks now have actual successful terminal evidence. This full review records their limits. Sealing and a separate delivery audit remain the next gates.')
 body=body.replace('The next action is the unfinished full delivery of this Coordination Context candidate, followed by the remaining planned definitions with definitions, types and logic first.','The next gates are the full candidate seal and separate audit, followed by Implementation and the remaining planned definitions with definitions, types and logic first.')
 review+='## '+str(number)+'. '+title+'\n'+body.rstrip()+'\n\n'
 additions=[paragraphs[index] for index in assign[number]]
 additions=[text.replace('The next completion gates are qualified authority profiles, static reuse validation, reachable dependencies, whole111 inventory, six fresh full-delivery checks, full aspect review, seal and a separate audit.','Qualified authority profiles, static reuse, reachable dependencies, whole111 inventory and six fresh full-delivery checks have completed. Full sealing and a separate delivery audit remain next.') for text in additions]
 review+='\n\n'.join(additions)+'\n\n'
 if number==11:
  review+='The separately replayed historical non-collapse audit matches all four positive and eighteen hostile cases and all six lifecycle cases. Its five v1 semantic blind spots and four historical findings are retained as historical evidence. The exact v2 package binds that same audit digest. This current read-only replay neither changes the historical validator nor converts the older candidate audit into current package authority.\n\n'
 if number==12:
  review+='All 10,389 predecessor files, 201 sources, thirty unrelated tracked files, seventeen typed inputs and five typed checkers are preserved. Fifteen static-reuse checks passed with live currentness delegated to the original resolver; no model or correspondence evaluation was skipped. The full delivery introduces separate current111 inventory records and leaves historical inventories unchanged. Two preparation failures and three consumer-checker failures are retained with exact evidence.\n\n'
assert len(review.split())>4000 and len(re.findall(r'^## [0-9]+\.',review,re.M))==13
with (unit/'DELIVERY-REVIEW.md').open('x') as f:f.write(review)
dag=load('continuation-dag.json');dag['schema_version']='CoordinationContext-full-delivery-DAG/v1-candidate';dag['next_native_requires_full_separate_audit']=True;dag['whole_episode_complete']=False
for node in dag['nodes']:
 node['status']='pending' if node['id'] in ['seal','audit','original-scope'] else 'actual-candidate-evidence-complete'
with (unit/'work-delivery-dag.json').open('x') as f:json.dump(dag,f,indent=2);f.write('\n')
print(json.dumps({'full_review_words':len(review.split()),'aspects':13,'source_findings':21,'consumer_findings':15,'work_dag_nodes':len(dag['nodes']),'work_dag_edges':len(dag['edges']),'whole_episode_complete':False}))
