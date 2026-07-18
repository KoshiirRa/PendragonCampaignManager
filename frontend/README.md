# Campaign chronicle frontend

This directory contains the player-facing chronicle. It is a vinext/React application deployed to
Cloudflare Workers. The earlier private Sites deployment remains available only at its Sites URL;
its Salisbury custom-domain binding was removed when production moved to Cloudflare.

The current screen reads live campaign data from the FastAPI player-view projection on every
request. Embedded representative records are retained only as a resilient design fallback when the
API is unavailable.

The County Salisbury map is a campaign-approved published reference supplied by the Gamemaster.
It is identified in the UI as circa 510. Earlier campaign years use separate annotations rather
than modifying the source cartography or presenting its later political labels as contemporaneous.
The campaign-approved national player map is integrated as a circa-510 kingdom overview with
Salisbury as the transition point into the detailed county map.

The Families and Places & Manors sections render the player-safe projection's lineage,
inheritance context, holdings, estate history, and map-linked manor data. Manor records present
persisted improvements, special-feature assets, and defensive layers separately. The embedded
representative dataset is displayed only if the live API request fails.

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
`PENDRAGON_API_KEY`, `PENDRAGON_CAMPAIGN_DOMAIN`, and `PENDRAGON_CAMPAIGN_ID`. For a recognized
subdomain it requests `/campaigns/by-slug/{slug}/player-view`; the campaign ID is the fallback when
the hostname does not provide a slug. It requests the API's player-safe projection on every page
load and keeps the credential out of the browser.
Future private campaigns will require scoped player authentication; the current production
chronicle exposes only the player-safe read projection.

## Production deployment

`wrangler.production.jsonc` defines the production Worker, wildcard campaign route, concrete
Salisbury custom domain, static assets, generated ES modules, and non-secret runtime settings.
`PENDRAGON_API_KEY` is stored as a Cloudflare Worker secret and is not present in the repository.

The GitHub Actions deployment requires these repository secrets:

- `CLOUDFLARE_API_TOKEN`: an account API token able to deploy Worker scripts and manage Worker
  routes for `dwarvenbard.com`;
- `PENDRAGON_API_KEY`: the backend API key, uploaded to the Worker after each deploy.

The secret-binding step intentionally runs after `wrangler deploy`. Publishing a new Worker version
without that final step leaves the server-side proxy unable to authenticate to FastAPI.

See [`docs/frontend-deployment.md`](../docs/frontend-deployment.md) for DNS, certificates, campaign
hostnames, CI behavior, verification, and troubleshooting.
