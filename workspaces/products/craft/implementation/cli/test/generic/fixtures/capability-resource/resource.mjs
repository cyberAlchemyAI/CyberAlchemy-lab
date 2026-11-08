// Explicit installed fixture resource; the selected harness delegates one tool.
// Open Questions: docs/GENERIC-CAPABILITIES.md#open-questions.
import {copyWire} from './copy.mjs';
export function createCapabilityResource(selection) {
  const agent=selection.realization.contract==='agent-run/v1';
  return Object.freeze({
    abi:selection.abi,
    operations:selection.realization.operations,
    capabilities:selection.realization.capabilities,
    ...(agent?{harness_owner:selection.target.model_or_harness}:{}),
    async invoke(request) {
      if(agent&&request.toolBroker)return request.toolBroker.invoke('lookup',copyWire(request.input));
      return copyWire(request.input);
    },
  });
}
