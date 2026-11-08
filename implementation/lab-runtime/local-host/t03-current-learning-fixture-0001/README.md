# T03 synthetic current Lesson fixture 0001

This disjoint fixture creates one **technical, synthetic** Operational Lesson about
API33's observed native representation gaps. Its evidence is the independently
reviewed API33 gap analysis (`EVIDENCE_SHA` in `fixture.py`), not the expired R03
Machine Lesson. It selects the candidate using the actual pinned
`lesson-selection-rules-v2` implementation. The fixture is not in a signed
Source8 store and grants no Lesson application, assessment, authority, or
runtime permission.

The source cut, Assignment, Session, review, retention policy, applicability,
instruction, and original-byte witnesses are synthetic and internally exact.
`build(aware_now)` gives the Lesson a 24-hour candidate expiry from construction;
the cold tests use a fixed clock to make refusal cases reproducible. Real host
selection must replace every synthetic input with independent current sources.

Run the cold tests from this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_fixture.py
PYTHONDONTWRITEBYTECODE=1 python3 -O -m unittest -v test_fixture.py
```

The selected native family `legacy-local-947e6c2a5b3d10f8` still has zero
current Lessons. Its Context generator explicitly refuses any current Lesson
and assumes 25 mapped source rows and 30 generated carriers; the source builder
assumes 21 admissions. A positive live T03 sequence therefore needs a **new
versioned native Source/Reader/Mapper/Context family** whose signed source
contains this Lesson, whose mapping represents it, and whose Context proves
applicability without widening the original scopes. It also needs independent
review, policy, instruction, operator, and assessment witnesses described in
`../t03-current-learning-runner-design-0001/NOTE.md`. The selected sixth API33
package and existing native family are untouched.
