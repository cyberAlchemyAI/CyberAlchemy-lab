# Candidate local provisioning rehearsal

C11 initializes a disposable Project branch from the exact pinned frozen v2 candidate engine and D75 profile. It independently signs and replays the S01 candidate catalog. The branch, catalog, key and exports live only in a program-owned temporary root outside the repository.

The Project store retains the frozen engine's explicit `artifact-instance` category and `admit` effect. Those settings do not enforce a semantic Work-only authority interface. Context projections, ontology graphs, local Project admission, catalog candidate posture and repository admission retain separate meanings.

Verification records the public configuration, independent replay pins, signed catalog genesis, exact export digests, fresh-process replay, recovery and cleanup. No permanent store or service is started. Fixture signatures are not human owner responses. The fixture private key is generated with mode 0600 and removed with the owned temporary root; it is absent from all public stores and receipts.

[Permanent operator instructions](OPERATOR.md) cover actual operator/location selection, private custody, profile gates, exports, rollback and recovery. Actual admitted provisioning remains A02 after R08.

```bash
python3 implementation/lab-provisioning/candidates/v1/validate.py
```

The result proves only isolated candidate provisioning. A later final package must include and validate the exact selected helper/adapter code and actual operation scope.
