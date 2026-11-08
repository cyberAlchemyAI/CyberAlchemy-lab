# d95 live profile correspondence repair

The frozen `t03-d95-margin-api-recut-0001` cold preflight passed, but its selected
API callback would always refuse a live Lesson operation: `Schemas.profile_binding`
uses `{ref, sha256}` while the protected configuration requires `{path, sha256}`.
The old callback compared those dictionaries directly. This disjoint API
successor converts the exact relative reference and digest before comparison;
it does not relax either input shape or digest. The old package and receipt
remain intact as a diagnostic.

The new API package is
`product/lab/release-candidates/v1/interface/api-integration-v33-t03-one-lesson-native-v4-margin-0006`.
Its source manifest SHA-256 is
`2e152c9ec926f9f1e161b1002cf1ba1b128e86e2cef1f6712c1ef2714022abe9`;
its profile SHA-256 is
`1f2cf91eaa72c4687a791faaaac264ef5132afa2ba369f970f10787a17fe1750`.
The 211-row selection retains the exact current application-v4 and
assessment-v2 method files. Only `observed_margin.py` changed semantically
from the prior cut; local paths/profile/manifest/receipt were rebound.

Use this package's `launch.py` with a repository driver and its `margin.py`
`DiagnosticMargin(package_name)` as documented in the predecessor README.
The selected interpreter remains the owned 1,010-member installation in
`t03-d95-margin-api-recut-0001/working/installation-0001`, with the reviewed
jsonschema 4.19.2 overlay. `capture.py` replays normal and optimized cold
preflight and ten causal scope tests in each mode. The preflight directly
proves the old dictionary equality is false, then proves the exact new
ref/path/digest correspondence and three wrong-shape, wrong-reference and
wrong-digest refusals.

No live `lesson.apply` or `lesson.assess` call has been executed by this
package. Its diagnostic mode does not qualify or enforce empirical margins.
