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

Cross-domain integrity that cannot be expressed by a simple foreign key (for example, confirming a session and event belong to the same campaign) is enforced in the service layer. Supabase Row Level Security policies will be introduced with authentication, rather than shipping permissive placeholder policies.

