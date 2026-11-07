"""Readable, paged explanations beside complete, unaltered diagram assets."""
import json
import re
from html import escape

# These explanations restate the existing diagram descriptions and labels.
# They add no model relations, permissions, or implementation claims.
READINGS = {
 'evidence-chain': [
  ('Saved inputs and output', 'Start with snapshot S1 and Northstar’s saved output E12. Preserve the account, filters and selected identifiers.'),
  ('Compare the identifier sets', 'Method 2 compares the required identifiers with the actual output identifiers. A row count alone cannot show which records are missing.'),
  ('Evidence supports a bounded assessment', 'The Evidence Set identifies 200 required identifiers missing from the output. The omission is confirmed; its cause and recovery remain unresolved.')],
 'admission-and-histories': [
  ('Specific proposal', 'Identify the records, versions and exact requested changes.'),
  ('Review the decision bundle', 'Independent decisions share a review checkpoint. Sharing a review does not extend any decision’s permission.'),
  ('Apply authorized changes', 'An Admission Transaction applies the accepted record changes together and saves the updated Project State.'),
  ('Keep two separate histories', 'The change history records what changed. The approval history records why it was accepted. Both identify the same specific change event.')],
 'meaning-shape-record': [
  ('Definition: meaning', 'What does Work mean? A bounded unit of effort.'),
  ('Artifact type: required format', 'What must a Work record contain? Declared fields and constraints.'),
  ('One Work record: this investigation', 'Which investigation is this? Investigate Northstar’s omission. Format conformance and owner acceptance retain their own requirements.')],
 'records-and-ontology': [
  ('Begin with particular records', 'Operational Observation version 1 originates from Source records identifying snapshot S1 and output E12.'),
  ('Distinguish the origin roles', 'S1 identifies the required input. E12 identifies the observed output. Both connections use originates-from, from the observation to a Source.'),
  ('Read the ontology view as a representation', 'The lower graph represents those same subjects and connections. It does not replace the records or change their standing.')],
 'agent-session': [
  ('Project State survives the session', 'Northstar’s observation, candidate revision 8, decisions and evidence are saved outside the agent, with separate histories of changes and acceptance.'),
  ('Views select exact information', 'Context View 3 selects snapshot S1, output E12 and rules. The Ontology View represents the investigation records and source trail.'),
  ('The agent session is temporary', 'Session 12 brings together the agent instance, investigation assignment, separate delegation, actions, tools and working memory.'),
  ('Record useful output; recheck expired views', 'Useful output needs authorized recording. Working memory ends with the session. When View 3 expires, continuation needs a checked replacement and current permission.')],
 'purpose-to-implementation': [
  ('Intent and resolution', 'Intent states the desired change. Intent Resolution chooses a response and how to assess success.'),
  ('Product: value offered over time', 'Read Product, Product Capability, the version-specific binding and Implementation together as the value column.'),
  ('Project: a particular effort', 'The Northstar repair Project coordinates its Goal and investigation Work. Agent Assignment identifies participation; delegation supplies permission.'),
  ('Incident: response and closure', 'The Incident coordinates response, accountability, communications, recovery and closure. It retains its own state alongside the repair project and investigation.')],
 'learning-loop': [
  ('Record what happened', 'Investigate Northstar’s saved export and source snapshot. Record the Operational Observation and comparison evidence; preserve the reflection for investigation.'),
  ('Propose a lesson with limits', 'Compare adjacent batches where data can change between requests. State the evidence, exclusions, predicted benefit and what would contradict it. This does not establish the cause or remedy of the fixed-snapshot incident.'),
  ('Examine later use', 'Name the lesson version used, or record deliberate non-use. Compare the predicted benefit with the observed result and evidence. Changing policies, profiles or code requires separate authorization.')],
 'figure-01': [
  ('A convenient local patch', 'A new request leads to a convenient patch.'),
  ('Responsibilities become entangled', 'Copied rules or entangled responsibilities make the next change harder.'),
  ('The pressure repeats', 'More investigation and coordination create pressure for another workaround.')],
 'figure-02': [
  ('Structural roles', 'Entity, Value Object and Enum.'),
  ('Behavioral roles', 'Operation, Query, Calculation, Rule, Policy and Workflow.'),
  ('Connective and lifecycle roles', 'Interface, Event and Mapping connect the model. State Machine is the lifecycle role. Together these are the 13 active backend roles.')],
 'figure-03': [
  ('Meaning informs the model', 'Domain definitions inform a project model of concepts, contracts and relationships.'),
  ('Validate and compile selected inputs', 'Validation checks the declarations under selected architecture constraints. The compiler uses selected realizations to construct artifacts.'),
  ('Preserve observations and performed work', 'Source-code artifacts retain bindings to their inputs and selections. Observations of exact targets and records of performed or pending work are preserved in Project State.')],
 'figure-04': [
  ('Use the supplied snapshot', 'Within capacity evaluates requested units against available units in the supplied snapshot.'),
  ('Follow the strict comparison', 'Requested units strictly below available units produce Accept. Equality or a larger request produces Reject.'),
  ('Return without a state change', 'Both branches return the decision. State remains unchanged.')],
 'figure-05': [
  ('Classify capacity is a Calculation', 'Its input type refers to Capacity snapshot, an Entity.'),
  ('The condition calls a Rule', 'The condition calls Within capacity through a typed Rule reference.'),
  ('The result refers to an Enum', 'The result type refers to Capacity decision: Accept or Reject. All three arrows are typed references, not authored graph relationship kinds.')],
 'figure-06': [
  ('Model validation', 'Are the declarations and connections consistent?'),
  ('Artifact verification', 'Does the target match the selected implementation?'),
  ('Behavioral evaluation', 'Does execution produce the expected decisions?'),
  ('Completion review', 'Which required actions have evidence that they were actually performed?')],
 'figure-07': [
  ('Allowing equality changes meaning', 'Revise the acceptance definition, Rule predicate and expected boundary outcomes.'),
  ('Reserving capacity changes responsibility', 'Add the state owner, writes, consistency and failure contracts. Specify coordinated checking and mutation for overlapping requests.'),
  ('Review and evaluate each successor', 'Each successor needs design review, supported construction and its own evaluation evidence.')],
 'figure-08': [
  ('The first session records its work', 'Agent session A is an ephemeral worker with its own session memory. Governed writes preserve work in durable project state.'),
  ('Views select continuing knowledge', 'Context Views select task-relevant information. Ontology Views expose recorded concepts and relationships.'),
  ('A later session recovers context', 'Agent session B uses new views and maintains its own new short-term memory. Durable project state retains the definitions, design selections, artifacts, observations and open work.')],
 'figure-09': [
  ('Authority', 'For a particular subject and version, examine the governing meanings and rules, permissions and scope.'),
  ('Provenance', 'Examine inputs, producing actions and relevant observations.'),
  ('Lifecycle', 'Examine the current state and permitted transitions. These three governance questions are independent.')],
}


def reading_markup(identity, full, minimum):
    data = json.dumps(READINGS[identity], ensure_ascii=False).replace('<', '\\u003c')
    return (f'<div class="diagram-reading" data-diagram-reading data-min-readable-width="{minimum}">'
            '<div class="diagram-reading-controls" role="group" aria-label="Diagram reading mode" hidden>'
            '<button type="button" data-diagram-mode="whole" aria-pressed="true">Whole diagram</button>'
            '<button type="button" data-diagram-mode="guide" aria-pressed="false">Guided reading</button></div>'
            '<div class="diagram-reader" hidden><div class="diagram-step-panel" aria-live="polite" aria-atomic="true">'
            '<p class="diagram-step-title" data-diagram-step-title></p><p data-diagram-step-copy></p></div>'
            '<div class="diagram-step-controls" role="group" aria-label="Reading steps">'
            '<button type="button" data-diagram-prev>← Previous</button>'
            '<span data-diagram-position></span><button type="button" data-diagram-next>Next →</button></div></div>'
            f'<div class="diagram-reading-full">{full}</div>'
            f'<script class="diagram-reading-data" type="application/json">{data}</script></div>')


def apply_diagram_reading(text, page, asset_prefix):
    if page.endswith('governance-lab-reference.html'):
        for identity in READINGS:
            if identity.startswith('figure-'):
                continue
            pattern = rf'(<figure\b[^>]*id="figure-{identity}"[^>]*>)(.*?)(<figcaption>.*?</figure>)'
            def wrap(match):
                original = match[2]
                # The two detailed HTML maps retain every record note and link.
                # Their existing SVG exports provide a compact whole-map view.
                if identity in {'purpose-to-implementation', 'learning-loop'}:
                    description = ' '.join(step[1] for step in READINGS[identity])
                    full = f'<div class="diagram-shell"><img class="diagram-reading-poster" src="assets/{identity}.svg" alt="{escape(description, quote=True)}" loading="lazy"></div>'
                    notes = '<details class="diagram-record-notes"><summary>Detailed record notes</summary>' + original + '</details>'
                else:
                    full, notes = original, ''
                return match[1] + reading_markup(identity, full, 800) + notes + match[3]
            text, count = re.subn(pattern, wrap, text, count=1, flags=re.S)
            assert count == 1, (page, identity)
    elif page.endswith('craft-model.html'):
        def wrap_craft(match):
            identity = 'figure-' + match[1].zfill(2)
            original = match[0]
            scroll = re.search(r'<div class="diagram-scroll"[^>]*>.*?</div>', original, re.S)
            assert scroll
            return original[:scroll.start()] + reading_markup(identity, scroll[0], 720) + original[scroll.end():]
        text, count = re.subn(r'<figure\b[^>]*id="figure-(\d+)"[^>]*>.*?</figure>', wrap_craft, text, flags=re.S)
        assert count == 9, count
        text = re.sub(r'(<p class="diagram-hint"[^>]*>).*?(</p>)', r'\1Use guided reading for a closer explanation.\2', text, flags=re.S)
    if page.endswith('company-brain.html'):
        text = text.replace('data-brain-branch="work" d="M300 314V410"', 'data-brain-branch="work" d="M300 340V410"')
    if any(key in text for key in ['data-diagram-reading', 'class="system-map"', 'class="company-brain-map"', 'class="system-flow"']):
        text = text.replace('</head>', f'<link rel="stylesheet" href="{asset_prefix}diagram-reading.css"><script src="{asset_prefix}diagram-reading.js" defer></script></head>', 1)
    if 'class="system-map"' in text:
        text = text.replace('</head>', f'<link rel="stylesheet" href="{asset_prefix}system-map-canvas.css"><script src="{asset_prefix}system-map-canvas.js" defer></script></head>', 1)
    return text
