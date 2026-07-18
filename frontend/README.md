# Campaign chronicle frontend

This directory contains the player-facing chronicle. It is a vinext/React application deployed to
Cloudflare Workers, with a private Sites deployment retained only as a prototype preview.

The current screen reads the representative development campaign from the FastAPI player-view
projection. Embedded representative records are retained as a fallback when the API is unavailable.

The County Salisbury map is a campaign-approved published reference supplied by the Gamemaster.
It is identified in the UI as circa 510. Earlier campaign years use separate annotations rather
than modifying the source cartography or presenting its later political labels as contemporaneous.
The campaign-approved national player map is integrated as a circa-510 kingdom overview with
Salisbury as the transition point into the detailed county map.

The Families and Places & Manors sections use representative records to prototype lineage trees,
inheritance context, holdings, household summaries, estate history, and map-linked manor browsing.
Manor records separately present improvements, special features, and defensive layers so the UI can
be evaluated before the final special-feature persistence model is designed.

## Local development

Use Node.js 22.13 or newer.

```powershell
npm install
npm run dev
```

Create a production build with:

```powershell
npm run build
```

## API integration

The frontend consumes the player-safe campaign projection rather than joining low-level domain
responses in the browser. FastAPI enforces visibility for chronicle, family, and manor data.

Never place the backend `X-API-Key` in frontend source or a browser-visible environment variable.

The server-side `/api/campaign` proxy expects `PENDRAGON_API_URL`,
`PENDRAGON_API_KEY`, and `PENDRAGON_CAMPAIGN_ID`. It requests the API's
player-safe projection on every page load and keeps the credential out of the browser.
Future private campaigns will require scoped player authentication; the current production
chronicle exposes only the player-safe read projection.

## Production deployment

`wrangler.production.jsonc` defines the production Worker, wildcard campaign route, and non-secret
runtime settings. `PENDRAGON_API_KEY` is stored as a Cloudflare Worker secret and is not present in
the repository. The GitHub Actions deployment requires a repository secret named
`CLOUDFLARE_API_TOKEN` with permission to deploy Workers and manage Worker routes.
