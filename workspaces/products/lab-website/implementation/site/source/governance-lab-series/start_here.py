"""Render the introductory page from the shared Lab and Craft source meanings."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib
import math
import re

from lab_visual_language import bind_model_icons


def render(root, catalog):
    source = root / 'templates/start-here.html.in'
    page = bind_model_icons(source.read_text())

    class ReadingWords(HTMLParser):
        def __init__(self):
            super().__init__()
            self.words = 0
        def handle_data(self, value):
            self.words += len(re.findall(r"\b[\w’'-]+\b", value))

    counter = ReadingWords()
    counter.feed(page.split('<article id="start-here"', 1)[1].split('</article>', 1)[0])
    minutes = math.ceil(counter.words / 220)
    page = page.replace('{{READING_TIME}}', str(minutes))
    assert '{{' not in page, 'Unresolved Start here placeholder'
    terms = {'Definition', 'Authority', 'Provenance', 'Lifecycle Posture', 'Artifact Type',
             'Artifact', 'Intent', 'Intent Resolution', 'Product', 'Product Capability',
             'Project', 'Goal', 'Work', 'Agent Assignment', 'Delegation', 'Agent Session',
             'Context View', 'Ontology View', 'Project State', 'Operational Lesson'}
    metadata = {
        'schema_version': 'editorial-start-here/v1',
        'authority_effect': 'none',
        'entry': 'start-here.html',
        'source': str(source.relative_to(root)),
        'reading_words': counter.words,
        'reading_minutes': minutes,
        'audience': 'Readers new to CyberAlchemy Lab and Craft.',
        'purpose': 'Explain the enduring model and provide routes into existing documentation.',
        'definition_bindings': [{key: entry[key] for key in ['term', 'ref', 'source', 'sha256']}
                                for entry in catalog['definitions'] if entry['term'] in terms],
        'additional_source_bindings': [
            {'source': name, 'sha256': hashlib.sha256((root / name).read_bytes()).hexdigest()}
            for name in ['research/incident-extraction-case.json',
                         '../craft-documentation-proposal/craft-model.md']],
        'preserved_distinctions': [
            'Accepted meaning and scope versus permission to act.',
            'Definition, type contract, instance and derived graph view.',
            'Intent, resolution, product, capability, project, goal, work and assignment.',
            'Durable Project State versus temporary machine instance and session memory.',
            'Craft software design versus Lab records, owner acceptance and deployment.',
            'Calculation and Query versus state-changing Operation.'],
        'scope': 'Introduction only; no operational status page, new contract, admission or integration claim.'}
    return page, metadata
