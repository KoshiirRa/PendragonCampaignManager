# Pendragon Campaign Manager Player Guide

Pendragon Campaign Manager preserves the history of a long-running Pendragon campaign outside Foundry VTT. It records characters, families, Glory, possessions, horses, wounds, estates, and major events so that facts remain consistent across sessions and generations.

## What players need to do

Players do not need a database account, API key, Supabase account, or Google Cloud account. The Gamemaster configures the connection and controls synchronization.

Keep your Foundry Actor accurate and tell the Gamemaster when important information changes. This includes:

- character name, birth year, culture, religion, and other biographical details;
- Traits, Passions, Skills, statistics, and Glory;
- equipment, armor, weapons, and horses;
- parents, spouse, children, and other family members;
- History entries and wounds;
- manor ownership and annual economic results.

The Gamemaster can then use the Actor header controls to synchronize the character.

## Historical records

The campaign manager favors historical records over replacing old information. A new Trait value, wound state, horse owner, manor holder, or annual economic outcome becomes another dated entry in the campaign history.

This makes it possible to answer questions such as:

- What was this knight's Sword Skill in 490?
- When did this horse change owners?
- Who held this manor before the current knight?
- Which relatives were alive during a particular year?
- How was the knight's current Glory accumulated?

Synchronizing an unchanged Actor again should not create duplicate records.

## Character and family information

Foundry family Items become campaign characters so that parents, spouses, and children have durable identities. Parentage, marriages, family membership, deaths, and qualifying inheritance claims are stored separately as historical relationships.

The public Description field on a family Item becomes player-visible character information. The GM Info field remains private.

Book of Sires and other ancestral material belongs to the family's ancestral timeline rather than the individual Actor's History tab.

## Glory

Glory is maintained as a ledger. Foundry's total Glory is reconciled against that ledger without creating a second award for every imported History entry.

History Item Glory is retained as historical provenance. The ledger remains the authoritative accounting record.

## Winter Phase and wounds

Foundry History Items become dated campaign events. History Items marked with the `winter` source also identify participation in that year's Winter Phase.

Wounds are append-only state records. Treating or otherwise changing a wound adds a new dated state rather than erasing the earlier injury.

Births and child deaths are preserved through family and character-status history.

## Manors

The Gamemaster can create and manage a linked knight's manor from the Actor header. The campaign manager can preserve:

- ownership and tenure history;
- assized rent and population;
- annual Stewardship and economic outcomes;
- treasury income and expenses;
- improvements, investments, resources, and livestock;
- household professionals and soldiers;
- defenses and Defensive Value.

Players should provide the Gamemaster with the agreed results of rolls and choices. The database records those outcomes; it does not replace table rulings or automatically reproduce sourcebook procedures.

Estate money is recorded in Librum, with 240 denarii to one Librum. Currency labels do not refer to modern British pounds.

## Privacy

Player-visible descriptions and campaign facts are kept separate from GM-only information. GM Info, private notes, secrets, and restricted source material are not intended to appear in player-facing responses.

If private information appears where players can see it, notify the Gamemaster before continuing to use or share that view.

## Troubleshooting

If a change is missing:

1. Confirm that the Foundry Actor or Item was saved.
2. Ask the Gamemaster to synchronize the Actor again.
3. Tell the Gamemaster which field and campaign year are affected.

If the same person or object appears twice, do not delete either record. Tell the Gamemaster so the external identity mapping can be corrected without losing history.

Players should never be asked to share or enter the Campaign Manager API key.
