# Order operation with transactional Outbox effect

This domain declares the guarded operation and the event that its action adapter
may record in an Outbox. The adapter is responsible for persisting the order
change and the Outbox message in the same local database transaction.

```alchlang
domain order-outbox-operation "Order operation with Outbox effect"
owner order-domain-owner

entity OrderOperation:
  operationId: identifier required
  orderId: identifier required
  status: string required
  outboxMessageId: identifier required
  occurredAt: timestamp required
  payload: record required

entity OutboxMessage:

actor OrderService

states OrderOperation:
  initial pending
  pending -> committed when operation-pending emits outbox-message-recorded

rule operation-pending:
  status == pending

boundary order-transaction-authority:
  owner order-domain-owner

permission commit-order-with-outbox:
  actor OrderService
  action CommitOrderWithOutbox
  when operation-pending
  boundary order-transaction-authority

effect PersistOrderWithOutbox:
  pattern transactional-outbox
  binding sqlite-transactional-outbox
  writes OrderOperation, OutboxMessage
  emits outbox-message-recorded
  guarantee atomic-state-and-outbox
  on-failure rollback
  boundary order-transaction-authority

action CommitOrderWithOutbox:
  actor OrderService
  subject OrderOperation
  input operationId, orderId, outboxMessageId, occurredAt, payload
  requires operation-pending
  permission commit-order-with-outbox
  boundary order-transaction-authority
  emits outbox-message-recorded
  performs PersistOrderWithOutbox using sqlite-transactional-outbox

event outbox-message-recorded:
  subject OrderOperation
  payload operationId, orderId, outboxMessageId, occurredAt, payload
  boundary order-transaction-authority

example pending-order-operation:
  kind positive
  expected committed-with-outbox-message
  rules operation-pending
```
