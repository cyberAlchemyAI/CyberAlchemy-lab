# Ontology Lifecycle

Ontology Lifecycle keeps a record of the things in a knowledge map, the
connections between them, and how they change over time. It lets us rebuild the
map as it stood at a chosen point in its history.

An **ontology** is a structured description of a subject: what things exist,
what they mean, and how they relate. In CyberAlchemy, those things can include
products, projects, capabilities, and rules.

The **lifecycle** is how an entry is created, changed, taken out of use, or
removed from future use while keeping its history.

## Why we need it

A map of a system changes as our understanding changes. A capability gets a
clearer description. A product stops using it. Someone questions a claim.
Looking only at the latest map would hide the earlier versions and the reasons
for those changes.

Ontology Lifecycle keeps that history so we can answer questions such as:

- What did the map contain at this point?
- Which version of a concept does this connection refer to?
- Which evidence or review belongs to that version?
- Can we rebuild the same map from the recorded history?

It also lets different agents work from different recorded versions. One agent
can keep using the map it started with while another uses a newer map. The
first agent does not need to hold the shared state locked throughout its task.
When an agent wants to record a change, the write must still be checked and
coordinated. Keeping a stable view and changing shared history are separate
operations.

## A small example

Imagine a parcel delivery product called **Parcel Desk**. Its map contains a
capability called **Track a parcel**, with a connection from the product to the
capability.

Later, the team changes the capability's description. The system records the
new version and keeps the earlier one. A reader can rebuild the map from before
or after that change.

If the capability is taken out of use, the connection cannot remain active
while pointing to it. The map must remain consistent.

A review of the old description also stays attached to that old version.
The system does not silently treat it as a review of the new description.

These names are an illustration, not records created by this package.

## How it works

Each concept and each connection has its own lasting identity. Changes are
recorded as new entries in its history. The code calls these entries **events**.

The system reads those events to rebuild the map. A graph, saved summary, or
view for a particular task is a result of that process. The recorded history
allows those results to be rebuilt.

It keeps two kinds of history separate:

- **Meaning:** what a concept or connection says, and whether it is in use.
- **Review and evidence:** where the information came from, how it can be
  questioned, and which version an assessment concerns.

## What happens when something leaves the map

| State | Meaning |
| --- | --- |
| Active | Included in the usable map. |
| Retired | Out of use for now. It can become active again through a new recorded change. |
| Removed | No further meaning or lifecycle changes under that identity. Its earlier history remains available. |

An active connection needs active concepts at both ends. Being active says
that an entry is available in the map; approval and confidence are separate
questions.

## Where to read next

- [Architecture](ARCHITECTURE.md) explains the main parts, the path a change
  follows, and how a reader gets a view of the map.
- [Relationships and the wider Lab](RELATIONSHIP-INTEGRATION.md) explains how
  this fits the newer rules for connections between Lab records.
- [The Rust implementation](runtime/src/lib.rs) contains the working history
  and reconstruction code.
- [The graph read-model candidate](runtime-candidates/cal-ontology-graph-read-model/v1/README.md)
  explores faster lookup and navigation through a rebuilt map.

## Where the work stands

The folder includes working Rust code, recorded checks, and several experiments.
There is also a recorded adoption of one exact version of the library and a
past execution of a local command-line tool.

Those records have specific scopes. They do not tell us that a service is
running now, or that every newer Lab relationship rule is enforced by this
library. The [architecture guide](ARCHITECTURE.md#implementation-and-recorded-checks)
links the relevant evidence and explains these limits.

This guide was checked against repository source on **2026-11-02**.
