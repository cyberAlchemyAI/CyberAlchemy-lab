# Correction to the preceding profile-selection numeric explanation

The preceding registered K02-profile-selection MODEL-REVIEW/API prose described
the Nat decoder as requiring canonical integer spellings. That explanation was
incorrect. Its proved code uses NumberEpochAst.TokenEpochMeaning and the exact
nonnegative rational-value equation from DecimalEpochCheck: decimal and exponent
spellings with a natural value are supported, and negative zero is supported.
The registered proof sources and results remain unchanged; this append-only
correction changes the current explanation rather than rewriting historical
evidence. It establishes no new inherited discharge or Schema equivalence.

`42.0` and `4.2e1` both have exact value 42 and are accepted. The real shape/raw
gap is a non-integral token such as `123.000000000000000000000001`: ordinary
floating-point JSON decoding rounds it to 123.0, so a decoded-value integer
schema can accept it. The formal decoder evaluates the retained rational token
exactly and refuses it as a Nat. Duplicate-key preservation is a separate gap.

The predecessor's integral-float schema case demonstrates decoded-value shape
acceptance, not a difference in acceptance of `42.0`. Its flag that shape validity
does not establish byte-decoder acceptance is still a valid general limitation;
the accompanying canonical-spelling explanation was not supported by the code.

`representation-comparison-probe.json` binds fresh phase-specific executions of
the exact token cases and an actually captured authority snapshot containing the
rounding counterexample. The main interpreter equivalence proofs retain their
original scope; these probes are runtime comparisons, not independent checking.
