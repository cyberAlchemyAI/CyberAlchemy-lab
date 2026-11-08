# Compiler self-model successor

Candidate prototype, authority effect none. The original domainspec/ source and
its historical evidence remain unchanged. project/ contains the complete successor.

The four generic typed backend nodes become versioned contract-document Entities.
Their six fields describe contract identity, revision, required information,
semantics, rejection and authority limits. Evaluation reads these documents; it
does not execute an invented domain mapping or choose an invented policy default.
Three additional Entities represent declarations, compiler bindings and evidence.

migration.json accounts for every original node and edge, pins predecessor bytes
and records each preserved/replaced relationship. New prototype relationships
make compilation read declarations and bindings and create evidence.

Open questions: product review of this exact successor; later runtime realization
of document revision/identity management. Compilation alone proves neither.
