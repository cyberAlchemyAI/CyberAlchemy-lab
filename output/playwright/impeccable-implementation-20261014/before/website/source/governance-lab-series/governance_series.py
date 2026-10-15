"""Shared incident meanings and examples for the canonical governance guide."""
from html import escape
import json
from lab_visual_language import bind_model_icons


PARTS = [
    {'key': 'authority', 'number': 1, 'topic': 'Authority',
     'path': 'governance-authority.html', 'title': 'What governs meaning and action?',
     'deck': 'How accepted definitions, record requirements and permissions give a task its meaning and limits.',
     'preview': 'Inspect an accepted definition, its scope and the separate permission to act.',
     'essay_title': 'Authority begins with meaning',
     'terms': ['Definition', 'Authority', 'Authority Claim', 'Authority Boundary', 'Artifact Type',
               'Relation Kind', 'Policy', 'Constitution', 'Agent Assignment', 'Delegation',
               'Governance-Axis Independence Invariant', 'Incident', 'Failure Occurrence']},
    {'key': 'provenance', 'number': 2, 'topic': 'Provenance',
     'path': 'governance-provenance.html', 'title': 'Where did this come from?',
     'deck': 'How sources, methods and recorded results make a conclusion inspectable.',
     'preview': 'Follow a result to its sources and see what the evidence supports.',
     'essay_title': 'Following the evidence',
     'terms': ['Source', 'Provenance', 'Evidence', 'Evidence Set', 'Measurement Method',
               'Measurement Result', 'Finding', 'Operational Observation', 'Observation', 'Incident', 'Failure Occurrence', 'Failure Assessment']},
    {'key': 'lifecycle', 'number': 3, 'topic': 'Lifecycle',
     'path': 'governance-lifecycle.html', 'title': 'What can change from here?',
     'deck': 'How independent states, authorized changes and current views let a project evolve through time.',
     'preview': 'Compare independent states and follow the rules for each kind of change.',
     'essay_title': 'Changing a governed system',
     'terms': ['Definition', 'Governance-Axis Independence Invariant', 'Semantic Epoch', 'Representation Revision', 'Derived Refresh', 'Decision Bundle',
               'Admission Transaction', 'Project State', 'Context View', 'Ontology View',
               'Agent Instance', 'Agent Session', 'Session Memory', 'Challenge Contract', 'Challenge Event', 'Incident', 'Failure Assessment']},
]


LENS_ICONS = {
    # Shield and cycle match the system map's original 24-unit line icons.
    'authority': '<path d="m12 2 9 4v6c0 5-5 8-9 10-4-2-9-5-9-10V6Zm-4 10 3 3 5-6"/>',
    'provenance': '<path d="M6.5 4H16a4 4 0 0 1 0 8h-1.5M9.5 12H8a4 4 0 0 0 0 8h9.5"/><circle cx="4" cy="4" r="2.5"/><circle cx="12" cy="12" r="2.5"/><circle cx="20" cy="20" r="2.5"/>',
    'lifecycle': '<path d="M20 8a8 8 0 0 0-14-3L3 8m0-5v5h5M4 16a8 8 0 0 0 14 3l3-3m0 5v-5h-5"/>',
}


def lens_icon(lens):
    return (f'<svg class="governance-lens-icon" data-lens-icon="{lens}" '
            'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
            f'aria-hidden="true" focusable="false">{LENS_ICONS[lens]}</svg>')


def incident_bindings(root):
    case = json.loads((root / 'research/incident-extraction-case.json').read_text())
    export, agent, ticket = case['export'], case['investigation'], case['ticket_presentation']
    return {key: escape(str(value)) for key, value in {
        'CASE_TITLE': case['incident']['title'], 'CASE_TRIGGER': case['incident']['trigger'],
        'CASE_TICKET_ID': ticket['ticket_id'], 'CASE_REPORTED_VIA': ticket['reported_via'],
        'CASE_OPENED_AT': ticket['opened_at'], 'CASE_UPDATED_AT': ticket['updated_at'],
        'CASE_CUSTOMER_REPORT': ticket['customer_report'],
        'CASE_OWNER': case['incident']['owner'], 'CASE_ACCOUNT': export['account'],
        'CASE_FILTERS': export['filters'], 'CASE_SNAPSHOT': export['snapshot'], 'CASE_OUTPUT': export['output'],
        'CASE_RUN': export['run'], 'CASE_SERVICE_REVISION': export['service_revision'],
        'CASE_REQUIRED_COUNT': format(export['required_count'], ','),
        'CASE_OUTPUT_ROW_COUNT': format(export['output_row_count'], ','),
        'CASE_MISSING_COUNT': format(export['missing_required_count'], ','),
        'CASE_DEFINITION_VERSION': export['definition_version'], 'CASE_SESSION': agent['session'],
        'CASE_METHOD_VERSION': agent['method_version'], 'CASE_FIX_REVISION': agent['proposed_fix_revision'],
        'CASE_OBSERVATION_VERSION': agent['observation_version'],
        'CASE_VIEW_VERSION': agent['task_view_version'],
    }.items()}


def bind_incident(root, content):
    content = bind_model_icons(content)
    for lens in LENS_ICONS:
        content = content.replace('{{' + lens.upper() + '_ICON}}', lens_icon(lens))
    for key, value in incident_bindings(root).items():
        content = content.replace('{{' + key + '}}', value)
    return content


def incident_context(root, prefix):
    return bind_incident(root, (root / 'templates/incident-case.html.in').read_text().replace('{{CASE_PREFIX}}', prefix))


def incident_lens_summary(root, prefix):
    return bind_incident(root, (root / 'templates/incident-lens-summary.html.in').read_text().replace('{{SUMMARY_PREFIX}}', prefix))


def export_completeness_definition(root, prefix):
    """Keep the example's meaning and Lab voice structure shared across pages."""
    return bind_incident(root, (root / 'templates/export-completeness-definition.html.in').read_text().replace(
        '{{DEFINITION_PREFIX}}', prefix))


def lens_definition_and_example(root, lens, prefix):
    """Use the same reader definitions and business records in both editions."""
    example_file = 'authority-incident-example' if lens == 'authority' else lens + '-example'
    bridge_copy = {
        'authority': ('Use the definition in the investigation',
                      'The definition above sets the completeness criterion. The investigation below shows how the agent finds that rule, identifies its job and checks permission before applying it.'),
        'provenance': ('Build the trail described by the definition',
                       'The definition above describes what a provenance trail preserves. The investigation below supplies those sources, operations and responsibilities for the comparison of snapshot S1 and output E12.'),
        'lifecycle': ('Apply the structure to each incident subject',
                      'The definition above explains how states and changes are governed. The example below applies that structure to four separate subjects in the same incident, each with its own conditions for change.'),
    }
    title, explanation = bridge_copy[lens]
    bridge = (root / 'templates/definition-application-bridge.html.in').read_text()
    for key, value in {'BRIDGE_LENS': lens, 'BRIDGE_TITLE': title, 'BRIDGE_TEXT': explanation}.items():
        bridge = bridge.replace('{{' + key + '}}', escape(value))
    content = {lens.upper() + '_EXAMPLE': bridge + bind_incident(root,
        (root / f'templates/{example_file}.html.in').read_text().replace('{{EXAMPLE_PREFIX}}', prefix + '-example'))}
    if lens != 'authority':
        content[lens.upper() + '_DEFINITION'] = bind_incident(root,
            (root / f'templates/{lens}-definition.html.in').read_text().replace('{{DEFINITION_PREFIX}}', prefix + '-definition'))
    return content

