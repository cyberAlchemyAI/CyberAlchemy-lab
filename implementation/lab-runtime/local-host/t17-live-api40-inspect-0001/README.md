# T17 live API40 artifact.inspect slice

The [live receipt](RUN-0001.json) records one authenticated API40 Base child driven through the cached disposable Paperclip process adapter. It queried a nonempty current canonical artifact set, selected one returned artifact, inspected that exact reference with contract and gap sections, then received `unauthorized` when it repeated the inspection with a wrong authenticated context. The child and adapter exited zero, the workspace held no objects or effect-journal entries before or after, and the private control was removed.

`select.py` pins the receipt, runner, reader, adapter, plan, API40 source/profile, preceding query slice and its live receipt. It checks that both live receipts observed the same exact source cut. [RESULT.json](RESULT.json) selects `artifact.inspect` as the fifth cumulative live operation pair, leaving **29 of 34** without selected positive and causal-negative evidence. The artifact reference itself is not retained; the receipt retains a SHA-256 of its canonical JSON encoding. The inspector did not request the body section or prove a persistent service. Six selector and three bootstrap/lock tests pass normally and under `-O`.

This local cut uses the legacy fixture selected by API40. A later Source/API recut requires its own dispatch and causal-negative evidence; these five pairs cannot be relabeled onto it.
