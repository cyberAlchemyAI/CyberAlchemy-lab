---- MODULE ToolchainSmoke ----
EXTENDS Naturals

VARIABLE x

Init == x = 0

Next == IF x = 0 THEN x' = 1 ELSE x' = 0

TypeOK == x \in {0, 1}

====
