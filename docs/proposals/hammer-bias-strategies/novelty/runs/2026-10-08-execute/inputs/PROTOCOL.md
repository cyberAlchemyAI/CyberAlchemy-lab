# Protocol for investigating useful novelty in analysis

Status: prepared design, no scored trials executed. The question is whether a particular operator adds assessable, potentially useful openings beyond ordinary analysis and a generic creativity request, under the same evidence and workflow. Effects are conditional on the common two-lane scaffold; this study cannot establish that the scaffold itself is better.

## Evidence motivating the design

The earlier experiment's three conditions selected identical actions on twelve authored cases. Two open cases produced overlapping mechanism families. The control permitted changing approaches when appropriate. These observations support no local selection winner and leave generative novelty unresolved. See the [independent experiment audit](../runs/2026-10-08-execute-all/audit/experiment-review.json). The proposed changes below are design judgments, not findings from a new experiment.

## Freeze before launch

An investigator must prepare six case packets: two discovery cases, two related-domain confirmation cases, and two different-domain transfer cases. A separate case author uses the case contract in protocol.json; there are no answer menus or model-best action keys. Include one case where the familiar tool is useful and another where the assumed boundary could be questioned. All observations in synthetic cases are explicitly stipulated. Do not reuse the hammer/queue examples in these documents as held-out evidence of transfer.

Freeze case bytes, evidence, actual hard constraints, scored outcome, archive, prompts, budgets, selection rules, model settings, and assessment criteria before seeing treatment outputs. Randomize condition execution order within case/repetition blocks and randomize blind packet presentation order, recording the separate shuffle seeds. These are order seeds, not a claim that model randomness is controllable. Case-specific reference archives may include ordinary proposals and earlier findings with provenance; disclose their incompleteness. Keep archives evaluator-only so they do not become generation menus. Keep transfer packets out of prompt tuning, finalist selection, and screening. Record file hashes and access boundaries. These case packets and archives are launch work, not artifacts claimed to exist now.

## Conditions and comparable resources

Every run unit has exactly three generation calls:

1. Lane Z independently analyzes the incumbent, outcome, evidence, and constraints. It cites a real supplied counterexample if one exists; otherwise records the absence rather than inventing one.
2. Lane A independently generates alternatives. Only its operator instruction changes between conditions. Neither lane sees its sibling's output before both are saved.
3. Neutral Distill receives the two frozen outputs and produces one compact decision artifact under the same instruction in every condition.

The two controls are ordinary outcome-and-constraint analysis and the same prompt plus a generic request for unusual useful possibilities. The twelve treatments fill Lane A's operator slot from catalog.json. Generation packets contain only the operator question/instruction and common contract, never worked examples, reviewer calibration, earlier rankings, or the parent's clever sentences.

The provisional ceiling is 900 generated tokens per lane plus 600 for Distill: 2,400 per run unit. Corresponding roles have equal input-token ceilings, tool access, runtime configuration, and candidate slots. There are at most two openings per lane and four raw openings per run; fewer or zero are valid. Common Distill preserves a disposition for every ID, with no more than four retained openings. Perform one unscored format preflight on a separate case to check that the contract fits. Budget it separately as one run unit, three generation calls, and 2,400 output tokens. If it shows the contract does not fit, revise the common specification and resource bounds before any scored launch; no extra attempt is silently included.

Record actual tokens, calls, elapsed time, errors, model/settings, and any unobservable overhead. When the runtime cannot enforce caps or expose usage, label the comparison as matched instructions and soft ceilings, not equal compute. Word counts are only a proxy. Hard cap failure or truncation is an execution-quality outcome, not zero novelty. Default retries are zero. Record failed or truncated calls as execution-quality outcomes. Any decision to permit retries requires a revised, frozen common rule and explicit additional resource bound before scored launch; never selectively rerun weak ideas.

## Two stages with explicit limits

| Stage | Conditions | Cases | Repetitions | Maximum run units |
| --- | --- | --- | --- | --- |
| Discovery | 12 operators and 2 controls | 2 discovery cases | 2 fresh repetitions | 56 |
| Confirmation | Up to 2 frozen finalists and 2 controls | 4 untouched cases | 3 fresh repetitions | 48 |

Maximum scored total: 104 run units, 312 generation calls, and 249,600 allocated generated tokens before review. Including the separately budgeted single format preflight, the preparation-and-scored envelope is 105 run units, 315 generation calls, and 252,000 allocated generated tokens. All these totals use the stated provisional caps and zero retries. These are proposed ceilings, not incurred use. If zero finalists advance, stop with the discovery result; do not invent a winner. With one finalist the confirmation stage has 36 run units. The combined recipes C1–C3 are subsequent experiments, not extra arms silently added here.

These sample counts bound exploration and repeated observation. They are not derived from a power calculation. Repetitions from the same runtime family do not become independent organizations, people, or domains.

## Assessment and blinding

Each opening may be a mechanism, hypothesis, question, or explicit frame branch. Generators cite only supplied case/incumbent evidence IDs. Evaluators later attach frozen archive matches; archive IDs are never demanded from generators who cannot see the archive. Use candidate-template.json as the record contract, adapting field formatting to the frozen output budget. Save raw outputs first. Any uncertain or unsupported premise stays marked.

Prepare method-anonymous presentations using stable IDs and a fixed field order. Remove condition labels and rhetorical styling, but preserve causal content, uncertainty, constraints, and predictions. A normalizer cannot repair a weak proposal. Keep the raw text and a reversible mapping. Reviewers should record if the operator is inferable; blinding limits remain part of the result.

Two independent judges receive the frozen archive and method-anonymous raw/post-Distill pair. They lock judgments before seeing condition labels or one another's judgments. Deduplicate within each case/run by actor, operation, target, causal path, conditions, predictions, and assumptions. A parameter adjustment may be useful without forming a new family. Combinations count as different only when a specified interaction changes behavior. New questions need a different observable distinction, not a new wording of the same request for diagnosis.

Each judgment is a vector:

- Novelty: equivalent, new parameter/condition, new mechanism/observable distinction, explicit frame branch, or uncertain; always name the comparison set.
- Potential usefulness: no stated link, plausible stated link, or direct connection to a named outcome or next decision. This remains a judgment, not observed benefit.
- Constraint fit: preserves commitments, uncertain, explicitly conditional, or violates a hard constraint.
- Observability: missing, vague, or a specific discriminator against the nearest rival.
- Support: supplied evidence, inference, or speculative premise.
- Burden: measured generation/review cost and separately estimated implementation burden.

Use judges' reasons and anchored categories; never multiply ordinal scores into one creativity number. Retain disagreements. One bounded adjudication per disputed pair may use original text; unresolved cases remain uncertain. At the maximum there are 104 raw/post pairs and 208 independent pair assessments, plus up to 104 adjudications. Budget review separately: a proposed ceiling of 600 generated tokens per pair assessment and 600 per adjudication gives at most 187,200 review tokens, excluding input context and any deterministic presentation work. Actual costs remain unmeasured until execution.

## Compression loss and preservation

Every raw opening has a stable ID. Distill maps it to retained, merged-with-IDs, rejected-with-reason, or parked. A retained name with its distinguishing causal relation deleted is a lost idea. Count the number of distinct archive-new ideas still intelligibly represented after Distill divided by the corresponding number before Distill. A zero denominator yields undefined retention. Report commitment-preserving and conditional frame branches separately.

Also record unsupported additions, changed certainty, missing beneficiaries, erased minority ideas, and burden reduction. A generator may add novelty that compression later removes. Distill timing and workflow structure remain fixed in this study; a separate matched ablation would test those effects.

## Selection and interpretation

Use the per-case set of novel, assessable, potentially useful, commitment-preserving openings as the main comparison, accompanied by all other dispositions. Compare both the full capped set and the first two openings selected under a frozen relevance rule. Do not change that rule after viewing method labels. Empty outputs, refusals, and execution failures receive explicit dispositions.

A discovery operator can advance only if both judges or adjudication identify an archive-new, specific, potentially useful, commitment-preserving distinction on both discovery cases. This is a conservative local screening rule, not statistical significance. Compare concurrent controls: an idea found equally by controls provides no operator advantage. Remove mechanism-equivalent finalists. Among eligible operators, retain the non-dominated set on per-case contributions, fit, and burden; if more than two remain, use a preregistered random selection with its seed recorded. Do not tune the finalists using confirmation data.

On untouched cases, report paired per-case differences, repeated appearances, family overlap, disagreement, counterexamples, and transfer failures. Use conclusions such as no observed advantage, context-limited signal, unresolved, or candidate for focused testing. An illustrative advancement rule is a useful novel contribution repeated across multiple untouched cases; it never proves population-level superiority. Do not claim global originality from a local archive.

## Next action and stop conditions

The next owner is a future experiment investigator applying experiment-harness to freeze and launch the packets above. This package provides the operators, contracts, route shapes, review design, and finite budget. Stop generation at the fixed cap or repeated equivalent proposals. Stop the whole investigation on irreparable evidence mismatch, leakage into a holdout, or an unsupported comparison claim; retain completed results with the appropriate exclusion reason. Missing outcome evidence is a reason to design a probe, not automatically a reason to abandon generation.

Completion states remain separate: prepared, generated, independently assessed, and tested in the world. This preparation completes the strategy-design request. It makes no claim that new comparative trials, physical probes, or operational interventions have run.
