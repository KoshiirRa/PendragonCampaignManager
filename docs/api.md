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
