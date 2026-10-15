# Exact byte digest: independent specification before implementation

This is reversible N01 preparation for the full plan. The supported candidate is
SHA-256 on byte-aligned messages, with the full 256-bit result represented as
exactly 64 lowercase ASCII hexadecimal characters. Its proposed profile is not
an authentic owner choice. Other algorithms/representations remain unsupported
by this evaluator, rather than silently being interpreted as this profile.

The algorithm reference is [NIST FIPS 180-4, August 2015](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf):
sections 3.2, 4.1.2, 4.2.2, 5.1.1, 5.2.1, 5.3.3 and 6.2.2.
External standard-to-formal-model translation is a separate review obligation.
There is no FIPS validation or cryptographic-security claim.

Independent computation meaning, without a call to the digest evaluator:

1. Original input is a finite ordered list of UInt8, with length less than 2^61
   bytes (hence bit length less than 2^64). Empty input is supported. The
   interpretation neither normalizes JSON nor reconstructs bytes from an AST.
2. Padding retains all original bytes, appends 0x80, the unique zero-byte count
   k in [0,63] making n+1+k+8 divisible by 64, and the original bit length as
   eight bytes in big-endian order. The length bound forbids wrapping.
3. The padded input is decomposed, without omission, reordering or overlap,
   into exact 64-byte blocks. Each block supplies sixteen big-endian 32-bit
   words. A schedule has exactly 64 words, retains those first sixteen, and
   satisfies the prescribed recurrence for positions 16 through 63.
4. Each block starts its eight working words at the previous hash state. There
   are exactly 64 rounds, in order, with the pinned constants and functions.
   Word operations use UInt32 modular arithmetic. The resulting working words
   are added componentwise to the previous hash state. Blocks proceed in order,
   beginning at the eight SHA-256 initialization words.
5. The eight final words are serialized in order, most significant nibble first,
   using lowercase hexadecimal, including leading zeroes. There is no prefix,
   whitespace, truncation, case folding or alternate algorithm interpretation.

The independent meaning will use inductive schedule, round, block and message
derivations. Shared low-level word operations are mathematical primitives, not
success flags or an asserted hash output. The evaluator must prove correspondence
to these derivations. Test vectors complement, and cannot replace, that proof.

Profile binding means equality of the complete submitted RevisionRef with the
selected candidate profile, together with the specified algorithm and encoding.
Authentic selection of that profile for the exact Frame remains the separate
ownedDigestProfile policy. A nonempty label cannot establish it. Digest equality
also cannot prove the input's issuer, owner review, freshness, schema validity,
collision freedom, or relation validity.

Refusal cases must remain distinguishable: unsupported profile; input outside
the algorithm domain; configured operational byte budget exceeded; malformed
digest representation; recomputed digest mismatch. A resource refusal is not a
semantic counterexample. No operational budget becomes qualified merely because
an implementation accepts the algorithm's theoretical length domain.

Integration must retain full original envelopes, match declared byte count,
check the submitted profile and digest, then compose with byte-record preparation.
It must not repair a submitted bad digest or substitute a caller AST. Schema,
authentic issuer, profile ownership and owner-review providers remain mandatory.

All 263 inherited obligations and the 90 retained original discharges keep their
existing scope. K04 and D01-D08 remain pending. This specification alone closes
no inherited obligation, admission gate, independent-checker run or full-plan task.
