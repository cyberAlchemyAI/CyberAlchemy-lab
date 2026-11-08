# Connected operations: six applications, three genuine dependencies

The six business models serve different purposes. Ingestion prepares a permitted document index; RAG releases a cited answer from that exact index; support uses that answer to prepare a reviewed customer reply. CRM owns current contact preferences; marketing reads those preferences before preparing and scheduling a campaign. Invoice processing independently compares a bill with its purchase order and receipts before requesting an accounting draft.

`system.alch` connects these existing applications using the original read contracts. It does not copy an index, manufacture a RAG answer, duplicate CRM records or give one application another application's permission. The original producer still checks its saved work, current sources and actor before the consumer can use its output.

The child folders are modest copies of the canonical business-only source examples. They contain business models, permissions and environment identities, plus labelled fixtures; no application runtime, custom workflow handler, connector factory or handwritten join lives here. The profile library and generated system bootstrap supply that wiring.

Compile the six original profile selections into each child's selected `profiles/...` path, and compile `system.profile.json` into `profiles/system`. Use the enclosing `technical-profile-source` folder as the source root because the system source reuses `library.alch` and the existing contracts. Then use the matching CLI:

```sh
alchlang-generic generate-application-system --project system-project.json --out generated --accept-local-review local-example
```

The operator supplies actual Auth, private stores, model resources, documents, provider credentials and independent review inputs. Fixture provider/model responses are examples, not qualification. The generated system must preserve each child's identity, original state and source custody.

## Open questions

Real provider/model quality, deployment and publication remain unqualified. Local hosting, TDE and EVF remain deferred. The selected connected-application proof owns executed layouts, recovery cases and installation identities.
