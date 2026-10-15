const APPROVAL_REQUESTS = new Set([
  "item/commandExecution/requestApproval",
  "item/fileChange/requestApproval",
  "item/permissions/requestApproval",
]);

export function isApprovalRequest(method) {
  return APPROVAL_REQUESTS.has(method);
}

export function defaultApprovalResult(method) {
  if (method === "item/permissions/requestApproval") return {permissions: {}, scope: "turn"};
  return {decision: "decline"};
}

export function declineElicitationResult() {
  return {action: "decline", content: null, _meta: null};
}
