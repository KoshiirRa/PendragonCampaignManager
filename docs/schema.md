# Schema: foundation slice

## Design decisions

- Every campaign-owned record carries `campaign_id`; this makes tenant boundaries explicit and supports many simultaneous campaigns.
- Campaign deletion is archival. Historical records use restrictive foreign keys and are never cascaded through campaign deletion.
- Sessions are numbered within a campaign and may span an in-game year range.
- `events` is the chronological backbone. Domain records added in later slices will reference the event that caused them.
- Recorded events are append-only at the service layer. Corrections create another event using `supersedes_event_id`.
- `event_links` provides indexed, role-aware links from an event to any domain entity without duplicating entity state.
- Dice rolls preserve the expression, individual dice, modifier, total, target, and interpreted outcome.
- Pendragon dates can be narratively uncertain, so `in_game_year` is sortable while `in_game_date` preserves human-readable detail.

## Current tables

| Table | Purpose |
|---|---|
| `campaigns` | Multi-campaign root and configuration |
| `campaign_sessions` | Real-world play sessions and their in-world range |
| `events` | Ordered, historical campaign timeline |
| `event_links` | Polymorphic event-to-entity participation links |
| `dice_logs` | Immutable audit trail of resolved rolls |

## Character and estate slice

Characters use one table for player knights and NPCs so relationships, events, ownership, and lineage can reference a single identity. `kind` distinguishes their campaign role; it does not divide them into incompatible entity types. Foundry UUIDs are unique within a campaign and serve only as external mappings.

Traits, skills, passions, Glory, and manor improvements use append-only ledgers. Current values are reconstructed by ordering effective year, sequence, and recording time. Corrections therefore add entries rather than rewriting earlier campaign history.

Foundry synchronization preserves the source Item PID or UUID in nullable `source_key` columns on
trait definitions, skill definitions, and character passions. Partial unique indexes keep those
external identities unique without requiring manually entered records to have an external key.
Snapshot synchronization compares against the latest ledger row and records only changed values.
Foundry's calculated total Glory is converted into a signed reconciliation entry rather than
replacing the Glory ledger.

Knowledge-bearing records use `knowledge_scope`:

- `gm_only` is restricted to the Gamemaster;
- `players` is legitimate player knowledge;
- `shared` is suitable for both archive projections.

The API defaults to excluding GM-only notes and Glory entries. Authentication roles will ultimately determine whether `include_gm` is honored; the current development key must be treated as GM-level access.

Locations form a campaign-scoped hierarchy and may also have graph connections for roads, borders, and routes. A manor is a specialized one-to-one record attached to a location of kind `manor`. Tenure periods preserve holder history, while a partial unique index prevents two open-ended current holders.

| Table | Purpose |
|---|---|
| `characters` | Shared identity for player knights and NPCs |
| `character_status_ledger` | Birth/death/missing/current-status history |
| `character_notes` | Append-only, knowledge-scoped character notes |
| `trait_definitions` | Campaign trait/opposed-trait catalog |
| `character_trait_ledger` | Historical paired trait values |
| `skill_definitions` | Campaign skill catalog |
| `character_skill_ledger` | Historical skill values |
| `character_passions` | Named, scoped character passions |
| `character_passion_ledger` | Historical passion values |
| `glory_ledger` | Signed, categorized Glory awards and corrections |
| `locations` | Hierarchical campaign geography |
| `location_connections` | Non-hierarchical routes and relationships |
| `manors` | Manor-specific economic attributes |
| `manor_tenures` | Effective-dated character tenure history |
| `manor_improvements` | Stable improvement identities |
| `manor_improvement_ledger` | Improvement status and economic history |

Cross-domain integrity that cannot be expressed by a simple foreign key (for example, confirming a session and event belong to the same campaign) is enforced in the service layer. Supabase Row Level Security policies will be introduced with authentication, rather than shipping permissive placeholder policies.

The attached legacy archive design treated Markdown as canonical. In this backend, normalized PostgreSQL records are canonical; future Markdown and ZIP archives will be reproducible, scope-filtered exports.

## Families, inheritance, and ancestral history

Families are stable campaign entities, while membership, parentage, and marriage are effective-dated historical records. Parentage supports biological, adoptive, foster, and user-defined relationship types without forcing uncertain genealogy into a confirmed fact; `certainty` and `knowledge_scope` preserve that distinction.

Inheritance is represented as a case with candidate heirs and explicit asset transfers. Recording an inherited manor closes its current tenure and opens the beneficiary's tenure in the same database transaction, linked to the transfer event.

`family_history_entries` supports year-by-year ancestral histories before or after 480. Every entry creates a central event and may link an ancestor, realm, source citation, dice log, and Glory ledger entry. Source title, edition, locator, summary, roll results, and arbitrary metadata are user-entered fields. The application contains no sourcebook prose or built-in sourcebook tables.

| Table | Purpose |
|---|---|
| `families` | Named dynasties and branches within a campaign |
| `family_memberships` | Effective-dated character affiliation |
| `character_parentage` | Typed and certainty-qualified ancestry links |
| `marriages` | Effective-dated unions with start/end events |
| `inheritance_cases` | Estate resolution following a death |
| `inheritance_heirs` | Candidate, designated, accepted, or rejected claims |
| `inheritance_manor_transfers` | Event-backed inherited manor transfers |
| `source_references` | Campaign-owned citations to books or other sources |
| `family_history_entries` | Event-backed ancestral timeline entries and optional Glory |
