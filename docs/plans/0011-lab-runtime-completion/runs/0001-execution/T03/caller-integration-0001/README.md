# Source caller integration

The Source template captures the integrity helper and caller companion independently, using their true paths and exact hashes. It holds both companion entry code records and the helper contract outside those modules. Before and after every original capture or whole-input verification, it checks the companion module/global/function bindings and then the externally held helper contract. The original metadata and domain functions remain unchanged.

Reader, mapper and Context already delegate to that Source implementation. Their selected postimages, and the corrected Context generation postimage, are retained byte for byte. Only the Source helper loader and identity checker change; the shared loader gains a closed kernel/caller namespace distinction.

Actual installed 0004 controls passed eleven checks. These compile the exact Source prefix before native imports, exercise its actual loader and held contract, verify owned files and explicit external inputs, and check the five selected postimages against their preimages. They do not construct or qualify a native Source, reader, mapper, Context, Service or Session.

The new helper/companion files, their component manifest and this exact caller template must be selected into a new family recipe and every affected role's complete closure. The old recipe pins its old helper and postimage paths; it cannot silently adopt this package. Independent component review, recipe adaptation, complete fresh native construction, full source/profile eligibility, realistic performance measurements and the original learning sequence remain required. No old permission, signer, Session or qualification transfers.
