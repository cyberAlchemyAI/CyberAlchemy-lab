# What the digest implementation establishes

Previously the byte-capture pipeline could check the original bytes against a
record meaning and retain the submitted envelope, but its digest field could
still be an uncomputed fixture label. This candidate computes SHA-256 from the
exact byte list and checks the submitted digest against that computation.

The meaning was specified before the evaluator. It is an independent derivation:
correct padding, lossless ordered 64-byte block partition, 64-word schedules,
64 prescribed rounds per block, componentwise feed-forward, ordered block chain,
and final word serialization. No predicate is defined as successful execution of
its checker. Word arithmetic and bit functions are shared mathematical primitives;
translation of those definitions and constants from the external standard remains
an explicit review boundary.

The main general result, digest_exact, says:

    digestBytes input = some claimed  iff  DigestMeaning input claimed.

This is proved through stage soundness and completeness, rather than an assumed
hash provider. Domain totality separately proves that every input shorter than
2^61 bytes produces a result. Canonical output is proved to have exactly 64
characters, all from 0-9 and a-f. Digest uniqueness is uniqueness for one exact
input. It is not injectivity, collision freedom or cryptographic security.

The candidate profile names SHA-256/FIPS1804-2015 and lowerhex64. Profile checking
compares the complete RevisionRef: owner, artifact, revision and profile digest.
All components must be nonempty. The expected profile is an input to the checker;
this cannot prove that its selector is authentic or entitled to choose it for a
Frame. Reference spelling and equality are structural evidence only.

The digest-specific classifier distinguishes unsupported profile, algorithm-domain
refusal, byte-budget refusal, malformed digest and digest mismatch, with verified
as the sole success result. General exactness results cover these outcomes and
the boolean check. A configurable byte budget is a resource guard; neither its
value nor successful test runs establish a qualified operational envelope.

Kernel controls check the empty and abc vectors and refusals for changes in each
profile reference component, unsupported algorithm/encoding, malformed digest and
budget excess. Their reference and profile digest are explicitly synthetic. Runtime
controls compare 51 concrete byte inputs with Python hashlib, including padding
boundaries, arbitrary bytes, both original binding fixtures and byte changes.
Eight additional cases keep the original submitted digest while checking unchanged,
truncated, same-count changed and appended inputs. Differential runtime comparison
is separate from the kernel theorem, and is not independent proof checking.

The full plan remains open. Capture/catalog composition, authentic profile selection,
Schema and actual issuer/review providers, all nineteen full-source policy predicates,
external standard translation, runtime/resource qualification, all relation obligations
and mandatory independent checking retain their requirements. K04 and global D01-D08
reviews remain pending. All 263 inherited obligations remain pending and the 90 original
discharges retain their original scope. This package does not admit N01, freeze N03,
authenticate a capture, promote a profile or finish the plan.
