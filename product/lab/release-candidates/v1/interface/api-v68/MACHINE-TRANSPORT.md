# Machine transport integration candidate

Status: authored successor; source and profile are not frozen. No execution or
qualification is claimed.

The trusted host selects an actual live Agent Session. A second service uses
that resource through an explicit borrowed read surface, without acquiring a
second Session custody lease. The host continues to own termination, timers and
durable Session metadata.

The Machine receives its own one-use connection nonce and RAM Ed25519 key. Its
trusted context names the actual Agent Instance, Session, Assignment and
accountable Principal. Governing roles remain empty. The allowed operations are
the intersection of the parent's current grant and the seven declared read
operations. Its action budget is zero; expiry cannot exceed the Session or
parent grant.

Each use checks the live resource and current parent policy and source. An
authentication or liveness refusal disposes the Machine credential. Explicit
Session disposal invokes its registered hook. Closing the borrowed service
closes that Machine transport; the parent retains Session ownership.

Short memory remains in the existing Session RAM resource. Note insertion and
disposal share a lifetime lock. Disposal zeroes retained note bytearrays, clears
the list and removes credential references. Removing cryptography key references
does not establish that underlying native key memory was independently zeroed.
Durable continuity remains Project State through fresh Context and Ontology
Views. Saved metadata cannot create another peer for an old resource.

The successor preserves all 245 inherited test method ASTs. Fourteen additional
cases cover actual identity/signature and shared custody, all seven public reads
with the real Machine Actor, replay, another signing key, foreign nonce, public
Actor spoofing, effect refusal before a journal claim, one peer per resource,
missing live resource, actual policy revocation, public termination and RAM
disposal, borrowed-service closure, original real-clock expiry, and undeclared
proof fields. The expiry case waits for the actual original interval.

Fixture helpers preserve each actual public reply and original durable journal
bytes before assertions. They retain request hashes without copying caller
request bodies. These observations inspect no Session RAM or signing keys and
replace no production callback. They establish neither fixture cleanup nor a
successful whole suite when execution is interrupted.

Before freezing and executing this successor, qualify Context6 with its full
50 original cases and independent audit, select its exact source/package pins,
and retain API34's full six-case termination and eleven-case controls evidence.
All inherited 146/134 integration and export cases, review cases, and an
independent Machine audit remain required. Fourteen new cases alone cannot
qualify the whole API, Agent, or release.

The original 34 public contracts and 46 task plan remain intact. The sole actual
owner checkpoint remains R08 after S02. This candidate grants no canonical
admission, activation, release, publication, or external authority.
