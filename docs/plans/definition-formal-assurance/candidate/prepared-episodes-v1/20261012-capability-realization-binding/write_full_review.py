"""Full thirteen-aspect CRB explanation derived only after six actual fresh checks pass."""
from pathlib import Path
import copy,json,re,sys
root=Path.cwd();prepared=Path(__file__).resolve().parent;unit=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.capability-realization-binding';sys.path.insert(0,str(unit));import build_candidate as b
def load(name):return json.loads((unit/name).read_bytes())
fresh=load('fresh-command-results.json');assert [x['check'] for x in fresh]==['contract','model','source','profile','dependency','inventory'] and all(x['exit_code']==0 and not(unit/x['stderr']).read_bytes() for x in fresh)
inventory,graph,local=load('current-inventory.json'),load('current-dependency-graph.json'),load('dependency-graph.json');assert inventory['partial_drafts']==110 and len(inventory['missing_current_drafts'])==73
typed=load('types-logic-receipt.json');b.unchanged(typed['inputs']+typed['checker_bindings'])
text=(unit/'REVIEW.md').read_text();h12=re.search(r'^## 12\..*$',text,re.M);h13=re.search(r'^## 13\..*$',text,re.M);assert h12 and h13
prefix=text[:h12.start()];suffix=text[h13.start():];prefix='# Capability Realization Binding: full candidate delivery and formalization review\n'+prefix.split('\n',1)[1]
suffix=suffix.replace('This typed stage creates the 110th partial candidate and leaves seventy-three identities without T; the historical sealed whole inventory remains the earlier 109-theory observation until refreshed.','This full candidate delivery includes the refreshed110-theory inventory andseventy-three current identities without T. Earlier109-theory inventories retain their historical scopes.')
suffix=suffix.replace('Consumer and profile inspection, reachable dependency and whole110 inventory refresh, six full fresh checks, full review, seal and separate audit still remain before Coordination Context native work.','Consumer/profile observations,replays,reachabledependencies,whole110inventory andsixfreshchecks are complete. Fullreview,seal andseparateactualaudit retain their required boundary before Coordination Context native work.')
consumer=(unit/'CONSUMER-REVIEW.md').read_text().split('\n',1)[1].replace('Full delivery remains unsealed.','The immutable typed receipt retains its earlier scope; this full delivery adds the subsequently verified stages.').replace('Next are qualified authority profiles andtheir replay, a bounded stage audit,reachable dependencies,whole110 independent-witness inventory,six fresh full checks,the full aspect review,seal andseparate audit.','Qualified profiles andtheir replay,the boundedstageaudit,reachabledependencies,whole110independent-witness inventory andsixfreshchecks are now recorded. The fullreview,seal andseparateaudit are distinct required boundaries.')
section='''## 12. Current source, consumer, dependency and delivery evidence

The historical typed receipt retains its exact seventeen inputs andfivechecker bindings. Its three fresh checks andseparate typed audit are distinct from the six actual full-delivery processes now recorded. The first eleven aspects explain the source-bound types,notation,necessary logic andintuition; this aspect adds exact current consumer behavior,proposed maps,qualified profiles andwhole-inventory evidence. All source-owner andshared-denotation limitations remain.

'''+consumer+'''

### Qualified hypotheses and independent verification

Thirty-eight profiles retain one explicit pending baseline andreject thirty-seven incompatible claims.157finite correspondence frames retain one complete unaccepted baseline andreject156incomplete oroverstated frames. Fifty mapping obligations preserve exact endpoints,distinct posture/lifecycle,evidence purposes,canonical authority,optional projection/digest,intended state andextensional succession,as well asC60/C66/C70scope differences. These are constraints on candidate reporting,not decisions about real owner policy,permission orsemantic approval.

Fifteen adversarial differential checks preserve process-local static-only snapshot reuse. Identical serialized snapshot verification may reuse the original static result;every live repository check delegates,and allmodels andsource correspondence packets remain evaluated. The original verifier isrestored andits initial/final static results agree. Different,malformed ormutated snapshots retain their exact original rejection. No shared sealed validator,formula,model expectation orbudget changes.

The six actual independent checks validate contract,models,source,profile,reachabledependencies andwholeinventory. Every terminal record has exit zero andempty stderr,and output parity withthe corresponding successful producer. Longchecks arecaptured separately withprocess identities andstart ticks. A progressfile,path,successful launcher,timeout orsuccessful ancestor run never substitutes forcurrent terminal evidence.

'''
counts=inventory['counts'];section+=f"The refreshed inventory has110partial candidate theories and73currentidentities withoutnativeT. Its independently counted aggregate is {counts['source_units']} source units,{counts['mapped_clauses']} mappedclauses,{counts['encoded_clauses']} encodedclauses,{counts['explanatory_clauses']} explanatoryclauses,{counts['deferred_clauses']} deferredmappings,{counts['required_populations']} requiredpopulations and{counts['unresolved_populations']} unresolvedpopulations. Every oneof110selected supplied per-definition T/I witnesses isfreshly evaluated. These separatelyqualified witnesses are notoneaccepted common-denotation model orwhole proof. Historical I04,prior inventories andoriginal planned-output-presence reviews keep their original scopes.\n\n"
section+=f"The joint declared graph has {len(graph['nodes'])} nodes,{len(graph['edges'])} edges,{len(graph['missing_or_quarantined_interpretations'])} missingcounterpart interpretations and{len(graph['cycle_reviews'])} unclassifiedcycle. CRB's reachable graph has {len(local['nodes'])} nodes,{len(local['edges'])} edges,{len(local['missing_or_quarantined_interpretations'])} missingpackets and{len(load('dependency-selection.json')['packet_refs'])} existingselected packets. Each edge retains exact sourceversion,clause andauthored semantic-use basis. Edge completeness still requires independent review;SCC ordering neitherdecides recursive meaning norinfers least-fixed-point semantics orconsistency.\n\n"
section+='''### Execution boundary, preservation and original scope

The eighteen-node,eighteen-edge acyclic workDAG keeps source selection,signature,sourceaccount,model/query evidence,typed review/freeze andseparate audit before consumer/profile work,dependency/inventory refresh,sixfreshchecks,fullreview,seal andseparate audit. The semantic graph's unresolved cycle is a different object. Coordination Context native creation requires actual full CRB seal andseparate audit success first. Source-only preparation cannot replace that boundary.

The full seal records the exact current candidate file set bypath andSHA-256 whilepreserving10287predecessor files and201source files. The separate actualread-only fullaudit mustverify thatexact set andeachbounded claim. Ancestor exact-file-set audits are notrerun aftera child isadded; their preservedhashes andactualrecorded outcomes retain their narrower scope. Thirty unrelated trackeddirtyfiles remain byte-identical to their independently recorded state.

One prepared model-construction failure isretained withtwenty-six history bindings:collapsing evidence-purpose roles originallyproduced duplicate relation tuples. Givingtherelation itssetrepresentation preserves thecollapsed constants andsemantic rejection expectation. One native source-check failure isretained witheightbindings:the default correspondencecheck omitted thebuilder's requireddependency/conflict denominator arguments;characteraccounting wasalreadycomplete. Correctedsourcechecks retain allrequirements. Neither issue weakens formulas,models,sourceexpectations orlimits.

The first typed-freeze session laterhadamissing handle,no matchingprocess,no terminalcapture andnoreceipt. Itsoldchildexit isnotrecorded;noneisfabricated. Exactcurrentinput/checker bindings,runtime andpredecessor/sourcepreservation justified rerunningonly thatunfinishedfreeze. The actualsuccessfulrerun andseparateaudit remain distinct fromtheinterruption observation. Subsequentconsumer,profile,reuse,dependency,inventory andfreshchecks preserve those histories while recording their ownactual outcomes.

The task receipt closesaverifiedpartialcandidate,not acceptedwholetranslation. Wholeowner-acceptedtranslations andwholeproofs remainzero;acceptedsource-to-consumer maps areempty;sourcefidelitypending andsemanticreadyfalse. No actual adoption,deployment,conformance,successfuloperation,Productvalue,authority-effect orprojectionpublication followsfromthecandidate guards. Independently justifiedoutcomes remainpossible ratherthanuniversallyprohibited.

The original183identities189versions201files121tasks511planningedges797work-units36frontiers and T/O/E/R/J/finalaspect-reviewrequirements remainrequired. Complete explicitlypending orunresolved outcomes can satisfy onlytheir original recordingcriteria;they do notprove acceptedmeaning andcannotexcuse missingartifacts. Remainingdefinitions,obligation sets,actualevaluation orspecifiedunresolvedresult artifacts,attributableorpendingreviews,selectedjointclosures andthefinal original-scope completionaudit remainafterthisdelivery. NativeTpresence alone doesnotcomplete theepisode.

Unresolved consumer findings:

'''
for finding in load('carrier-consumer-inspection.json')['unresolved_consumer_findings']:section+='- '+finding['finding_id']+': '+finding['issue']+'\n'
result=prefix+section+'\n'+suffix
assert len(result.split())>4000 and len(re.findall(r'^## [0-9]+\.',result,re.M))==13
assert all('CRB-FINDING-'+str(i).zfill(3) in result for i in range(1,23)) and all('CRB-CONSUMER-FINDING-'+str(i).zfill(3) in result for i in range(1,14))
with (unit/'DELIVERY-REVIEW.md').open('x') as f:f.write(result)
dag=copy.deepcopy(load('continuation-dag.json'));dag.update({'schema_version':'CRB-full-work-delivery-DAG/v1-candidate','next_native_requires_full_separate_audit':True,'semantic_dependency_graph_is_separate':True,'whole_episode_complete':False,'fresh_actual_checks':[x['check'] for x in fresh]});b.put('work-delivery-dag.json',dag)
print(json.dumps({'result':'CRB full thirteen-aspect explanatory review written from actual six-check evidence','review_words':len(result.split()),'aspects':13,'source_findings':22,'consumer_findings':13,'partial_drafts':110,'semantic_ready':False},indent=2))
