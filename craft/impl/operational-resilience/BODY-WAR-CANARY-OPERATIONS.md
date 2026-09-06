# Body War Canary Operations Model

The later runtime lifecycle is finite:

1. Verify exact host, artifact, image, label, port, and safety-limit bindings.
2. Persist and fsync the recovery ledger before the first effect.
3. Start only stable, gateway, and Prometheus; prove readiness.
4. Run the bounded stable baseline.
5. Add the byte-identical candidate and prove direct health.
6. Activate candidate-only gateway faults and run the bounded fault window.
7. Freeze workload and Prometheus inputs; evaluate without actuation authority.
8. On rollback, remove route target/weight, reconcile gateway state, then remove
   the candidate container.
9. Independently prove all five candidate-reference classes absent, 20 gateway
   probes good, five direct stable probes good, image unchanged, and deadline.
10. Tear down only exact project-labelled resources, allowing one idempotent
    cleanup retry, then freeze and scan evidence.

There is no full-trial or fault-activation retry. An unknown effect permits only
read-only reconciliation and exact cleanup. Actuator success is never observer
input. Prepared images and frozen evidence are separately declared residue;
runtime project residue must be zero.
