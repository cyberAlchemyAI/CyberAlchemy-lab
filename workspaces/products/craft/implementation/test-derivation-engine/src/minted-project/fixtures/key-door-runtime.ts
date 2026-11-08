import type { KeyDoorInput, KeyDoorOutput } from "../types.js";

/** Pure EVF harness adapter. This is not an application runtime. */
export function attemptUnlock(input: KeyDoorInput): KeyDoorOutput {
  return input.has_key
    ? { status: "unlocked", door_locked: false }
    : { status: "denied", door_locked: true };
}
