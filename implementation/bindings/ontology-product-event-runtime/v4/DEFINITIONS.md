# v4 construction definitions and acceptance contract

Status: prototype; authority effect none. Preserve v2 and frozen v3.

Source Package: exact profile-qualified identity, not an ontology-name winner.
Record Identity: package + node/relation/document kind + declared source identity.
Cross-package Relation: explicit endpoint alias resolved against the manifest;
all records share a storage graph namespace without merging semantic packages.
Document Record: exact UTF-8 source file content and digest, represented as a
source-document node; metadata, rule registries and definitions remain source
data, never imported executable authority.
Transaction: one immutable, digest-chained file containing semantic/governance
event pairs, optionally the initial source manifest. Readers see whole committed
transactions. Pending files are not committed history.
Expected Version: number of prior semantic events for one exact subject.
Create expects zero; update and retire require the current version.
Source Record Profile: lossless JSON envelope, not domain-schema conformance.
Retirement: representation lifecycle transition; never source-file deletion.
Recovery: validate committed history, then remove an uncommitted pending file
under a writer lock. Do not steal a stale writer lock automatically.

D65 chain: these definitions -> non-authoritative scaffold -> source-preserving
Product/Business contract -> explicit prototype DomainSpec envelope -> event
transaction system model -> Rust implementation -> frozen candidate -> current
tests -> user Product review. No generated DomainSpec compilation or admitted
profile is claimed.

Construction DAG: A baseline -> B mappings; B -> C governance adapters, D Define
adapters, E qualified links, F document coverage. A -> H transaction hardening.
C/D/E/F -> G coverage; E/H -> I versioned writes; G/I -> J Context queries;
J/H -> K corpus round trips, restart, hostile tests, benchmarks -> L freeze.
No intermediate prototype approval. Operations O rollback preparation and
R owner mapping proceed independently; live cutover remains deferred.

Benchmark thresholds, fixed before runs: real 21-package import <= 120 seconds;
fresh full replay <= 30 seconds; scoped query <= 30 seconds. Three fresh query
processes; report observed maximum and durations. These are local prototype
acceptance bounds, not production performance promises or large-graph SLA.

Benchmark execution uses the optimized release CLI, built before timed runs.
The first draft's debug-build run completed functional checks but exceeded the
query timing bound; no PASS or approval was granted. The limits above remain
unchanged for this new candidate epoch. Focused tests also run in debug mode.
