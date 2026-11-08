# Value-computation family

This family owns the portable proof denominator for a DomainSpec Calculation.
The fixture states one business calculation: net settlement amount is gross
amount minus fee amount. It is owner-authored input, not generated from any
language implementation.

`RMT-CALC-002` deliberately closes with the target observation missing. The
family evaluator and independent effect-observation transport are executable,
but TypeScript, Python, and Rust providers belong to later SWUs. A provider may
not prove purity by returning its own zero counters: the observation must bind
the separately locked observer and cover every declared channel.

The portable claim is limited to the declared observation perimeter. It is not
an operating-system sandbox or proof that an unsupported channel was effect
free.
