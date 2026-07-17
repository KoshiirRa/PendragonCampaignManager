# ChatGPT Actions guide

This API is the persistent campaign memory used by a Pendragon Gamemaster. ChatGPT should read the OpenAPI schema for exact request and response fields, then use the rules and workflows below when selecting actions.

For step-by-step configuration in the Custom GPT editor, see [Connect a Custom GPT to the Pendragon Campaign API](custom-gpt-setup.md).

## Action configuration

- OpenAPI URL: `https://pendragon-campaign-api-wetwnuz4jq-uc.a.run.app/openapi.json`
- Authentication type: API key
- Authentication location: custom header
- Header name: `X-API-Key`
- Store the key in the GPT Action authentication settings. Never place it in GPT instructions, knowledge files, URLs, or conversation messages.

The API key grants GM-level access to the current deployment. Do not expose `gm_only` material when responding in a player-facing context.

## Core operating rules

1. Select a campaign first and retain its returned `id` as `campaign_id`.
2. Never guess UUIDs. Resolve existing records with list operations or create the record first.
3. Use the central event timeline for significant facts such as births, deaths, marriages, trait changes, Glory, battles, transfers, and oaths.
4. Treat events and historical ledgers as append-only. Correct a fact with a superseding or corrective record instead of deleting history.
5. Use in-game years for chronology. Preserve uncertainty in narrative text and certainty/scope fields rather than inventing exact dates.
6. Keep player knights and NPCs in the shared character model; distinguish them with `kind`.
7. Honor `scope`: `gm_only` is secret, `players` is player knowledge, and `shared` is suitable for both projections.
8. Before a multi-step write, identify the required parent IDs and explain any missing information to the GM.

## Recommended workflows

### Start a campaign

1. `list_campaigns` to avoid duplicates.
2. `create_campaign` if needed.
3. Create locations, characters, and the initial session.
4. Record the opening event and any initial status or ownership ledgers.

### Record a session

1. Create the session.
2. Create important events in chronological order.
3. Add dice logs for consequential rolls.
4. Add trait, skill, passion, status, Glory, manor, or family records linked to the relevant event where the schema supports it.
5. Preserve GM-only notes separately from player-visible facts.

### Record ancestral history

1. Resolve or create the family.
2. Resolve the ancestor character when the entry belongs to a known person.
3. Create a source reference once per source and edition.
4. Add the family-history entry with its year range, realm, source locator, summary, roll information, and scope.
5. Supply ancestral Glory only when an ancestor character is present; the API creates the linked event and Glory ledger record atomically.
6. Use `before_year=480` when retrieving the pre-480 family timeline.

### Resolve an inheritance

1. Record or resolve the decedent and death event.
2. Open an inheritance case.
3. Register possible heirs and their claim status.
4. Create the transfer event.
5. Record each manor transfer. The API closes the current manor tenure and opens the beneficiary's inherited tenure in one transaction.

## Error recovery

- `401`: the Action lacks the correct `X-API-Key`.
- `404`: an ID does not exist in the selected campaign; list the relevant records and retry with a real ID.
- `409`: the requested record conflicts with campaign history, often an existing current relationship or ownership period. Inspect current records instead of retrying blindly.
- `422`: request fields are invalid or incomplete. Read the validation details and correct the payload.
- `503` from `/ready`: database connectivity is unavailable; do not continue writes until readiness returns.

## Sources of truth

- Live machine-readable schema: `/openapi.json`
- Versioned schema snapshot: `docs/openapi.json`
- Domain design and table semantics: `docs/schema.md`
- ER relationships: `docs/er-diagram.md`
- Developer API notes: `docs/api.md`
