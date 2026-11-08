# Phase-scoped T35 template plan, inactive

The reviewed v1 Source→Reader probe selected all 30 initial stage leaves in
its Source manifest. That made later Mapper pin rewriting impossible without
invalidating `Source.verify_source` and `SelectedReader.guard`. The historical
constructor instead captured the Source role and Reader code first, then
rewrote Mapper and Context files after their predecessor manifests existed.

This v2 module separates a full prospective template plan from the initial
materialized family. It binds 27 role templates and three controls. The plan
control is self-contained: it records 12 Source/Reader role bindings, 15
future Mapper/Context template bindings, and the two other controls. Its own
binding is derived from its final bytes, avoiding a recursive self-hash.
Only the 12 Source/Reader role leaves and three controls may appear in the
initial family inventory. Future Mapper/Context paths must be absent. An
early Source manifest can select exact repository inputs plus those 15
materialized leaves without selecting future role bytes. Once Source/package
and Reader manifests exist, the pure `mapper_bindings` calculation rewrites
the historical Mapper predecessor constants and derives four prospective
Mapper output bindings; it does not write those files.

The three tests are synthetic contract oracles. They check 27+3 planning,
15+15 partition, refusal of an early future role or changed early leaf,
caller-row mutation isolation, and exact Mapper predecessor pin rewriting
under normal and optimized Python. They do not prove that a Source/Reader
builder succeeds with the future paths absent. A later separate fixture must
O_EXCL-create only the initial 15 leaves, run Source then Reader against that
closed prefix, and independently select the resulting phase outputs before
any Mapper import or native effect. The current v1 receipt remains a bounded
standalone Reader proof and is not silently reused as this v2 predecessor.

No production writer, protected Source8 input, current issuer, native Mapper,
Context phase, host qualification, formal LC-U02-05 acceptance, or activation
authority is implemented by this pure plan.
