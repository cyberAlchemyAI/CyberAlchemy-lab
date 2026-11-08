"""Reader aids derived from selected contracts; never substitute normative text."""
from html import escape
import re

from source_labels import display_text


CORE_EXAMPLES = {
    'Definition': ('The owner-accepted completeness criterion governs identifier coverage for Northstar, the declared filters and S1.', 'Treating a generated summary or an unaccepted draft as an accepted definition.'),
    'Artifact Type': ('The Work contract specifies how investigation records identify their kind and carry the required information.', 'Assuming a record conforms because its filename says “work.”'),
    'Artifact': ('A particular investigation record has an exact identity and version under its declared Work type.', 'Treating a rendered copy as a separately authoritative record.'),
    'Authority': ('The accepted definition governs meaning; a separate scoped delegation permits the investigation actions.', 'Inferring deployment permission from definition acceptance.'),
    'Provenance': ('Trace the omission claim to S1, E12, the account and filters, method version 2 and the saved comparison.', 'Treating traceability as proof of the cause or permission to act.'),
    'Intent': ('Customers need complete eligible data; this need frames the investigation and possible responses.', 'Treating the need itself as an accepted implementation plan.'),
    'Intent Resolution': ('Choose an investigation as the response to the reported need and declare how satisfaction will be assessed.', 'Assuming a chosen response has already satisfied the intent.'),
    'Product': ('The customer-data platform promises continuing value through export capabilities.', 'Identifying the temporary repair Project as the Product.'),
    'Product Capability': ('Export eligible customer data is a promised Product outcome that an implementation can realize.', 'Treating the promise as proof that a particular implementation delivers it.'),
    'Implementation': ('Software revision 7 is the realization used in run 12; revision 8 is proposed.', 'Treating a proposed revision as deployed or proven to repair the omission.'),
    'Project': ('The export-repair Project coordinates goals, decisions, evidence and work across sessions.', 'Equating the enduring coordination identity with one investigation task.'),
    'Goal': ('Declare the scoped repair outcome, criteria, required evidence and responsible owner.', 'Marking the repair goal achieved solely because investigation Work ended.'),
    'Work': ('Investigate the reported omission with selected inputs, expected results and constraints.', 'Inferring successful outcome or authority from Work completion.'),
    'Source': ('The exact saved S1 input and E12 output provide distinct origins with inspectable integrity boundaries.', 'Assuming source material is true or authoritative merely because it is recorded.'),
    'Operational Observation': ('Record the 200 missing required identifiers during ordinary Project investigation work.', 'Recording “pagination caused the incident” as though it followed from the identifier comparison.'),
    'Evidence': ('The saved comparison and inputs bear on the scoped identifier-omission claim.', 'Using evidence of omission as sufficient evidence of successful recovery.'),
    'Evidence Set': ('Group the selected inputs, method and result that bear on the omission assessment.', 'Assuming that assembling the set accepts its claims.'),
    'Failure Assessment': ('Establish omission in E12 while leaving cause, wider impact and recovery unresolved.', 'Inferring cause or recovery from the occurrence posture.'),
    'Incident': ('The customer-data service owner coordinates investigation and response under the open incident.', 'Closing the incident merely because the agent prepared a proposal.'),
    'Agent Assignment': ('Assign the agent to the bounded Northstar investigation Work.', 'Treating participation in the Work as permission to deploy code.'),
    'Delegation': ('The recorded 30-minute scope permits inspection, comparison and preparation of candidate material.', 'Treating the grant as indefinite or unrestricted authority.'),
    'Agent Instance': ('One temporary machine-agent instance performs session 12; a later session uses a new instance.', 'Making the machine instance the durable owner of project knowledge.'),
    'Agent Session': ('Bind the instance to its exact assignment, views, permissions, inputs, budgets and termination conditions.', 'Continuing on an expired view because the agent remembers its contents.'),
    'Session Memory': ('The current session holds temporary working notes while inspecting the comparison.', 'Relying on those notes as durable project knowledge after termination.'),
    'Project State': ('Persist permitted observations, evidence, proposals and decisions with their exact standing.', 'Assuming a saved candidate proposal has been accepted.'),
    'Context View': ('Prepare a frozen answer to the session’s task-information request, with selected source versions and limits.', 'Treating an expired task view as usable without checking its refresh conditions.'),
    'Ontology View': ('Select an exact consistent cut of subjects and connections for the investigation’s purpose and consumer.', 'Making the derived graph a competing canonical source or an authority grant.'),
    'Operational Lesson': ('Propose checking export boundaries, with evidence, applicability, exclusions, predicted benefit and a falsifier.', 'Claiming improvement merely because the lesson was saved or presented.'),
    'Lesson Application': ('A later export investigation records the exact lesson it actually uses.', 'Counting a lesson displayed in context as demonstrated use.'),
    'Lesson Outcome Assessment': ('Compare the predicted benefit of a used lesson with the later observed outcome.', 'Concluding benefit from the existence of an application record alone.'),
    'Typed Relation': ('A source-bound observation can originate from a Source under a declared ordered pair and qualifier contract.', 'Drawing a convenient connection without a declared signature and required qualifiers.'),
    'Ontology': ('Organize typed meanings, subjects, connections and evidence so the investigation can recover their context.', 'Promoting meaning or granting permission because a node appears in a graph.'),
}

CORE_APPLICABILITY = {
    'Definition': 'When a shared meaning needs an exact version, accountable owner, scope and boundaries.',
    'Artifact Type': 'When declaring or inspecting the requirements for a particular kind of record.',
    'Artifact': 'When identifying a particular typed, versioned piece of recorded work.',
    'Authority': 'When asking what can govern a meaning, rule or effect within a declared scope.',
    'Provenance': 'When tracing an item to its sources, transformations and integrity boundaries.',
    'Intent': 'When making the need and purpose explicit before choosing how to respond.',
    'Intent Resolution': 'When selecting a response to an intent and stating how its satisfaction will be assessed.',
    'Product': 'When identifying the enduring promise of value around which capabilities and work are organized.',
    'Product Capability': 'When describing an outcome promised by one Product, independently of the implementation used to realize it.',
    'Implementation': 'When identifying the exact technical realization, its version, owner, interfaces and build or deployment posture.',
    'Project': 'When related goals, decisions, evidence and work need an enduring coordination identity.',
    'Goal': 'When a Project needs a declared future outcome, achievement criteria, evidence and responsible owner.',
    'Work': 'When organizing a bounded effort with purpose, inputs, participants, expected result and constraints.',
    'Source': 'When identifying the exact origin of content, data, evidence or a claim.',
    'Operational Observation': 'When recording an attributable, bounded datum from ordinary Project work outside the research- or experiment-specific Observation boundary.',
    'Evidence': 'When inspectable material bears on a specific claim within a declared scope.',
    'Evidence Set': 'When assembling provenance-preserving support, counterevidence and limitations for one declared question or claim.',
    'Failure Assessment': 'When evaluating a failure occurrence or declared group while keeping occurrence, mode, cause, impact, containment, recovery and uncertainty independently supported.',
    'Incident': 'When related failure occurrences require coordinated ownership, investigation, containment, recovery, communication and closure.',
    'Agent Assignment': 'When specifying an agent’s participation and job in bounded work.',
    'Delegation': 'When recording a grant of scoped authority with its effective period and revocation conditions.',
    'Agent Instance': 'When identifying the concrete agent performing attributable actions; a machine instance belongs to one session.',
    'Agent Session': 'When binding one instance to its exact assignment, views, permissions, inputs, budgets, working memory and termination conditions.',
    'Session Memory': 'When identifying temporary working memory owned by one Agent Session.',
    'Project State': 'When preserving governed project knowledge outside any individual agent or session.',
    'Context View': 'When preparing an immutable answer to an exact context request from selected source versions.',
    'Ontology View': 'When selecting an immutable projection of an exact consistent ontology cut for a declared purpose and consumer.',
    'Operational Lesson': 'When proposing reusable guidance from experience with evidence, applicability, exclusions, predicted benefit and a falsifier.',
    'Lesson Application': 'When recording actual use of an exact lesson in later work.',
    'Lesson Outcome Assessment': 'When evaluating whether a used lesson produced its predicted benefit in the later work.',
    'Typed Relation': 'When connecting governed subjects through a declared meaning, ordered endpoint pair and required qualifiers.',
    'Ontology': 'When organizing meaning, typed subjects, relationships, evidence and limits into a usable connected model.',
}


def h(text):
    return escape(str(text), quote=True)


def excerpt(value):
    """A complete first paragraph or sentence, with the full scope still below."""
    text = display_text(value or '').strip().split('\n\n')[0]
    if len(text) > 800:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        text = sentences[0]
    return text


class ReaderAids:
    def __init__(self, catalog, type_link):
        self.catalog = catalog
        self.type_link = type_link
        self.by_type = {t['artifact_type_ref']: t for t in catalog['artifact_types']}
        self.by_relation = {r['relation_kind_id']: r for r in catalog['relations']}
        self.by_endpoint = {e['endpoint_kind']: e for e in catalog['endpoints']}
        self.definition_count = self.type_count = self.relation_count = self.endpoint_count = 0
        self.example_count = 0

    def definition(self, d):
        self.definition_count += 1
        rows = []
        use = CORE_APPLICABILITY.get(d['term']) or excerpt(d.get('scope', {}).get('applicability', ''))
        if use:
            rows.append(('When it applies', h(use)))
        types = [t for t in self.catalog['artifact_types'] if d['ref'] in t['semantic_definition_refs']]
        rows.append(('Record formats', ' · '.join(self.type_link(t['artifact_type_ref']) for t in types)
                     or 'No record-type contract in this selected catalog declares this exact definition among the meanings it uses.'))
        if d['term'] in CORE_EXAMPLES:
            good, wrong = CORE_EXAMPLES[d['term']]
            rows.extend([('<a href="incident-walkthrough.html">In the Northstar incident</a>', h(good)), ('Common mistake', h(wrong))])
            self.example_count += 1
        else:
            limits = d.get('scope', {}).get('exclusions', [])
            if limits:
                rows.append(('A stated exclusion', h(excerpt(limits[0]))))
        return '<dl class="reference-aid">' + ''.join(f'<div><dt>{title}</dt><dd>{body}</dd></div>' for title, body in rows) + '</dl>'

    def record_type(self, t):
        self.type_count += 1
        required = t['schema_top_level_required']
        keys = ''.join(f'<li><code>{h(key)}</code></li>' for key in required)
        fields = ('<ul class="required-keys">' + keys + '</ul>') if required else '<p>No required fields are declared directly at the selected schema level.</p>'
        endpoint_kinds = [e['endpoint_kind'] for e in self.catalog['endpoints'] if e['carrier_ref'] == t['artifact_type_ref']]
        refs = ' · '.join(f'<a href="#endpoint-{kind}">{h(kind)}</a>' for kind in endpoint_kinds)
        definitions = [d for d in self.catalog['definitions'] if d['ref'] in t['semantic_definition_refs']]
        examples = [CORE_EXAMPLES[d['term']] for d in definitions if d['term'] in CORE_EXAMPLES]
        example = ('<p><strong><a href="incident-walkthrough.html">Content example from the incident:</a></strong> ' + h(examples[0][0]) + ' This describes the subject; a complete record must satisfy the full contract.</p>') if examples else ''
        complete = {'work', 'operational-observation', 'evidence-set', 'failure-occurrence', 'classification-assignment', 'failure-assessment', 'agent-assignment', 'delegation', 'agent-session', 'context-view', 'measurement-method', 'measurement-result', 'definition'}
        if t['semantic_kind'] in complete:
            example += '<p><a href="record-examples.html#example-' + h(t['semantic_kind']) + '">Inspect a complete specimen and a one-field failure →</a></p>'
        return ('<div class="reference-aid type-reading"><h4>Prepare a record</h4>' + fields
                + '<p class="small">These keys are required at the selected schema level. Nested fields, alternatives and referenced rules remain in the full schema.</p>'
                + example + '<p><strong>Declared endpoint kinds for this exact carrier:</strong> '
                + (refs or 'None in this selected catalog.') + '</p></div>')

    def pattern(self, relation, pair):
        self.catalog_pair(relation, pair)
        source = pair['source_kind']; target = pair['target_kind']
        endpoint = lambda kind: f'<a href="#endpoint-{h(kind)}">{h(kind)}</a>' if kind in self.by_endpoint else h(kind)
        qualifiers = ', '.join(relation['required_qualifier_axes']) or 'None declared'
        return ('<div class="reference-pattern">' + endpoint(source) + '<span><strong>'
                + h(relation['predicate']) + ' <span class="direction-right" aria-hidden="true">→</span><span class="direction-down" aria-hidden="true">↓</span></strong><small>Required: ' + h(qualifiers)
                + '</small></span>' + endpoint(target) + '</div>')

    @staticmethod
    def catalog_pair(relation, pair):
        assert pair in relation['allowed_endpoint_pairs'], (relation['predicate'], pair)

    def relation(self, r):
        self.relation_count += 1
        if not r['allowed_endpoint_pairs']:
            return ''
        pair = r['allowed_endpoint_pairs'][0]
        return '<div class="reference-aid"><h4>Read one permitted pattern</h4>' + self.pattern(r, pair) + '<p class="small">This pattern is one declared ordered pair. A complete connection needs exact endpoints and every applicable contract requirement. Other permitted pairs are listed below.</p></div>'

    def endpoint(self, e):
        self.endpoint_count += 1
        pairs = [(r, p) for r in self.catalog['relations'] for p in r['allowed_endpoint_pairs']
                 if e['endpoint_kind'] in (p['source_kind'], p['target_kind'])]
        if not pairs:
            return '<p>No allowed connection pair for this kind is declared in the selected catalog.</p>'
        r, pair = pairs[0]
        return '<div class="reference-aid"><h4>One declared connection for this kind</h4>' + self.pattern(r, pair) + '<p class="small">Open <a href="#rel-' + r['relation_kind_id'].replace('.', '-') + '">' + h(r['predicate']) + '</a> for all its permitted pairs and qualifier rules.</p></div>'

    def receipt(self):
        return {'schema_version': 'editorial-reference-aids/v1', 'authority_effect': 'none',
                'definitions': self.definition_count, 'artifact_types': self.type_count,
                'relations': self.relation_count, 'endpoints': self.endpoint_count,
                'reviewed_incident_examples': self.example_count,
                'derivation': 'Applicability and exclusions from captured definitions, with reviewed plain introductions for core concepts; type links from exact semantic references; required keys from selected schemas; patterns from exact ordered pair declarations.',
                'preservation': 'Introductions only; exact normative statements, scope, versions, acceptance, identities, hashes, schemas and pair tables remain unchanged.'}
