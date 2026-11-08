# Sustained ingestion experiment profile

- Profile ID: `sustained`
- Lifecycle owner: CyberAlchemy Lab graph-read-model prototype construction
- Artifact type: implementation-bearing product experiment
- Contract path: `../contract.json`
- Prompt set: none; native deterministic process workload
- Regime set: `sustained`
- Attempt count: two independent fresh processes
- Authority effect: none

## Quality bar

Each attempt must accept and project 500 ordered calculated batches through a
16-slot bounded queue while four reader threads inspect immutable snapshots.
The paused-start control must fill exactly the declared queue and reject the
next batch as retryable overload. The retry must succeed after resume. Final
state must equal an independently rebuilt calculated cut, all accepted batches
must drain, final semantic and governance lag must be zero, reader observations
must contain no torn generation, and the process must remain inside the declared
time, throughput, latency, and pending-work bounds.

## Anti-patterns

- Treating queue acceptance as projection completion.
- Dropping or silently reordering an overloaded batch.
- Calling a disposable read model a canonical event source.
- Inferring multi-writer, durable append, power-loss, production, approval,
  admission, activation, or deployment claims from this local experiment.
