"""Inert C05 route-plan join. This module never loads callables or invokes effects.

The caller must independently select/authenticate registry bytes, private plan,
principal, scope, source cut, bindings and current grants. A PASS here is only a
closed structural join and cannot authorize a producer or workflow transition.
"""
import hashlib
import json


class PlanRefusal(ValueError):
    pass


def _need(ok, code):
    if not ok:
        raise PlanRefusal(code)


def _closed(value, keys, code):
    _need(type(value) is dict and set(value) == set(keys), code)


def _name(value):
    return type(value) is str and 0 < len(value) <= 256 and "\x00" not in value


def _digest(value):
    return type(value) is str and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def _binding(value, code):
    _closed(value, ("path", "sha256"), code)
    path = value["path"]
    _need(_name(path) and not path.startswith("/") and "\\" not in path and
          all(part not in ("", ".", "..") for part in path.split("/")) and
          _digest(value["sha256"]), code)


def _canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                          allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise PlanRefusal("PLAN_ENCODING") from exc


def _plain(value):
    """Refuse objects before their comparison, iteration or JSON hooks can run."""
    remaining = [10000]

    def walk(item, depth):
        remaining[0] -= 1
        if remaining[0] < 0 or depth > 16:
            return False
        if type(item) is dict:
            return len(item) <= 1024 and all(type(key) is str and len(key) <= 256 and
                                              walk(child, depth + 1) for key, child in item.items())
        if type(item) is list:
            return len(item) <= 1024 and all(walk(child, depth + 1) for child in item)
        if type(item) is str:
            return len(item) <= 4096
        if type(item) is int:
            return -(1 << 63) <= item <= (1 << 63) - 1
        return type(item) is bool or item is None

    return walk(value, 0)


PLAN_KEYS = ("schema_version", "principal_ref", "scope_ref", "source_cut",
             "registry_sha256", "authority_effect", "routes")
ROUTE_KEYS = ("transition_ref", "definition_binding", "allowed_output_carriers",
              "producer_binding", "producer_entrypoint", "producer_instance_contract",
              "resolver_binding", "resolver_entrypoint", "invocation_ref",
              "invocation_input_binding", "output_slot_ref", "output_scope_ref",
              "output_custody", "scope_contract_binding", "producer_control_binding",
              "authority_stage")
REGISTRY_KEYS = ("workflow_type_ref", "definition_binding", "output_carriers",
                 "original_producer_path", "family")


def validate(plan, registry, *, expected_registry_sha256, principal_ref, scope_ref, source_cut):
    """Return an inert summary only after a complete exact 28-route join."""
    _need(_plain(plan) and _plain(registry), "PLAN_DATA")
    _closed(plan, PLAN_KEYS, "PLAN_SHAPE")
    _need(plan["schema_version"] == "lab-private-workflow-output-route-plan/v5-inert-candidate"
          and plan["authority_effect"] == "none", "PLAN_PROFILE")
    _need(all(_name(x) for x in (principal_ref, scope_ref, source_cut)) and
          plan["principal_ref"] == principal_ref and plan["scope_ref"] == scope_ref and
          plan["source_cut"] == source_cut, "PLAN_SCOPE_CUT")
    _need(type(registry) is dict and len(registry) == 28 and
          all(_name(ref) for ref in registry), "REGISTRY_COVERAGE")
    registry_sha256 = hashlib.sha256(_canonical(registry)).hexdigest()
    _need(_digest(expected_registry_sha256) and
          registry_sha256 == expected_registry_sha256 == plan["registry_sha256"],
          "REGISTRY_ORIGINAL")
    _need(type(plan["routes"]) is dict and set(plan["routes"]) == set(registry),
          "ROUTE_COVERAGE")
    slots, invocations = set(), set()
    for ref, original in registry.items():
        _closed(original, REGISTRY_KEYS, "REGISTRY_ROW")
        _binding(original["definition_binding"], "REGISTRY_DEFINITION")
        _need(type(original["output_carriers"]) is list and original["output_carriers"] and
              len(original["output_carriers"]) == len(set(original["output_carriers"])) and
              all(_name(c) for c in original["output_carriers"]) and
              _name(original["original_producer_path"]) and
              _name(original["workflow_type_ref"]) and _name(original["family"]), "REGISTRY_ROW")
        route = plan["routes"][ref]
        _closed(route, ROUTE_KEYS, "ROUTE_SHAPE")
        _need(route["transition_ref"] == ref and
              route["definition_binding"] == original["definition_binding"], "ROUTE_DEFINITION")
        _need(type(route["allowed_output_carriers"]) is list and
              route["allowed_output_carriers"] == original["output_carriers"], "ROUTE_CARRIERS")
        for key in ("producer_binding", "resolver_binding", "invocation_input_binding",
                    "scope_contract_binding", "producer_control_binding"):
            _binding(route[key], "ROUTE_BINDING")
        _need(route["producer_binding"]["path"] == original["original_producer_path"],
              "ROUTE_PRODUCER_ORIGIN")
        for key in ("producer_entrypoint", "producer_instance_contract", "resolver_entrypoint",
                    "invocation_ref", "output_slot_ref", "output_scope_ref", "output_custody"):
            _need(_name(route[key]), "ROUTE_IDENTITY")
        _need(route["authority_stage"] in ("technical-contract", "authorized-candidate-effect",
                                                  "actual-owner-effect"), "ROUTE_STAGE")
        _need(route["output_slot_ref"] not in slots and route["invocation_ref"] not in invocations,
              "ROUTE_DUPLICATE")
        slots.add(route["output_slot_ref"])
        invocations.add(route["invocation_ref"])
    return {"schema_version": "lab-inert-route-validation/v1", "registry_sha256": registry_sha256,
            "route_count": 28, "authority_effect": "none", "producer_invocations": 0}
