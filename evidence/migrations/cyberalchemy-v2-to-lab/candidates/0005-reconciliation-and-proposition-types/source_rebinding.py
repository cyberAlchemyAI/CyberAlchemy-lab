"""Narrow source binding for D53, whose surrounding section now contains other definitions."""
import hashlib
import re
from common import ROOT, SOURCE, L0, L1, load, sha, module, need


def payload_sha(text):
    return hashlib.sha256((text.strip() + "\n").encode()).hexdigest()


def build(path=None):
    path = SOURCE / "authority/definitions/DEFINITIONS.md" if path is None else path
    text = path.read_text()
    heading = "## CAV2-D53: Axiom"
    need(text.count(heading + "\n") == 1, "Axiom heading is ambiguous")
    start = text.index(heading + "\n")
    following = re.search(r"(?m)^#{2,3} CAV2-D\d+: .+$", text[start + len(heading):])
    need(following is not None, "Axiom boundary missing")
    section = text[start:start + len(heading) + following.start()]
    definition = load(L1 / "definitions/axiom/v1/definition.json")
    voices = definition["voices"]
    expected = {
        "Normative Definition": voices["scientific_formal"]["normative_statement"].split("Bound source-semantic basis:\n\n", 1)[1],
        "Formal Interpretation": voices["scientific_formal"]["formal_expression"],
        "Operational Interpretation": definition["scope"]["applicability"],
        "Plain-Language Intuition": voices["plain_language"]["explanation"],
        "Domain-Context Voice": voices["domain_context"]["explanation"].split("Source context retained for reconstruction:\n\n", 1)[1],
        "Boundary": definition["boundaries"][0],
    }
    bindings = []
    for name, original in expected.items():
        match = re.search(r"(?ms)^### " + re.escape(name) + r"\n(.*?)(?=^#{2,3} |\Z)", section)
        need(match is not None, "Missing Axiom subsection: " + name)
        need(payload_sha(match.group(1)) == payload_sha(original), "Axiom meaning changed: " + name)
        bindings.append({"selector": heading + " / ### " + name,
                         "payload_sha256": payload_sha(original), "comparison": "exact-content-after-outer-whitespace-trim"})
    helper = module(L0 / "author.py", "d53_historical_section")
    return {"schema_version": "cal-d53-source-selector-rebinding/v1", "authority_effect": "none",
            "source_root": str(SOURCE), "source_path": "authority/definitions/DEFINITIONS.md", "source_file_sha256": sha(path),
            "definition_path": str((L1 / "definitions/axiom/v1/definition.json").relative_to(ROOT.parents[4])),
            "historical_section_sha256": definition["source_refs"][0]["content_sha256"],
            "current_historical_selector_sha256": hashlib.sha256(helper.markdown_h2_section(path, heading)).hexdigest(),
            "selected_subsections": bindings,
            "disposition": "Use these six unchanged meaning-bearing subsections for the new Axiom carrier; retain full historical section drift explicitly.",
            "remaining_residue": {"owner": "role:definition-owner",
                "issue": "Resilience definitions were inserted between the Axiom boundary and its later questions/consumers. The whole historical D53 selector is not source-current.",
                "scope_limit": "This batch does not repair the legacy document, re-admit the old Definition, or establish currentness of its later questions and consumer list."}}
