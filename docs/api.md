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
- location list, create, read, update, and archive;
- manor creation, tenure history, and improvement history.

Historical timeline events and dice logs intentionally have no update or delete endpoints. Corrections are appended as superseding events.
The same rule applies to character-value, Glory, tenure, and improvement ledgers.
# Family and ancestral-history API

Family endpoints live under `/api/v1/campaigns/{campaign_id}`. Create and list families, add memberships and parentage, record marriages, open inheritance cases, register heirs, and transfer manors through the corresponding nested resources.

Ancestral entries use `POST /families/{family_id}/history`. The service creates the central event automatically and can also create a linked Glory ledger entry when `glory_amount` and `ancestor_character_id` are supplied. Use `GET /families/{family_id}/history?before_year=480` for the pre-480 timeline.

Sources are campaign-owned records at `/source-references`; `source_locator` on each history entry can hold a page, table, section, URL, or other user-defined locator.
