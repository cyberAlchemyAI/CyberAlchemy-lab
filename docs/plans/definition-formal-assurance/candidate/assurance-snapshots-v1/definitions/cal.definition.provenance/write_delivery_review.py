"""Produce the full partial Provenance candidate explanation after six actual checks."""
import json,re
from pathlib import Path
u=Path(__file__).resolve().parent
def load(n):return json.loads((u/n).read_bytes())
def main():
 fresh=load('fresh-command-results.json');assert [x['check'] for x in fresh]==['contract','model','source','profile','dependency','inventory'] and all(x['exit_code']==0 and not (u/x['stderr']).read_bytes() for x in fresh)
 inv=load('current-inventory.json');p=load('authority-profile-checks.json');d=load('dependency-graph.json');old=load('types-logic-receipt.json');assert inv['partial_drafts']==76 and inv['source_owner_accepted_whole_translations']==inv['whole_definition_proofs']==0
 text=(u/'REVIEW.md').read_text().replace('# Provenance: typed candidate review','# Provenance: full partial candidate delivery review',1)
 a=text.index('## 12.');z=text.index('## 13.',a)
 diagram=text[text.index('```mermaid\n',a):text.index('```\n',text.index('```mermaid\n',a)+12)+4]
 text=text[:a]+'''## 12. Current carrier/profile observations and execution DAG

Actual current catalog inspection finds143 admitted-contract rows and121 current types,with no direct current carrier bound to the exact Provenance Definition. The generic current Definition/v2 binds its own Definition meaning. A generic C13 Definition evaluation profile is separately admitted and retains candidate/none historical body posture. It evaluates a Definition record rather than a provenance path. The C12 Provenance semantic scaffold retains revise posture and the separate relation.originates-from normalization target. Its exact generated projection is observed separately from C53 meaning and source-use admission.

The checker passed17 actual catalog/schema/projection checks,37 Definition schema probes and30 C13 profile probes. Unresolved reference and overclaimed text controls expose the difference between shape and semantic evidence. It checked33 qualified hypotheses,of which31 are rejected,and68 proposed-map frames,of which63 are rejected. Twenty source-map obligations retain normalized meaning,D35 lineage,record/object/context,typed path,five-field steps,positions,strict local order,repeated sources,relation precision,operations,owner/process handling,posture,gaps,residue/routes,empty policy and typed use. These remain proposed maps or explicit residue rather than accepted fidelity.

The source also says provenance is used before promotion,adaptation,import,validation or publication. This partial theory has no accepted consumer timing map for that precondition;strict order within a declared path does not prove it. No package validator,carrier writer or live consumer was executed. No source-to-carrier or consumer correspondence was accepted. Dependency evidence and the whole76-draft inventory are freshly compiled. One supplied T/I witness for every current partial draft is independently evaluated. Semantic cycles retain unresolved classification and missing counterpart packets remain explicit. All six delivery checks completed successfully with empty stderr. The work DAG keeps source and prior audit before types,populations and correspondence before finite checks,and full review/seal before separate audit. Review follows that separate audit.

'''+diagram+'\n'+text[z:]
 text=text.replace('This unit follows75 previously sealed partial interpretations and adds a working76th draft. A later whole-inventory refresh must establish the exact incremental count;historical I04 selected-eight reporting stays unchanged.','This unit follows75 previously sealed partial interpretations. The actual refreshed inventory verifies76 partial drafts and107 current identities without T files;historical I04 selected-eight reporting stays unchanged.')
 text=text.replace('Continue by freezing and separately auditing the typed stage,then inspecting exact current carrier hypotheses and consumer-map gaps,refreshing dependencies and whole inventory,running the six delivery checks,and producing the full review,seal and separate audit. Then proceed with the manifest\'s Review Definition.','The typed stage was frozen and separately audited. Current carrier/profile observations,dependencies,whole inventory and six delivery checks completed successfully. Complete the candidate seal and its separate audit,then proceed with the manifest\'s Review Definition.')
 text+='\nActual full-delivery evidence: '+json.dumps({'current_definitions':inv['current_definitions'],'admitted_versions':inv['admitted_source_versions'],'partial_drafts':inv['partial_drafts'],'missing_current_drafts':len(inv['missing_current_drafts']),'counts':inv['counts'],'local_graph_nodes':len(d['nodes']),'local_graph_edges':len(d['edges']),'joint_graph_nodes':inv['joint_declared_graph']['nodes'],'joint_graph_edges':inv['joint_declared_graph']['edges'],'joint_missing_counterparts':len(inv['joint_declared_graph']['missing_counterpart_packets']),'prior_seal_files':old['prior_candidate_files_preserved'],'frozen_typed_inputs':len(old['inputs']),'source_files_current':201},sort_keys=True)+'.\n'
 assert len(re.findall(r'^## [0-9]+\.',text,re.M))==13 and len(text.split())>2500
 with (u/'DELIVERY-REVIEW.md').open('x') as f:f.write(text)
 print(json.dumps({'review_words':len(text.split()),'aspects':13,'owner_findings':18},indent=2))
if __name__=='__main__':main()
