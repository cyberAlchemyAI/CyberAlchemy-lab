# Successor importer prototype definitions

Status: prototype. Authority effect: none.

A Source Package is one profile-qualified source document set. Package identity
includes the source profile path; equal ontology names never merge packages.
A Source Record is one complete JSON node or relation object. Its original
fields, JSON value types, source ownership, challenge contracts and authority
posture are retained without interpretation as new authority.
An Import Manifest selects exact files by SHA-256 and JSON array selectors,
with explicit identity, type and endpoint field mappings. It never discovers
or reads arbitrary references from source content.
A Source Record Envelope is a closed runtime property object holding the
original record plus its exact document selector and package identity.
A Migration Event is a complete-state semantic event, joined to a non-authorizing
governance event. Initial import creates revision one; replay calculates state.
A Migration Projection is the current set of records calculated from events,
not an alternative canonical store. Source JSON can be compared losslessly
at the record level; JSON formatting and package-level metadata are not claimed
as reconstructed source files.
An Unsupported Package is reported, never silently skipped or called migrated.

## D65 prototype chain

Definitions -> agent scaffold -> Product: inspect actual ontology records ->
Business: retain source meaning and ownership -> DomainSpec: explicit typed
source-record envelope -> System: sealed subject events and exact governance
join -> Rust importer and isolated kernel -> exact candidate -> current tests ->
one final Product review. The envelope is a prototype profile, not an admitted
DomainSpec profile or generated DomainSpec compiler output.

## Work lanes

Product construction: implement, exercise and freeze the importer; runnable now.
Causal limits: source adapters and the kernel's empty-property restriction.
Operational support: none blocks this prototype. Runtime owner owns later
cutover; source owners own retirement; repository owner owns publication.
All are deferred and do not stop dependency-ready construction.
