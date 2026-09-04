<!-- GENERATED FILE: edit the bound JSON source and rerun render.py. -->

# Definition lifecycle profile v1

> Generated from `lifecycle.json`; this view is not canonical.

- Status: `candidate-unadmitted`
- Authority effect: `none`
- Owner: `role:definition-owner`

## States

- `candidate-authored`
- `validated-candidate`
- `owner-reviewed`
- `admitted`
- `superseded`
- `withdrawn`

## Transitions

| From | To | Gate | Effect |
| --- | --- | --- | --- |
| `candidate-authored` | `validated-candidate` | Current Definition evaluation result is PASS under the exact bound evaluation profile. | Records validation posture only; grants no authority. |
| `validated-candidate` | `owner-reviewed` | Definition owner reviews the exact candidate digest and evidence set. | Records review completion only; grants no admission. |
| `owner-reviewed` | `admitted` | Exact human admission decision binds candidate, evidence, registry postimage, index projection, and drift audit. | Makes only the selected Definition version canonical inside its declared authority scope. |
| `admitted` | `superseded` | Exact successor decision names the admitted replacement version. | Preserves history and routes current lookup to the successor. |
| `candidate-authored` | `withdrawn` | Exact owner withdrawal decision. | Reserves identity and stops promotion. |
| `validated-candidate` | `withdrawn` | Exact owner withdrawal decision. | Preserves evidence and stops promotion. |
| `owner-reviewed` | `withdrawn` | Exact owner withdrawal decision. | Preserves review evidence and stops admission. |
| `admitted` | `withdrawn` | Exact owner withdrawal decision with replacement or terminal route. | Removes current authority without deleting history. |

## Separation invariants

- Semantic identity, lifecycle state, source currentness, validation result, authority state, and publication state are independent axes.
- A digest change creates a new candidate epoch; it cannot refresh an old admission decision.
- PASS does not imply owner review, admission, publication, implementation, or correctness.
- Directory placement and generated projections never change lifecycle state.

## Claim ceiling

This candidate defines lifecycle vocabulary and transition preconditions only. It does not transition, review, admit, supersede, or withdraw any Definition.
