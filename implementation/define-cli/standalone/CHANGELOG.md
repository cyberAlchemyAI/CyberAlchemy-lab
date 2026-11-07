# Changes

## 0.3.0rc2

Qualification successor to the standalone rc1 candidate. The subsequent packaging update applies Apache-2.0 with LICENSE, NOTICE and SPDX metadata; runtime sources remain unchanged:

- Report source drift consistently as blocked with exit status 3 through the JSON executable.
- Keep task values and parameter-schema literals separate from source-binding traversal.
- Reject reserved control-path collisions, unselected captured bytes and unsupported row selectors.
- Preserve known rc1 empty-snapshot encoding records; new empty snapshots carry only necessary controls.
- Check materialization references during preparation and reject contradictory assessment reasons.
- Report an unknown publication outcome if parent-directory synchronization fails after the atomic rename.
- Load installed schema/generator resources through portable, digest-checked reads and use canonical manifest paths.
- Include the standalone test suite and public fixtures in the source archive.

The release evidence records Linux installations and full suite runs on Python 3.11–3.14. This candidate does not establish native Lab admission, authenticated external standing or domain execution.
