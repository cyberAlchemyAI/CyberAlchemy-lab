import {createHash} from "node:crypto";
import {readFileSync} from "node:fs";
import {isAbsolute, relative, resolve, sep} from "node:path";

import {deepFreeze} from "../../intent-route-resolver/index.mjs";
import {admitDecisionProfile} from "./profile.mjs";
import {markVerifiedDecisionProfile} from "./verified-profile.mjs";

function sha256(value) {
  return createHash("sha256").update(value).digest("hex");
}

export function loadVerifiedDecisionProfile(profilePath, repositoryRoot) {
  let profile;
  try {
    profile = JSON.parse(readFileSync(profilePath, "utf8"));
  } catch (error) {
    return deepFreeze({ok: false, reason_codes: [`profile.load-failed:${error.code ?? error.name}`]});
  }
  const admission = admitDecisionProfile(profile);
  if (!admission.ok) return admission;
  const reasons = [];
  const root = resolve(repositoryRoot);
  const sourceBytes = new Map();
  for (const source of admission.value.provenance) {
    const path = resolve(root, source.path);
    const pathFromRoot = relative(root, path);
    if (pathFromRoot === ".." || pathFromRoot.startsWith(`..${sep}`) || isAbsolute(pathFromRoot)) {
      reasons.push(`profile.provenance-escape:${source.id}`);
      continue;
    }
    try {
      const bytes = readFileSync(path);
      sourceBytes.set(source.id, bytes);
      const actual = sha256(bytes);
      if (actual !== source.sha256) reasons.push(`profile.provenance-drift:${source.id}:${actual}`);
    } catch (error) {
      reasons.push(`profile.provenance-unavailable:${source.id}:${error.code ?? error.name}`);
    }
  }
  if (reasons.length > 0) return deepFreeze({ok: false, reason_codes: reasons.sort()});
  let registry;
  try {
    registry = JSON.parse(sourceBytes.get("route-registry")?.toString("utf8") ?? "null");
  } catch (error) {
    return deepFreeze({ok: false, reason_codes: [`profile.route-registry-invalid:${error.name}`]});
  }
  if (!registry || !Array.isArray(registry.routes)) return deepFreeze({ok: false, reason_codes: ["profile.route-registry-routes.required"]});
  const registryById = new Map(registry.routes.map((route) => [route.route_id, route]));
  const excludedRegistryIds = new Set([registry.entry_route_id, "CA2-ROUTE-AMBIGUOUS"]);
  const requiredIds = registry.routes.map((route) => route.route_id).filter((id) => !excludedRegistryIds.has(id)).sort();
  const policyIds = admission.value.route_policies.map((policy) => policy.route_id).sort();
  if (JSON.stringify(requiredIds) !== JSON.stringify(policyIds)) {
    return deepFreeze({ok: false, reason_codes: [`profile.route-policy-coverage:${requiredIds.join(",")}:${policyIds.join(",")}`]});
  }
  const routes = admission.value.route_policies.map((policy) => {
    const route = registryById.get(policy.route_id);
    return {
      route_id: route.route_id,
      capability_ref: route.capability_ref,
      label: route.objective,
      lifecycle_state: route.lifecycle_state,
      objective_kinds: policy.objective_kinds,
      signals: [...new Set([...(route.match ?? []), ...policy.signal_additions].map((item) => String(item).toLowerCase()))].sort(),
      exclusions: [...new Set([...(route.excludes ?? []), ...policy.exclusion_additions].map((item) => String(item).toLowerCase()))].sort(),
      effect_classes: policy.effect_classes,
      owner_gate_ref: policy.owner_gate_ref,
      provenance_ids: policy.provenance_ids,
    };
  });
  const verified = deepFreeze({...admission.value, routes});
  markVerifiedDecisionProfile(verified);
  return deepFreeze({ok: true, value: verified});
}
