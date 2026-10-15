# Transactional caller initialization

This successor preserves the prior helper/caller selection and every domain function body. Helper execution removes its own exact synthetic registration on failure. A paired initialization handler rolls back earlier successful helper registrations if companion setup fails. A separate handler covers all later original native imports and Source initialization.

Rollback removes an entry only while it still refers to the exact object created by this import. Replacement objects and unrelated registrations survive. The owned registration list is cleared after rollback. Successful initialization retains both selected modules and the externally held code contracts.

Actual installed 0004 controls passed14 scoped checks. They include normal file/contract/delegation checks, an owned helper-execution exception, pair rollback, preservation of a replacement object, and static verification that both initialization failure regions invoke rollback. Original native imports and domain function bodies remain unchanged inside the new failure handler. No Source/native/Service/Session constructor or production callback was exercised or changed.

The original review and flagged predecessor remain frozen. Independent re-review, recipe adaptation, new source family, complete source/profile eligibility, full learning and timing-margin qualification remain required. These checks do not establish native authority or make the prior learning attempt pass.
