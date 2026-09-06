# Formal Tool Receipt

Timestamp: 2026-06-16T21:24:05Z

Command:

```bash
+ /home/vrondelli/projects/domainspec-core/.formal-tools/jre/current/bin/java -jar /home/vrondelli/projects/domainspec-core/.formal-tools/alloy/org.alloytools.alloy.dist-6.2.0.jar exec -f -t json -o projects/domainspec-v2/research/alloy-tla-modeling/invoke-plan/run-results/alloy/order-fulfillment-output -c \* projects/domainspec-v2/research/alloy-tla-modeling/examples/OrderFulfillmentSaga.alloy
```

Output:

```text
00. run   showCompleteSaga         0    1/1     SAT
01. run   findMissingCompensation     0       UNSAT
02. check checkCompensationCompleteness     0       UNSAT
```

Exit: 0
