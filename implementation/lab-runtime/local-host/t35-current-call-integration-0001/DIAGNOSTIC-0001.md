# Frozen API33 current Source8 call refusal

The first actual current Source8 run used frozen `api-integration-v33-current-0001` with the reviewed 15-boundary observer. Signed Source replay succeeded, but `current_source8_view(view)` refused before policy construction or `Service.call`:

```text
AttributeError: module '_cal_legacy_local_947e6c2a5b3d10f8_legacy_session_fixture_mapping_reader_v2_0257.reader' has no attribute 'CurrentFixtureReader'
```

The selected current reader module defines `SelectedReader`; the frozen API33 `source_bridge.py` current Source8 branch names `CurrentFixtureReader`. This is a product selector defect, not a measured callback outcome. The original API33 and observer bytes remain frozen. The disjoint successor changes that one class-name literal, rebinds its copied closure and 15 boundary rows, and must independently pass a new actual call before any positive T35 claim.

The first successor attempt then reached the callback boundary, but the old observer's `compile()` inherited its own `from __future__ import annotations` compiler flag while the selected `service.py` did not use that flag. The only runtime-versus-source code difference was `co_flags`, so the observer falsely returned `BOUNDARY_CALLBACK_CODE_REFUSED` before invocation. The disjoint observer copy uses `compile(..., dont_inherit=True)` and its exact bytes are separately pinned. This second refusal also made no callback claim.
