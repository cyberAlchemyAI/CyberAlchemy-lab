/** Binding descriptors are inert metadata, not nominal scalar brands, target
 * existence evidence, repository readers or runtime target dependencies. */
export function renderPythonReferenceSupport(): string {
  return `from __future__ import annotations
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class FieldBinding:
    owner: str
    field: str
    kind: Literal["identity-reference", "field-projection"]
    target: str
    projection: tuple[str, ...]
`;
}
