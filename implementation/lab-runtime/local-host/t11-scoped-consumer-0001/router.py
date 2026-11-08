"""Local, read-only scope route for the 230 selected public candidate bodies.

The route returns exact source bytes to an installed consumer. It does not admit
an artifact, create a repository grant, or claim historical producer execution.
"""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import jsonschema
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


class RouteRefusal(ValueError):
    pass


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def read_binding(root: Path, binding: dict) -> bytes:
    if set(binding) != {"path", "sha256"}:
        raise RouteRefusal("binding shape changed")
    relative = Path(binding["path"])
    if relative.is_absolute() or ".." in relative.parts:
        raise RouteRefusal("binding escapes selected root")
    path = root / relative
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise RouteRefusal("selected input missing or redirected")
    data = path.read_bytes()
    if sha(data) != binding["sha256"]:
        raise RouteRefusal("selected input changed")
    return data


class ScopedConsumer:
    def __init__(self, root: Path, matrix_binding: dict, issuer_key: Ed25519PublicKey,
                 *, clock: Callable[[], datetime] | None = None):
        self.root = root
        self.matrix = json.loads(read_binding(root, matrix_binding))
        routes = self.matrix.get("routes")
        if self.matrix.get("original_member_count") != 363 or not isinstance(routes, list) or len(routes) != 230:
            raise RouteRefusal("selected route inventory incomplete")
        self._routes = {}
        for route in routes:
            member = route.get("member_ref")
            if not isinstance(member, str) or member in self._routes:
                raise RouteRefusal("duplicate or invalid member")
            self._routes[member] = copy.deepcopy(route)
        self.issuer_key = issuer_key
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    @property
    def routes(self) -> dict:
        """An inspection snapshot; mutation cannot change the selected router."""
        return copy.deepcopy(self._routes)

    def consume(
        self,
        member_ref: str,
        scope_ref: str,
        signed_grant: dict,
        consumer: Callable[[bytes, dict], object],
    ) -> object:
        if not callable(consumer):
            raise RouteRefusal("consumer missing")
        route = self._routes.get(member_ref)
        if route is None or route["body_scope_ref"] != scope_ref:
            raise RouteRefusal("member outside selected scope")
        now = self._clock()
        if not isinstance(now, datetime) or now.tzinfo is None:
            raise RouteRefusal("naive clock")
        grant = signed_grant.get("grant")
        signature = signed_grant.get("signature")
        if not isinstance(grant, dict) or not isinstance(signature, str):
            raise RouteRefusal("grant missing")
        if set(grant) != {"schema", "actor", "member_ref", "scope_ref", "body_sha256", "operation", "not_before", "expires_at"}:
            raise RouteRefusal("grant shape changed")
        if grant["schema"] != "lab-local-scoped-body-grant/v1" or not isinstance(grant["actor"], str) or not grant["actor"]:
            raise RouteRefusal("grant identity invalid")
        if (grant["member_ref"], grant["scope_ref"], grant["body_sha256"], grant["operation"]) != (
            member_ref, scope_ref, route["body_binding"]["sha256"], route["operation"]
        ):
            raise RouteRefusal("grant route mismatch")
        try:
            start = datetime.fromisoformat(grant["not_before"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(grant["expires_at"].replace("Z", "+00:00"))
            if start.tzinfo is None or end.tzinfo is None or not start <= now.astimezone(timezone.utc) < end:
                raise RouteRefusal("grant outside lease")
            self.issuer_key.verify(bytes.fromhex(signature), canonical(grant))
        except (ValueError, TypeError, AttributeError, InvalidSignature) as exc:
            raise RouteRefusal("grant signature or lease invalid") from exc
        # All selected bindings are checked before the consumer sees a byte.
        descriptor = json.loads(read_binding(self.root, route["descriptor_binding"]))
        schema = json.loads(read_binding(self.root, route["schema_binding"]))
        body = read_binding(self.root, route["body_binding"])
        document = json.loads(body)
        jsonschema.validate(document, schema)
        if document.get("scope_ref") != scope_ref or document.get("node_id") != route["version_ref"].split("@", 1)[0]:
            raise RouteRefusal("body identity or scope changed")
        if descriptor.get("artifact_type_ref") != route["carrier_ref"]:
            raise RouteRefusal("carrier mismatch")
        return consumer(body, copy.deepcopy(route))
