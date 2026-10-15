# Machine Context: Actor and policy custody

The Machine peer supplies its actual Actor, scoped seven-read allowlist, live
resource and ephemeral signer. Its parent ReaderChannel supplies the independent
private policy. These are different objects with different responsibilities.

The original fact-copy kernel registers one policy host. Registering the peer
as that host causes its parent's unchanged policy guard to reject the borrowed
fact scope. The peer then disposes its credential, even while its Session is
live. The runtime must explicitly bind the actual owner policy channel.

This candidate composition subclasses the original private fact-copy class.
The `host` property returns exactly the selected peer's original owner channel;
the original source, snapshot, Actor, grant, clock and generator functions are
retained. A private identity guard checks the actual Service, ReaderChannel,
MachinePeer, Context custodian, SignedSources and live resource chain on every
copied-fact check. A sibling host, different source, closed peer or changed
custody chain cannot borrow the scope.

The original generator still consumes the Machine Actor and permission bridge.
Only source facts are borrowed. Current policy, revocation, Actor and expiry
checks continue to run through the original parent and Machine guards. Full
source/package checks run before copying, after copying and after calculation.
Dispatch and durable writers remain outside the pure scope. No permission,
role, operation, lifetime or Agent identity is created by this composition.

Ordinary operator Context generation retains the original path. The Machine
adapter selects this composition explicitly in its frozen source closure. The
original seven-read method and affected refusal/lifecycle cases must qualify
the successor before complete Machine or API behavior can be claimed.
