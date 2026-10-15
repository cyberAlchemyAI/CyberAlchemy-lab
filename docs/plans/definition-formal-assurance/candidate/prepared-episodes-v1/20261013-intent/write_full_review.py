"""Compose thirteen delivery aspects from immutable typed and consumer reviews."""
from pathlib import Path
import json,re
root=Path.cwd();p=Path(__file__).resolve().parent
u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.intent'
def load(name):return json.loads((u/name).read_text())
fresh=load('fresh-command-results.json')
assert len(fresh)==6 and all(r['exit_code']==0 and not(u/r['stderr']).read_bytes() for r in fresh)
typed=(u/'REVIEW.md').read_text();consumer=(u/'CONSUMER-REVIEW.md').read_text()
# Preserve numbered section boundaries from the original typed review.
sections=re.split(r'(?=^## [0-9]+\.)',typed,flags=re.M)[1:]
assert len(sections)==13
intro='''# Intent: complete candidate delivery review

The candidate formalization of Intent now has independently replayed definitions, types, logic, source obligations, consumer observations, qualification profiles and dependency/inventory checks. All six fresh commands exited zero with empty stderr and exactly matched the original stdout captures. Source-owner fidelity and whole-definition proof remain pending. This review explains the complete current candidate packet, with thirteen aspects and explicit unresolved findings; it does not promote a candidate interpretation to canonical meaning.

The typed stage was frozen and separately audited before consumer work. Its seventeen inputs and five checkers remain byte-exact. The current carrier inspection passed 254 observations and the separate consumer-stage record passed 821 checks. The following sections distinguish the seven source coordinates from the sixteen auxiliary coordinate maps, and declarations from actual execution, satisfaction and authority. Full sealing and its separate audit are subsequent commands whose actual terminal records live outside the seal. Completion of this candidate delivery leaves the original full formalization episode active.

'''
consumer_body=consumer.split('\n\n',1)[1]
consumer_body=consumer_body.replace('Qualified profiles must preserve source scope, field meanings, sibling boundaries and all pending map obligations. Static reuse must continue to delegate live currentness and independently evaluate models. Reachable dependencies, whole113 inventory, six fresh checks, a complete delivery aspect review, sealing and separate audit are still required before the next Definition proceeds.','The qualification profiles preserve source scope, field meanings, sibling boundaries and all pending map obligations. Static reuse delegates live currentness and independently evaluates models. Reachable dependencies, the whole113 inventory and six fresh checks have passed. Full sealing and its separate audit remain the subsequent gates before the next Definition proceeds.')
sections[10]+='\n### Current carrier and consumer correspondence\n\n'+consumer_body+'\n'
profiles=load('authority-profile-checks.json');graph=load('current-dependency-graph.json');local=load('dependency-graph.json');inventory=load('current-inventory.json')
sections[11]+='''
### Qualification and interpretation boundaries

Forty authority profiles exercise the stated source, runtime and carrier qualification conditions. Thirty-nine are rejected; the nominal qualified profile remains unaccepted. The 124 finite comparison frames retain 123 rejections and thirty-nine pending map obligations. These are authored metadata and supplied-model checks. They neither authenticate attribution nor accept the carrier decoding. Changing scope labels, removing a qualification axis or declaring authority from a parent package cannot supply the missing correspondence. Each pending map must identify its source coordinate, actual carrier selector, interpretation, owner and evidence before a faithful shared denotation can be claimed.

The theory T and requested populations I remain separate. A supplied model satisfying both is a witness for this partial formalization. It is not a proof that the source Definition is fully encoded. A true T with false I indicates an uncovered requested population; a false T with true I preserves population coverage while violating a necessary guard. The fresh consumer models retain all four partitions: seven T/I true/true, five true/false, twenty false/true and three false/false. None is decoded from an actual admitted Intent record through an accepted map. The qualification frames leave actual authenticity, revision integrity, satisfaction and source ownership independently open.

### Reuse and fresh validation

Fifteen adversarial and differential static-reuse checks passed. Exact static source verification can be reused within its selected immutable snapshot while current repository state remains delegated to live verification. Candidate models, source correspondence and runtime bindings are checked independently. The before and after original static verification results agree and the original verifier is restored. No live currentness result is reused, and no shared sealed validator is edited. This changes verification cost within the candidate execution; it does not change the original meaning, claim ceiling or checker limits.

The six fresh commands separately check the interpretation contract, candidate models, source obligations, qualified profiles, reachable dependency graph and whole current inventory. Their terminal exit codes, arguments, stdout and stderr are retained. All six actual exits are zero, stderr is empty, and each stdout is byte-equal to its original capture. The contract comparison uses the separately frozen typed contract capture. These independent replays substantiate repeatability of the selected checks. They cannot establish an unbounded theorem about all records or erase any unresolved finding.

'''
sections[12]=sections[12].replace('Three fresh typed-stage checks, the input freeze and a separate audit remain the next gates at this review\'s creation. Full consumer/profile/reuse/dependency/whole113inventory/freshsix/review/seal/separate-audit work follows them.','Three fresh typed-stage checks, the input freeze and a separate typed audit completed with actual zero exits. Consumer, profile, reuse, reachable-dependency and whole113 inventory producers also completed with actual zero exits. Six further fresh checks completed with stdout parity. Full candidate sealing and a separate full audit are the subsequent gates; their actual terminal records, rather than this review alone, establish closure.')
counts=inventory['counts']
extra=f'''
### Current dependencies and inventory

The local reachable graph has {len(local['nodes'])} nodes and {len(local['edges'])} declared edges, with {len(local['missing_or_quarantined_interpretations'])} missing counterpart packets and {len(local['cycle_reviews'])} unresolved cycle classification. It selects 110 existing packets. The joint current graph has {len(graph['nodes'])} nodes and {len(graph['edges'])} declared edges, with {len(graph['missing_or_quarantined_interpretations'])} missing counterparts and {len(graph['cycle_reviews'])} unresolved cycle classification. Intent adds twenty-eight explicit direct semantic uses. The edge denominator still requires independent review; recorded edges and graph reachability do not establish a complete semantic dependency inventory or an accepted fixed-point interpretation.

The current inventory independently re-evaluates one supplied T/I witness for each of 113 partial drafts. Seventy of the 183 current identities still have no typed draft. The inventory preserves all 189 admitted source versions and 201 source files. Its totals are {counts['source_units']} source units, {counts['mapped_clauses']} mapped clauses, {counts['encoded_clauses']} encoded clauses, {counts['explanatory_clauses']} explanatory clauses, {counts['deferred_clauses']} deferred clauses, {counts['required_populations']} required populations and {counts['unresolved_populations']} unresolved populations. Source units and mapped clauses have separate denominators; these totals are not a translation-completeness percentage. The predecessor inventory of 112 drafts remains an immutable historical observation.

Separate per-definition witnesses are not a common model of all definitions. Equal printed symbol names across version-qualified theories do not identify equal denotations. Missing counterpart packets and semantic cycles need explicit treatment before shared consistency can be assessed. No least-fixed-point semantics, acyclic semantic theorem or owner-approved translation is inferred from the acyclic execution plan. The delivery DAG has eighteen nodes and seventeen edges and preserves typed closure before consumer work, fresh checks before the full review, and the seal before the separate audit.

The next planned definition is F08-T.cal.definition.intent-resolution, conditional on actual full Intent closure. Its source may be selected read-only, but native construction follows the full separate audit. That dependency prevents future source selection or authoring from changing the current candidate file set between seal and audit. After child packets exist, ancestor preservation uses exact hashes and retained actual prior audit records; it does not rerun an ancestor exact-file-set audit against an enlarged descendant tree.

### Final candidate claim ceiling

All twenty-three source-owner findings and eighteen consumer findings remain explicit below or in the preceding consumer aspect. No semantic map or whole translation is accepted. The original scope still contains T/O/E/R/J obligations and a final explanation of every formalization aspect. Pending owner records and unresolved experiment or joint-logic outcomes satisfy only the original alternatives that explicitly permit them. They preserve unfinished obligations and evidence boundaries; they cannot replace missing artifacts, authenticate outputs or establish universal proof. The full goal remains active after this candidate delivery.

'''
sections[12]+=extra
text=intro+''.join(sections)
assert len(text.split())>4000 and len(re.findall(r'^## [0-9]+\.',text,re.M))==13
for row in load('correspondence.json')['source_precedence']['conflicts']+load('carrier-consumer-inspection.json')['unresolved_consumer_findings']:assert row['finding_id'] in text
with(u/'DELIVERY-REVIEW.md').open('x') as f:f.write(text)
dag=load('continuation-dag.json');dag['schema_version']='Intent-full-delivery-DAG/v1-candidate';dag['next_native_requires_full_separate_audit']=True;dag['whole_episode_complete']=False
for node in dag['nodes']:
    if node['id'] not in ['seal','audit','original-scope']:node['status']='complete'
    else:node['status']='pending-at-review-creation'
dag['status_reporting']='Historical creation statuses; actual seal and separate audit completion require external terminal records.'
with(u/'work-delivery-dag.json').open('x') as f:json.dump(dag,f,indent=2);f.write('\n')
print(json.dumps({'review_words':len(text.split()),'aspects':13,'source_findings':23,'consumer_findings':18,'DAG_nodes':len(dag['nodes']),'DAG_edges':len(dag['edges'])}))
