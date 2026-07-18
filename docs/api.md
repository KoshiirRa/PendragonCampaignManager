# API

FastAPI generates the authoritative OpenAPI document at `/openapi.json` and interactive documentation at `/docs`.

The first slice exposes:

- campaign list, create, read, update, and archive;
- session list, create, and update within a campaign;
- timeline event list and create, with optional in-game year filtering;
- dice-log creation.

The character and estate slice additionally exposes:

- player-knight and NPC list, create, read, update, and archive;
- knowledge-scoped character notes;
- campaign trait and skill definitions;
- append-only trait, skill, passion, and Glory entries;
- computed Glory summaries;
- idempotent Foundry VTT character snapshots for traits, skills, passions, and Glory;
- location list, create, read, update, and archive;
- manor creation, tenure history, and improvement history.

Historical timeline events and dice logs intentionally have no update or delete endpoints. Corrections are appended as superseding events.
The same rule applies to character-value, Glory, tenure, and improvement ledgers.

## Foundry character synchronization

`POST /api/v1/campaigns/{campaign_id}/characters/{character_id}/foundry-snapshot` accepts the
current in-game year, core statistics, trait/skill/passion values, total Glory, inventory, and
horses. Stable Foundry PID
or Item UUID source keys identify definitions across repeated requests. The service appends only
values that differ from the latest ledger state and reconciles Glory with a signed ledger entry.
An unchanged snapshot returns `changed: false` and creates no event or ledger rows.

Inventory items have normalized weapon and armour profiles. Quantity and equipped state are
historical ledger values; an item absent from a later complete inventory snapshot receives a
zero-quantity entry. Horses are durable identities with effective-dated ownership and append-only
statistics. A horse absent from a later complete horse snapshot closes its current ownership.

When a snapshot changes history, the service creates one `foundry_character_sync` event and links
every new ledger entry to it. This endpoint is intended for machine synchronization; ordinary
historical edits should continue to use the individual append-only ledger endpoints.
# Family and ancestral-history API

Family endpoints live under `/api/v1/campaigns/{campaign_id}`. Create and list families, add memberships and parentage, record marriages, open inheritance cases, register heirs, and transfer manors through the corresponding nested resources.

The Foundry snapshot endpoint also accepts `family_name`, `relatives`, and `is_heir`. Relative Item UUIDs become durable NPC identities. Repeated snapshots reuse those identities and do not duplicate memberships, parentage, marriages, or inheritance claims. A marriage without a year in Foundry begins at the first synchronized campaign year. An inheritance case is inferred only when the knight is marked as heir and a parent has a death year.

Relative `description` is synchronized to the NPC's public description. Relative `gm_description` is appended as a `gm_only` character note when its content changes; identical repeated snapshots do not duplicate the note.

Ancestral entries use `POST /families/{family_id}/history`. The service creates the central event automatically and can also create a linked Glory ledger entry when `glory_amount` and `ancestor_character_id` are supplied. Use `GET /families/{family_id}/history?before_year=480` for the pre-480 timeline.

Sources are campaign-owned records at `/source-references`; `source_locator` on each history entry can hold a page, table, section, URL, or other user-defined locator.
