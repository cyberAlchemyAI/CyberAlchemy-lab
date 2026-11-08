# Read-model family

This family owns the portable fixture denominator for a DomainSpec Query. Its
owner-authored example asks for one complete settlement view from two exact,
ordered concept reads. The expected read model, closed field shape, declared
failures, and read-target order do not come from a language implementation.

The independent family observation records declared reads and the absence of
writes through return, iteration or await, cancellation, close, dispose,
finalizer, and quiescence paths. Missing or unsupported coverage fails closed.
The seven hostile classes include hidden writes, write-then-restore, deferred
writes, undeclared reads, extra result fields, missing lifecycle coverage, and
unsupported dynamic source. Cancel, close, dispose, finalizer, and quiescence
are variants of the one admitted missing-coverage class.

This first family denominator exercises owner-authored successful result cases.
It binds the declared failure vocabulary but does not yet treat a target failure
observation as passing family evidence; target failure-path proof is deferred to
the later target SWUs.

This is transport-level family-fixture evidence only. It is not runtime
interception, an operating-system sandbox, arbitrary-source coverage, target or
provider proof, language parity, or proof that the settlement facts are
business-correct.
