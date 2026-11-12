# Durable Project State → consumer views

Direction: exact durable sources and histories supply bounded consumer views; the view does not become a competing canonical state store.

Evidence: [Project State definition](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/project-state/v1/definition.json), [session freshness](../../../../implementation/lab-runtime/v2/lab_runtime/session.py) and [Craft ontology application](../../../../workspaces/products/craft/ontology/application/README.md).

Migration rule: preserve source identities and independent Project/ontology cursors, rebuild derived output from the selected cut, and invalidate stale sessions. Expired short-term notes are not copied into the new durable instance.
