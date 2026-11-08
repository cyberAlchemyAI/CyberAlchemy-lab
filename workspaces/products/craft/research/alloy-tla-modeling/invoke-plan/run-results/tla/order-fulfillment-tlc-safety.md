# Formal Tool Receipt

Timestamp: 2026-06-16T21:22:54Z

Command:

```bash
+ /home/vrondelli/projects/domainspec-core/.formal-tools/jre/current/bin/java -cp /home/vrondelli/projects/domainspec-core/.formal-tools/tla/tla2tools-1.7.4.jar tlc2.TLC -cleanup /home/vrondelli/projects/domainspec-core/projects/domainspec-v2/research/alloy-tla-modeling/examples/OrderFulfillmentSaga.tla
```

Output:

```text
TLC2 Version 2.19 of 08 August 2024 (rev: 5a47802)
Warning: Please run the Java VM which executes TLC with a throughput optimized garbage collector by passing the "-XX:+UseParallelGC" property.
(Use the -nowarning option to disable this warning.)
Running breadth-first search Model-Checking with fp 23 and seed -2426227615797343990 with 1 worker on 16 cores with 2992MB heap and 64MB offheap memory [pid: 3144423] (Linux 5.15.167.4-microsoft-standard-WSL2 amd64, Eclipse Adoptium 17.0.19 x86_64, MSBDiskFPSet, DiskStateQueue).
Parsing file /home/vrondelli/projects/domainspec-core/projects/domainspec-v2/research/alloy-tla-modeling/examples/OrderFulfillmentSaga.tla
Parsing file /tmp/Naturals.tla
Parsing file /tmp/FiniteSets.tla
Parsing file /tmp/TLC.tla
Parsing file /tmp/Sequences.tla
Semantic processing of module Naturals
Semantic processing of module Sequences
Semantic processing of module FiniteSets
Semantic processing of module TLC
Semantic processing of module OrderFulfillmentSaga
Starting... (2026-06-16 18:22:54)
Computing initial states...
Finished computing initial states: 1 distinct state generated at 2026-06-16 18:22:54.
Error: Invariant FreshnessSafety is violated.
Error: The behavior up to this point is:
State 1: <Initial predicate>
/\ completed = {}
/\ compensated = {}
/\ step = "Start"
/\ status = "Running"
/\ waiverRead = "ship-after-payment-timeout-v1"
/\ waiverCurrent = "ship-after-payment-timeout-v1"

State 2: <CreateOrder line 36, col 3 to line 39, col 65 of module OrderFulfillmentSaga>
/\ completed = {"CreateOrder"}
/\ compensated = {}
/\ step = "Payment"
/\ status = "Running"
/\ waiverRead = "ship-after-payment-timeout-v1"
/\ waiverCurrent = "ship-after-payment-timeout-v1"

State 3: <AuthorizePaymentTimeout line 42, col 3 to line 45, col 65 of module OrderFulfillmentSaga>
/\ completed = {"CreateOrder", "AuthorizePayment"}
/\ compensated = {}
/\ step = "Inventory"
/\ status = "Running"
/\ waiverRead = "ship-after-payment-timeout-v1"
/\ waiverCurrent = "ship-after-payment-timeout-v1"

State 4: <ReserveInventory line 48, col 3 to line 51, col 65 of module OrderFulfillmentSaga>
/\ completed = {"CreateOrder", "ReserveInventory", "AuthorizePayment"}
/\ compensated = {}
/\ step = "Shipment"
/\ status = "Running"
/\ waiverRead = "ship-after-payment-timeout-v1"
/\ waiverCurrent = "ship-after-payment-timeout-v1"

State 5: <CreateShipmentFails line 54, col 3 to line 57, col 68 of module OrderFulfillmentSaga>
/\ completed = {"CreateOrder", "ReserveInventory", "AuthorizePayment"}
/\ compensated = {}
/\ step = "Compensating"
/\ status = "Failed"
/\ waiverRead = "ship-after-payment-timeout-v1"
/\ waiverCurrent = "ship-after-payment-timeout-v1"

State 6: <CompensateInventory line 60, col 3 to line 64, col 69 of module OrderFulfillmentSaga>
/\ completed = {"CreateOrder", "ReserveInventory", "AuthorizePayment"}
/\ compensated = {"ReleaseInventory"}
/\ step = "Compensating"
/\ status = "Failed"
/\ waiverRead = "ship-after-payment-timeout-v1"
/\ waiverCurrent = "ship-after-payment-timeout-v1"

State 7: <CompensatePayment line 67, col 3 to line 72, col 69 of module OrderFulfillmentSaga>
/\ completed = {"CreateOrder", "ReserveInventory", "AuthorizePayment"}
/\ compensated = {"VoidPayment", "ReleaseInventory"}
/\ step = "Compensating"
/\ status = "Failed"
/\ waiverRead = "ship-after-payment-timeout-v1"
/\ waiverCurrent = "ship-after-payment-timeout-v1"

State 8: <CompensateOrder line 75, col 3 to line 80, col 69 of module OrderFulfillmentSaga>
/\ completed = {"CreateOrder", "ReserveInventory", "AuthorizePayment"}
/\ compensated = {"CancelOrder", "VoidPayment", "ReleaseInventory"}
/\ step = "Compensating"
/\ status = "Failed"
/\ waiverRead = "ship-after-payment-timeout-v1"
/\ waiverCurrent = "ship-after-payment-timeout-v1"

State 9: <DeadLetter line 83, col 3 to line 87, col 68 of module OrderFulfillmentSaga>
/\ completed = {"CreateOrder", "ReserveInventory", "AuthorizePayment"}
/\ compensated = {"CancelOrder", "VoidPayment", "ReleaseInventory"}
/\ step = "Terminal"
/\ status = "TerminalFailure"
/\ waiverRead = "ship-after-payment-timeout-v1"
/\ waiverCurrent = "ship-after-payment-timeout-v1"

State 10: <AcceptFreshnessClaim line 95, col 3 to line 98, col 74 of module OrderFulfillmentSaga>
/\ completed = {"CreateOrder", "ReserveInventory", "AuthorizePayment"}
/\ compensated = {"CancelOrder", "VoidPayment", "ReleaseInventory"}
/\ step = "Terminal"
/\ status = "Accepted"
/\ waiverRead = "ship-after-payment-timeout-v1"
/\ waiverCurrent = "ship-after-payment-timeout-v1"

State 11: <WaiverChangesAfterRead line 90, col 3 to line 92, col 67 of module OrderFulfillmentSaga>
/\ completed = {"CreateOrder", "ReserveInventory", "AuthorizePayment"}
/\ compensated = {"CancelOrder", "VoidPayment", "ReleaseInventory"}
/\ step = "Terminal"
/\ status = "Accepted"
/\ waiverRead = "ship-after-payment-timeout-v1"
/\ waiverCurrent = "ship-after-payment-timeout-v2"

38 states generated, 21 distinct states found, 1 states left on queue.
The depth of the complete state graph search is 11.
The average outdegree of the complete state graph is 1 (minimum is 0, the maximum 2 and the 95th percentile is 2).
Finished in 00s at (2026-06-16 18:22:55)
```

Exit: 12
