"""Cold O05 generator and local-vocabulary evidence route; no generator execution."""

from collections import Counter
import json
from pathlib import PurePosixPath
from jsonschema import Draft202012Validator


PACKAGE = "implementation/lab-ontology/candidates/v1/migration/candidate/0001/"
O05 = "implementation/lab-ontology/candidates/v1/receipts/O05/0001.json"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def record(read, root, binding):
    return json.loads(read(root, **binding))


def one(rows, path):
    found = [row for row in rows if row["path"] == path]
    need(len(found) == 1, "O05 selected file absent or ambiguous: " + path)
    return found[0]


def package_file(read, root, manifest, receipt, relative):
    pure = PurePosixPath(relative)
    need(relative == pure.as_posix() and not pure.is_absolute() and
         all(part not in ("", ".", "..") for part in pure.parts), "O05 unsafe package path")
    row = one(manifest["files"], relative)
    path = PACKAGE + relative
    need(one(receipt["files"], path)["sha256"] == row["sha256"], "O05 manifest/receipt file differs")
    return record(read, root, {"path": path, "sha256": row["sha256"]})


def observe(read, root, row22, row23, o05_binding):
    need(o05_binding["path"] == O05 and o05_binding in row22["original_evidence_bindings"] and
         o05_binding in row23["original_evidence_bindings"], "O05 evidence selection differs")
    scope_binding = one(row22["original_target_bindings"],
                        "implementation/lab-ontology/candidates/v1/migration/adapters/build-scope.json")
    profile_binding = one(row23["original_target_bindings"],
                          "implementation/lab-ontology/candidates/v1/migration/adapters/translation-profile.json")
    need(one(row22["original_target_bindings"], profile_binding["path"]) == profile_binding,
         "O05 generator/profile target differs")
    scope, profile, receipt = (record(read, root, binding)
                               for binding in (scope_binding, profile_binding, o05_binding))
    need(len({x["path"] for x in receipt["files"]}) == len(receipt["files"]) and
         all(one(receipt["files"], x["path"])["sha256"] == x["sha256"]
             for x in row22["original_target_bindings"] + row23["original_target_bindings"]) and
         receipt["result"] == "PASS" and receipt["task"] == "O05" and
         receipt["completion_mode"] == "candidate-implementation-verified" and
         receipt["authority_effect"] == "none" and receipt["actual_owner_outcome"] is None and
         receipt["source_bodies_copied"] == receipt["source_effects_applied"] ==
         receipt["global_typed_relations_created"] == receipt["domain_instances_conformed"] == 0,
         "O05 receipt source, validation or effect differs")
    manifest_binding = receipt["manifest_binding"]
    need(manifest_binding["path"] == PACKAGE + "manifest.json" and
         one(receipt["files"], manifest_binding["path"])["sha256"] == manifest_binding["sha256"],
         "O05 selected manifest differs")
    manifest = record(read, root, manifest_binding)
    need(len({x["path"] for x in manifest["files"]}) == len(manifest["files"]) == 224 and
         manifest["profile_binding"] == scope["profile_binding"] == profile_binding and
         manifest["source_selection_binding"] == scope["selection_binding"] ==
         profile["source_selection_binding"] and
         manifest["visibility"] == "private-candidate-metadata" and
         manifest["authority_effect"] == "none" and manifest["actual_owner_outcome"] is None and
         manifest["counts"] == receipt["counts"] ==
         {"generated-output": 1, "ontology-edge": 50, "ontology-node": 38, "source": 131},
         "O05 manifest/profile/selection/count differs")
    core = package_file(read, root, manifest, receipt, "core.json")
    reproduction = package_file(read, root, manifest, receipt, "reproducibility.json")
    generator_binding = one(row22["original_target_bindings"],
                            "implementation/lab-ontology/candidates/v1/migration/adapters/build.py")
    need(core["scope_binding"] == scope_binding and core["profile_binding"] == profile_binding and
         core["selection_binding"] == scope["selection_binding"] and
         all(one(core["code_bindings"], item["path"])["sha256"] == item["sha256"]
             for item in row22["original_target_bindings"] if item["path"].endswith(".py")) and
         reproduction["generator_binding"] == generator_binding and
         reproduction["profile_binding"] == profile_binding,
         "O05 generator source bindings differ")
    need(manifest["core_sha256"] == receipt["observations"]["repeated_build"]["core_sha256"] ==
         receipt["observations"]["warm_validation"]["core_sha256"] ==
         reproduction["core_sha256"] and
         receipt["observations"]["repeated_build"]["result"] == "PASS" and
         receipt["observations"]["cold_reconstruction"]["result"] == "PASS" and
         receipt["observations"]["repeated_build"]["same_original_bytes"] is True and
         receipt["observations"]["cold_reconstruction"]["same_original_bytes"] is True and
         receipt["observations"]["repeated_build"]["files_compared"] ==
         receipt["observations"]["cold_reconstruction"]["files_compared"] == 225 and
         reproduction["independent_rebuild_verified"] is False and
         core["source_bodies_copied"] == core["source_effects_applied"] ==
         core["global_typed_relations_created"] == core["domain_instances_conformed"] == 0,
         "O05 repeated/cold evidence or source-effect posture differs")
    output_rows = [item for item in manifest["files"]
                   if item["path"].startswith("records/generated-output/")]
    need(len(output_rows) == 1 and profile["output_carrier"]["carrier_ref"] ==
         "cal.artifact-type.generated-output/v2", "O05 generated-output selection differs")
    output_binding = {"path": PACKAGE + output_rows[0]["path"],
                      "sha256": output_rows[0]["sha256"]}
    output = package_file(read, root, manifest, receipt, output_rows[0]["path"])
    output_schema_binding = profile["output_carrier"]["schema_binding"]
    output_schema = record(read, root, output_schema_binding)
    Draft202012Validator.check_schema(output_schema)
    Draft202012Validator(output_schema).validate(output)
    need(output["kind"] == "generated-output" and
         output["lifecycle_state"] == "candidate" and
         output["authority_effect"] == "none" and
         output["payload"]["generator_ref"] ==
         generator_binding["path"] + "#sha256=" + generator_binding["sha256"] and
         output["payload"]["output_digest"] == "sha256:" + manifest["core_sha256"] and
         output["payload"]["reproducibility_receipt_ref"] ==
         PACKAGE + "reproducibility.json" and
         len(output["payload"]["input_refs"]) == manifest["counts"]["source"],
         "O05 generated-output contract or generator differs")
    need(scope["source_execution_allowed"] is False and
         scope["source_body_copy_allowed"] is False and
         scope["source_mutation_allowed"] is False and
         scope["private_body_export_allowed"] is False and
         profile["authority_effect"] == "none" and profile["actual_owner_outcome"] is None and
         profile["namespace"] == "lab.legacy-source-assertion.cav2-product-thesis" and
         profile["local_predicate_prefix"] == "legacy-product-local-predicate:" and
         len(profile["predicates"]) == len(set(profile["predicates"])) == 20 and
         profile["confidence"]["allowed_levels"] == ["not-assessed"] and
         profile["confidence"]["evidence_level"] ==
         profile["confidence"]["commitment_level"] == "not-assessed" and
         "global-typed-relation" in profile["forbidden_collapse"],
         "O05 local vocabulary or source-only scope differs")
    edge_rows = [item for item in manifest["files"] if item["path"].startswith("records/ontology-edge/")]
    need(len(edge_rows) == 50, "O05 edge inventory differs")
    directions = Counter()
    predicates = set()
    for item in edge_rows:
        edge = package_file(read, root, manifest, receipt, item["path"])
        payload = edge["payload"]
        directions[payload["direction"]] += 1
        predicates.add(payload["relation_type_ref"])
        need(edge["kind"] == "ontology-edge" and edge["record_state"] == "candidate" and
             edge["authority_effect"] == "none" and
             payload["edge_mode"] == "local-interpretation" and
             payload["global_typed_relation_binding"] is None and
             payload["replay_source"] is False and
             payload["local_interpretation"]["local_scope"] == profile["namespace"] and
             "global-typed-relation" in payload["forbidden_collapse"],
             "O05 edge acquired global/authority meaning")
    expected_predicates = {profile["local_predicate_prefix"] + value + "/v1-candidate"
                           for value in profile["predicates"]}
    need(directions == {"directed": 49, "symmetric": 1} and predicates == expected_predicates,
         "O05 local edge direction or predicate vocabulary differs")
    return {
        "schema_version": "lab-T10-O05-retained-local-route/v2",
        "generator": {"scope_binding": scope_binding, "code_binding": generator_binding,
                      "profile_binding": profile_binding, "manifest_binding": manifest_binding,
                      "output_schema_binding": output_schema_binding,
                      "output_record_binding": output_binding,
                      "output_carrier_ref": profile["output_carrier"]["carrier_ref"],
                      "reproduction_binding": {"path": PACKAGE + "reproducibility.json",
                                               "sha256": one(manifest["files"], "reproducibility.json")["sha256"]},
                      "core_sha256": manifest["core_sha256"], "repeated_build": "PASS",
                      "cold_reconstruction": "PASS"},
        "vocabulary": {"profile_binding": profile_binding,
                       "namespace": profile["namespace"], "predicate_count": 20,
                       "edge_directions": dict(sorted(directions.items())),
                       "global_typed_relations_created": 0,
                       "confidence_level": "not-assessed"},
        "source_bodies_copied": 0, "source_effects_applied": 0,
        "authority_effect": "none", "generator_rerun_this_run": False,
    }
