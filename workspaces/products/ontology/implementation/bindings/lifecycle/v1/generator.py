#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def render(data: dict) -> str:
    lines = [
        "<!-- Generated from binding.json. Do not edit. -->", "",
        "# Ontology Product lifecycle runtime binding", "",
        f"- Binding: `{data['binding_id']}`",
        f"- Version: `{data['version']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        f"- Product: `{data['product_ref']}`",
        f"- Coordination Context: `{data['coordination_context']['context_ref']}`", "",
        "## Product port", "",
        f"- Trait: `{data['port_contract']['rust_trait']}`",
        f"- Input: {data['port_contract']['input']}",
        f"- Output: {data['port_contract']['output']}",
        f"- Canonical source: {data['port_contract']['canonical_source']}",
        f"- Projection policy: {data['port_contract']['projection_policy']}", "",
        "## Semantic contexts", ""
    ]
    for context in data["semantic_contexts"]:
        lines.append(f"- `{context['context_ref']}` — `{context['ownership']}`")
    lines += ["", "## Runtime implementations", "", "| Runtime | Role | Replaceable | Adopted | Authority effect |", "| --- | --- | --- | --- | --- |"]
    for runtime in data["runtime_implementations"]:
        lines.append(f"| `{runtime['runtime_id']}` | `{runtime['role']}` | `{str(runtime['replaceable']).lower()}` | `{str(runtime['adopted']).lower()}` | `{runtime['authority_effect']}` |")
    lines += ["", "## Product tests", ""]
    lines.extend(f"- {item}" for item in data["product_tests"])
    lines += ["", "## Residue", ""]
    lines.extend(f"- `{item['residue_id']}` — {item['statement']} Treatment: {item['treatment']}" for item in data["residue"])
    lines += ["", "## Claim ceiling", "", data["claim_ceiling"], ""]
    return "\n".join(lines)


def main() -> None:
    data = json.loads((ROOT / "binding.json").read_text(encoding="utf-8"))
    (ROOT / "BINDING.md").write_text(render(data), encoding="utf-8")


if __name__ == "__main__":
    main()
