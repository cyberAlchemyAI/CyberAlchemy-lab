"""Closed Work → Source/Evidence Set → retained Package traversal for host embedding."""
from .custody import LOCATOR, RECEIPT
from .exact import decode, encode, require, sha, shape


class RecordResolver:
    def __init__(self, lookup_exact, validate_native_record, current_cut, gate, custody):
        self.lookup, self.validate, self.current_cut = lookup_exact, validate_native_record, current_cut
        self.gate, self.custody = gate, custody

    def reconstruct_work(self, work_ref, expected_cut, *, candidate_inspection=False):
        require(self.current_cut() == expected_cut, "changed-source-cut", exit_code=3)
        operation = "read-candidate-records" if candidate_inspection else "read-project-records"
        self.gate.permit(operation, self.custody.scope, sha(encode({"work_ref": work_ref, "cut": expected_cut})))
        visited, roots = {}, {}
        def follow(ref, expected_kind):
            require(isinstance(ref, str) and "@" in ref and not ref.startswith(("workspace-object:", "lab-retained:", "file:", "http:", "https:")), "unsupported-record-reference", exit_code=4)
            if ref in visited:
                require(visited[ref] in expected_kind, "unexpected-record-kind")
                return
            require(len(visited) < 256, "reference-budget")
            selected = self.lookup(ref)
            shape(selected, ("header", "record", "raw", "effective_state"))
            h, record, raw = selected["header"], selected["record"], selected["raw"]
            shape(h, ("scope_ref", "identity_ref", "version_ref", "carrier_ref", "byte_sha256"))
            require(h["version_ref"] == ref and h["scope_ref"] == self.custody.scope and sha(raw) == h["byte_sha256"] and decode(raw, source=True) == record, "exact-record-mismatch")
            require(selected["effective_state"] in (("admitted-current", "admitted-historical", "local-admitted-current", "local-admitted-historical", "candidate") if candidate_inspection else ("admitted-current", "admitted-historical", "local-admitted-current", "local-admitted-historical")), "unselected-record-standing", exit_code=3)
            require(record.get("kind") in expected_kind, "unexpected-record-kind")
            require(record.get("node_id") == h["identity_ref"], "record-identity-mismatch")
            visited[ref] = record["kind"]
            self.validate(record, h["carrier_ref"])
            p = record["payload"]
            if record["kind"] == "work":
                for output in p["output_refs"]:follow(output, ("source", "evidence-set"))
            elif record["kind"] == "evidence-set":
                for source in p["source_refs"]:follow(source, ("source",))
                for item in p["item_refs"]:
                    loc = LOCATOR.fullmatch(item)
                    require(loc is not None and loc[1] == self.custody.store_id, "unsupported-evidence-reference", exit_code=4)
                    require(loc[2] in roots, "evidence-root-without-source")
                    if loc[3]:
                        manifest, _, _ = self.custody.verify_retained(loc[2])
                        require(loc[3] in manifest["members"], "missing-evidence-member")
            else:
                loc = LOCATOR.fullmatch(p["locator"])
                require(loc is not None and loc[3] is None and p["content_digest"] == "sha256:" + loc[2], "source-retained-binding-mismatch")
                pins = [r for r in p["provenance_refs"] if RECEIPT.fullmatch(r)]
                require(len(pins) == 1, "source-receipt-pin-required")
                observation = self.custody.reconstruct(p["locator"], pins[0])
                roots[loc[2]] = observation
        follow(work_ref, ("work",))
        require(bool(roots), "reconstruction-incomplete", "Work has no completed resolvable retained result", 3)
        require(self.current_cut() == expected_cut, "changed-source-cut", exit_code=3)
        self.gate.permit(operation, self.custody.scope, sha(encode({"work_ref": work_ref, "cut": expected_cut})))
        return {"work_ref": work_ref, "source_cut": expected_cut, "packages": list(roots.values()),
                "candidate_inspection": candidate_inspection, "governing_standing_changed": False,
                "restored_session_memory": False, "authority_effect": "none"}
