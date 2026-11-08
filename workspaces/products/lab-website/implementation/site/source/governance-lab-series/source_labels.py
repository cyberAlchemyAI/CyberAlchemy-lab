"""Readable source citations for the article; source records remain unchanged."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
SOURCE_TITLES = {
    'authority/governance/candidates/0001-three-lens-module/MODULE.md': 'Proposed governance module',
    'docs/decisions/0074-governance-transaction-surface-admission/DECISION.md': 'Governance transaction approval',
    'docs/decisions/0075-lab-operational-runtime-v1-admission/DECISION.md': 'Local runtime implementation approval',
    'implementation/lab-runtime/v2/REVIEW.md': 'Review of the proposed source-selection update',
    'implementation/lab-runtime/v1/README.md': 'Local runtime implementation overview',
    'implementation/lab-runtime/ADMISSION.md': 'Local runtime admission scope',
    'ontology-lifecycle/README.md': 'Ontology lifecycle library overview',
    'implementation/bindings/ontology-product-event-runtime/v2/README.md': 'Product event runtime binding',
    'implementation/bindings/ontology-product-event-runtime/v4/README.md': 'Ontology migration and update prototype',
    'authority/project-state-transitions/current.json': 'Committed Project State',
    'implementation/lab-runtime/v1/lab_runtime/store.py': 'Local runtime: storage, approvals and replay',
    'implementation/lab-runtime/v1/lab_runtime/governance.py': 'Local runtime: governed consequences',
    'implementation/lab-runtime/v1/lab_runtime/session.py': 'Local runtime: temporary agent sessions',
    'authority/artifact-types/coordination-context/v2/schema.json': 'Coordination Context v2 schema',
    'authority/ontology-integration/candidates/0003-definition-complete-runtime-integration/integrated-model.json': 'Integrated Lab model record',
    'authority/artifact-types/candidates/0012-definition-complete-carrier-materialization/noncarrier-realizations.json': 'Definition realization contracts',
    'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/source-and-formalization-coverage.json': 'Source and formalization coverage',
    'implementation/lab-runtime/v2/profile.json': 'Proposed selection of accepted records',
    'implementation/lab-runtime/v2/receipts/validation.json': 'Validation record for the proposed update',
    'ontology-lifecycle/runtime/src/lib.rs': 'Ontology lifecycle runtime implementation',
}

ADMISSION_TITLES = {
    '0013': 'Foundational model admission',
    '0015': 'Definition contract admission',
    '0018': 'Definition and initial context promotion',
    '0021': 'Context artifact type promotion',
    '0026': 'Reference normalization definition promotion',
    '0027': 'Normalized context artifact type promotion',
    '0028': 'Craft foundation admission',
    '0029': 'Semantic foundation admission',
    '0030': 'Identity artifact types admission',
    '0043': 'Canonical package organization admission',
    '0053': 'Complete definition intake admission',
    '0054': 'Intent contract admission',
    '0057': 'Product identity successor admission',
    '0058': 'Product Thesis contract admission',
    '0059': 'Product Capability contract admission',
    '0060': 'Capability Realization Binding contract admission',
    '0062': 'Research Inquiry contract admission',
    '0063': 'Research Run contract admission',
    '0064': 'Typed Connection Extension Rule admission',
    '0065': 'Integrated definition model admission',
    '0066': 'Definition specialization and resolution admission',
    '0067': 'Coordination Context successor admission',
    '0068': 'Artifact type registry admission',
    '0070': 'Complete Lab definition model admission',
    '0072': 'Initial Project State admission',
    '0074A': 'Governance record types admission',
    '0074B': 'Admission Transaction definition admission',
    '0074C': 'Governance relation contracts admission',
    '0075': 'Local runtime implementation admission',
}


def admission_title(reference):
    """Name the recorded approval; retain its identifier in the source record."""
    match = re.match(r'CAL-DECISION-(\d{4}[A-Z]?)-', reference)
    if match and match.group(1) in ADMISSION_TITLES:
        return ADMISSION_TITLES[match.group(1)]
    return 'Recorded admission'


def source_title(snapshot):
    """Use a captured document heading, with explicit titles for code and records."""
    relative = str(snapshot).removeprefix('research/sources/')
    if relative in SOURCE_TITLES:
        return SOURCE_TITLES[relative]
    path = ROOT / snapshot
    if path.suffix == '.md' and path.is_file():
        heading = re.search(r'^#\s+(.+)$', path.read_text(), re.M)
        if heading:
            return heading.group(1).strip().strip('`')
    return citation_name(relative)


def citation_name(path):
    names = {
        '.craft/ledger.yml': 'Craft ledger',
        '.craft/index.json': 'Craft index',
        'CANONICAL-KINDS.md': 'Canonical kinds',
        'AUTHORITY-MODEL.md': 'Authority model',
        'promotion-policy.md': 'Promotion policy',
    }
    return names.get(path, names.get(Path(path).name,
        Path(path).stem.replace('-', ' ').replace('_', ' ').capitalize()))


# Match file citations, not artifact identities, schema selectors or URLs.
FILE_CITATION = re.compile(
    r'(?<![\w:/.-])(?:\.{1,2}/|[A-Za-z0-9_.-]+/)+'
    r'[A-Za-z0-9_.-]+\.(?:md|jsonl?|py|rs|sh|ya?ml|toml|txt|html)\b'
)
MARKDOWN_CITATION = re.compile(r'\[([^\]]+)\]\(([^\s)]+)\)')


def display_text(value):
    """Format repository citations without changing the captured original."""
    def named_link(match):
        label, target = match.groups()
        if FILE_CITATION.fullmatch(target):
            return citation_name(target) if FILE_CITATION.fullmatch(label) else label
        return match.group(0)
    text = MARKDOWN_CITATION.sub(named_link, str(value))
    return FILE_CITATION.sub(lambda match: citation_name(match.group(0)), text)


def display_value(value):
    if isinstance(value, str):
        return display_text(value)
    if isinstance(value, list):
        return [display_value(v) for v in value]
    if isinstance(value, dict):
        return {k: display_value(v) for k, v in value.items()}
    return value
