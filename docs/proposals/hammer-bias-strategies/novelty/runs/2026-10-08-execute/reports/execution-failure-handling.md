# Execution failure dispositions

The frozen addendum requires zero retries and preservation of failed units as execution-quality outcomes. A failed trial is not zero novelty. No original output, generation prompt, validator, or scoring rule is repaired after a failure.

## B001: critique constraint-status format

The native Q role completed and its output was hash-locked in [the receipt](../receipts/B001-Q.json). Its opening's `fit` is a descriptive conditional sentence. The frozen validator accepts only `preserves`, `uncertain`, `conditional`, or `violates`; it therefore returned `fit enum`. The frozen critique prompt contains `fit:...` without enumerating those values. This interface omission is part of the interpretation of this failure.

The original [Q output](../outputs/B001/Q.json) remains unchanged. The dependent D role was not invoked: [skip disposition](../receipts/B001-D-disposition.json). This is a failed full-scaffold trial, with valid Z/A artifacts and an invalid Q artifact. It must not be claimed as a completed combination with Distill or rerun selectively.

## Review and audit consequences

The original frozen `blind_packets.py` omits invalid role outputs from its `raw` list. The separately versioned [bundle packet adapter](../tools/blind_bundle_packets.py) preserves the actual readable Q openings and critiques, unchanged as data, alongside the execution-failure flag and absent Distill output. It retains the original shuffle, method-label removal, review criteria, and output lineage. Reviewers can assess the available text while recording unavailable retention; execution validity remains false. It does not repair `fit` or silently omit a failed opening. [Artifact checks](failure-packet-adapter-check.json) confirm exact preservation for B001/B002 and reject an unfinished unit. No full bundle review batch has been frozen yet. Version hashes are in [the adapter manifest](../failure-handling-tool-manifest.json).

B002 encountered the same `fit enum` validation failure and dependent D skip; its records are preserved in the shared failure ledger. This recurrence is evidence of an execution interface problem, not evidence against either combination's causal ideas.

The original integrity tool lists failed or dependency-skipped roles as pending because it checks successful generation. Final accounting must additionally reconcile [execution failure records](execution-failures.jsonl) and skip receipts to distinguish terminal failures from unstarted work. Preserve the original integrity report and report successful, failed, skipped, and genuinely pending work separately.

The current case-normalization adapter assumes all role outputs are valid and several post-disposition arrays are empty. It must explicitly support these recorded dispositions before normalizing a bundle batch containing a failure. It must not substitute empty arrays or successful status to pass its assertions.
