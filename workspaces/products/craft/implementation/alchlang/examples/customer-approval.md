# Customer approval domain

```alchlang
domain customer-approval "Customer approval"
owner customer-domain-owner

entity Customer:
  customerId: identifier required
  riskScore: integer required
  status: string required
  amount: decimal required

actor CreditOperator

states Customer:
  initial pending
  pending -> approved
  pending -> rejected
  approved -> released when approved-release emits credit-released

rule high-risk:
  A customer with riskScore <= 472 is considered high-risk.

rule approved-release:
  customer.status == approved

boundary credit-release-authority:
  owner customer-domain-owner

permission release-credit:
  actor CreditOperator
  action ReleaseCredit
  when approved-release
  boundary credit-release-authority

action ReleaseCredit:
  actor CreditOperator
  subject Customer
  input amount
  requires approved-release
  permission release-credit
  boundary credit-release-authority
  emits credit-released

event credit-released:
  subject Customer
  payload customerId, amount
  boundary credit-release-authority

example approved-release:
  kind positive
  expected released
  rules approved-release
```
