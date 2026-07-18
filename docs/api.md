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

# Winter Phase and character history API

List or create annual records at `/campaigns/{campaign_id}/winter-phases`; list participants beneath `/winter-phases/{phase_id}/participants`. Foundry History Items are available at `/characters/{character_id}/history`, and append-only wound states at `/characters/{character_id}/wounds`.

During Foundry synchronization each History Item becomes its own central Event and normalized history entry. Items whose source is `winter` create or reuse the campaign/year Winter Phase and attach the character as a participant. `reported_glory` preserves what the History Item displayed, but does not independently award Glory: snapshot total reconciliation remains authoritative and prevents double counting. History and GM Info use separate player-visible and GM-only records.

# Manor economics and household API

Create and list annual results at `/manors/{manor_id}/annual-resolutions`; creation automatically generates the central Event and a net treasury entry. Manual income, costs, construction payments, charity, ransoms, and other transactions use `/manors/{manor_id}/treasury`. Assets and their state histories use `/assets` and `/assets/{asset_id}/ledger`; household professionals use `/household`; ordered defensive structures use `/defenses`. Tenures, improvements, and their append-only ledgers all provide list endpoints so clients can reconstruct estate history before appending another record.

The API stores user-entered outcomes and modifiers rather than copyrighted sourcebook lookup tables. Clients calculate or select the outcome, while the backend validates campaign boundaries and preserves the resulting history.

# Squire service API

The Foundry character snapshot accepts a complete `squires` collection. Each stable source key creates or reuses an NPC identity, opens or closes effective-dated knight service, and appends changed yearly state. Repeating an unchanged snapshot creates no records. Resolve squire records to their NPC characters with `/squires`, list a knight's history at `/characters/{character_id}/squire-services`, and list development at `/squires/{squire_id}/states`.

Ancestral entries use `POST /families/{family_id}/history`. The service creates the central event automatically and can also create a linked Glory ledger entry when `glory_amount` and `ancestor_character_id` are supplied. Use `GET /families/{family_id}/history?before_year=480` for the pre-480 timeline.

Sources are campaign-owned records at `/source-references`; `source_locator` on each history entry can hold a page, table, section, URL, or other user-defined locator.
# Player-facing projection

`GET /api/v1/campaigns/{campaign_id}/player-view` returns the campaign year,
player-visible chronicle events, families and memberships, and manors with their
current holders, improvements, special features, and defenses. GM-only records
are excluded. The endpoint still requires the API key and is intended to be
called by a trusted server-side frontend proxy, never directly from browser code.

`GET /api/v1/campaigns/by-slug/{slug}/player-view` provides the same projection for
hostname-based campaign routing. Campaign slugs are unique and become the first
label beneath the configured chronicle domain.
