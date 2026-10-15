# Private fact read scope candidate

Status: authored; not frozen, tested, integrated or qualified.

## Reason for the successor

The recorded original-source profile attributes most cold-opening and guard cost to repeated verification of source paths and packages. A separate byte-stamp probe found no repeated immutable byte objects in its selected record set. Its digest helper therefore remains unintegrated.

This helper copies already verified exact facts for one synchronous pure calculation. It does not replace the original reader, model, eligibility implementation or parent guard callback.

## Boundary and invariants

1. Select the actual SignedSources class, matching original eligibility namespace, exact source-owning channel and original package checker/pin pairs through private host code.
2. Call full original source, package and channel guards before copying and full source/channel guards after copying.
3. Preserve the original ExactSources current_guard and parent callback. The new copied ExactSources receives a local byte/schema/scope/witness guard.
4. Keep original get/resolve validation on every copied reference, including original bytes, schema, identity, semantic kind, version witness, privacy and scope.
5. Registered consumers may use the copied source guard and package selection during this pure scope. Actual host policy files, revocation, Actor, permissions, time bounds and budgets must still be checked on every permission call. No permission is cached by the helper.
6. Remove the scope before full original source, package and channel exit guards. Failure prevents a derived result from reaching the next writer.
7. A copied source cannot serve facts after exit. Other threads receive no borrowed scope. Nested API dispatch or durable effects must be refused by the consumer while a scope exists.
8. Return to full original checks outside this scope. Do not renew the fixed Assignment period, extend a Context deadline, resurrect a Session or reuse expired Agent resources.

## Intended integration

Use immutable Context and API successors. Context generation and Session opening preflight are pure calculations; managed-object persistence and Session resource creation occur after successful exit guards. Host permission methods in the successors retain their live policy checks and use this helper solely for source/package selection during those calculations. Existing frozen Context4/API30 sources remain unchanged.

## Required validation before use

Actual signed source tests must cover exact copied facts, callback preservation, schema/witness/header/byte mutation, source corruption at exit, copied-source closure, foreign channel/source, source/package drift, host revocation within a calculation, fixed deadlines, cross-thread isolation and refusal of nested durable dispatch. Preserve all original Context and API assertion methods and run their complete suites on the integrated successors. A helper test or a profiler result cannot qualify the complete Agent lifecycle.
