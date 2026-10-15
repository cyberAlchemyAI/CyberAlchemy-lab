"""Write the thirteen-aspect CI review only after all six actual fresh checks pass."""
from pathlib import Path
import copy, json, re, sys
root, prepared = Path.cwd(), Path(__file__).resolve().parent
unit = root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.capability-instance'
sys.path.insert(0, str(unit))
import build_candidate as b


def load(name):
    return json.loads((unit/name).read_bytes())


fresh = load('fresh-command-results.json')
assert [x['check'] for x in fresh] == ['contract', 'model', 'source', 'profile', 'dependency', 'inventory']
assert all(x['exit_code'] == 0 and not (unit/x['stderr']).read_bytes() for x in fresh)
inventory, graph, local = load('current-inventory.json'), load('current-dependency-graph.json'), load('dependency-graph.json')
assert inventory['partial_drafts'] == 109 and len(inventory['missing_current_drafts']) == 74
typed = load('types-logic-receipt.json')
b.unchanged(typed['inputs'] + typed['checker_bindings'])
original = (unit/'REVIEW.md').read_text()
heading12 = re.search(r'^## 12\..*$', original, re.M)
heading13 = re.search(r'^## 13\..*$', original, re.M)
assert heading12 and heading13
prefix, suffix = original[:heading12.start()], original[heading13.start():]
prefix = '# Capability Instance: full candidate delivery and formalization review\n' + prefix.split('\n', 1)[1]
suffix = suffix.replace('This types stage remains a partial candidate.', 'This full delivery remains a partial semantic candidate.')
consumer = (unit/'CONSUMER-REVIEW.md').read_text().split('\n', 1)[1]
consumer = consumer.replace('The full CI delivery is still unsealed.', 'The immutable typed receipt retains its earlier scope; the subsequent full delivery adds the independent evidence below.')
consumer = consumer.replace('Next are the qualified authority profiles, strict reuse and dependency/inventory checks, six fresh terminal checks, full aspect review, seal and separate audit.', 'The current evidence includes qualified profiles and their replay, strict reuse, dependency and inventory refresh and six fresh checks. Full sealing and its separate audit retain their own required boundary.')
section = '''## 12. Current consumer, dependency, inventory and delivery evidence

The historical typed receipt is preserved byte-for-byte. Its three fresh checks and separate typed audit are earlier observations, distinct from the six actual full-delivery checks now recorded. The first eleven aspects retain the source-bound types, logic, intuition and claim ceilings. This aspect adds exact consumer comparisons, proposed maps, qualification, reachable dependencies and the current whole inventory. Successful local checks do not close missing translations, owner fidelity, accepted shared denotations or whole proofs.

'''+consumer+'''

### Qualified profiles and independent checks

Thirty-seven finite authority profiles retain one explicit pending baseline and reject thirty-six incompatible mutations. The 142 finite correspondence frames retain one complete pending baseline and reject 141 incomplete or overstated frames. Forty-five map obligations retain coordinate, owner, context, identity, claim-lane, recursion, adoption, construction, conformance, lifecycle and positive admission scope distinctions. No owner review or accepted map reference is invented. These qualification checks constrain the candidate report; they do not decide actual owner policy or establish real permission.

Fifteen differential and adversarial checks preserve the exact process-local static-snapshot reuse boundary. Only identical serialized snapshot validation can reuse an earlier static result. Every live repository currentness check delegates, every model witness is evaluated, every correspondence packet is accounted, and substituted or malformed inputs retain the original rejection. The original verifier is restored and its initial and final static results match. No sealed shared validator or evaluation bound changed.

Six fresh checks run as actual independent Python processes: contract, model, source, profile, reachable dependencies and the whole inventory. Every check records terminal exit zero, empty stderr and stdout parity with its successful producer. The two heavy graph/inventory checks are captured separately. A path, live progress observation, successful launcher or timeout is not substituted for a terminal result. Source, model, schema and consumer evidence remain distinct even when all these checks pass.

'''
counts = inventory['counts']
section += f"The refreshed whole inventory contains 109 partial candidate theories and 74 current identities without a native T. Its independent aggregate account is {counts['source_units']} source units, {counts['mapped_clauses']} mapped clauses, {counts['encoded_clauses']} encoded clauses, {counts['explanatory_clauses']} explanatory clauses, {counts['deferred_clauses']} deferred mappings, {counts['required_populations']} required populations and {counts['unresolved_populations']} unresolved populations. All 109 selected per-definition T/I witnesses are freshly evaluated. Each witness belongs to its qualified partial theory; there is no accepted common-carrier or meaning-aligned combined model. Historical I04 and prior inventory reports retain their original scopes.\n\n"
section += f"The joint declared graph contains {len(graph['nodes'])} nodes, {len(graph['edges'])} edges, {len(graph['missing_or_quarantined_interpretations'])} missing counterpart interpretations and {len(graph['cycle_reviews'])} unclassified semantic cycle. CI's reachable graph contains {len(local['nodes'])} nodes and {len(local['edges'])} edges, with {len(local['missing_or_quarantined_interpretations'])} missing packets and {len(load('dependency-selection.json')['packet_refs'])} selected existing packets. Every edge is an exact authored semantic use with source-qualified basis. Edge completeness requires independent review. Strongly connected component ordering does not decide cycle meaning, infer least-fixed-point semantics or prove consistency.\n\n"
section += '''### Execution order and full closure

The eighteen-node execution DAG preserves source selection, signature, source accounting, model and query evidence, typed review/freeze and separate audit before consumer/profile work, dependency and inventory refresh, six fresh checks, full review, full seal and separate audit. Its acyclic execution order is distinct from the semantic graph's unresolved strongly connected component. Capability Realization Binding native creation requires the actual completed full CI seal and separate audit first; preparation cannot substitute for that boundary.

The full seal records every current candidate path and SHA-256 while preserving all 10,188 predecessor files and 201 source files. The separate actual read-only full audit must verify that exact file set and each bounded claim before the next native unit is created. Earlier immutable ancestor audits are not rerun after child additions. Thirty unrelated tracked dirty files retain their separately recorded bytes. These preservation conditions prevent this candidate episode from rewriting source meaning, live state or unrelated implementation work.

The positive Definition admission is neither translation acceptance nor instance authority. Candidate and historical body labels are retained beside their exact current admission overlays. The full task receipt records a verified partial draft, pending source-owner acceptance, absent whole proof, explicit unresolved maps and semantic readiness false. Actual instance identity fidelity, parent exactness, ownership, context resolution, realization, adoption, construction, conformance, lifecycle, recomposition, termination and authority remain independent evidence targets.

The two retained consumer producer failures concern exact local schema resource binding and actual control-case naming. A discovery serialization failure and earlier prepared syntax/review-heading diagnostics also retain their exact records. None is silently replaced by a success report or used to weaken formulas, models, schema expectations or limits. The user-interrupted earlier typed audit has no fabricated child exit; its observation, preserved bindings and successful separate rerun remain explicit.

This delivery contributes to the original episode, not a reduced substitute. All remaining source definitions, operational obligation sets, actual evaluation or explicit unresolved outcome artifacts, attributable or explicitly pending reviews, selected joint closures, original final completion audit and aspect-by-aspect explanation remain required. A criterion permitting an explicit pending record still requires that record and cannot justify a missing artifact. T file presence alone does not finish T/O/E/R/J work or prove shared meaning.

'''
observations = load('carrier-consumer-inspection.json')
section += '\nUnresolved consumer findings:\n\n'
for finding in observations['unresolved_consumer_findings']:
    section += '- '+finding['finding_id']+': '+finding['issue']+'\n'
text = prefix + section + '\n' + suffix
assert len(text.split()) > 4000 and len(re.findall(r'^## [0-9]+\.', text, re.M)) == 13
assert all('CI-FINDING-'+str(i).zfill(3) in text for i in range(1, 27))
assert all('CI-CONSUMER-FINDING-'+str(i).zfill(3) in text for i in range(1, 13))
with (unit/'DELIVERY-REVIEW.md').open('x') as stream:
    stream.write(text)
dag = copy.deepcopy(load('continuation-dag.json'))
dag.update({'schema_version': 'definition-assurance-CI-full-work-delivery-DAG/v1-candidate',
            'source': load('context.json')['source_selection'], 'next_native_requires_full_separate_audit': True,
            'semantic_dependency_graph_is_separate': True, 'whole_episode_complete': False,
            'fresh_actual_checks': [x['check'] for x in fresh]})
b.put('work-delivery-dag.json', dag)
print(json.dumps({'result': 'CI full thirteen-aspect review written from actual six-check evidence',
                  'words': len(text.split()), 'aspects': 13, 'source_findings': 26, 'consumer_findings': 12,
                  'partial_drafts': 109, 'semantic_ready': False}, indent=2))
