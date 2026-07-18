# Frontend deployment

The player chronicle is a vinext/React application deployed as the Cloudflare Worker
`pendragon-campaign-chronicle`. Production reads the FastAPI player-view projection at request time;
database changes do not require rebuilding the frontend.

## Request flow

1. A player visits `{campaign-slug}.pendragon-chronicle.dwarvenbard.com`.
2. Cloudflare routes the hostname to the chronicle Worker.
3. The server-side `/api/campaign` route extracts the campaign slug from the hostname.
4. The Worker requests `/api/v1/campaigns/by-slug/{slug}/player-view` from FastAPI using the secret
   `X-API-Key` header.
5. The browser receives only the player-safe projection.

`PENDRAGON_CAMPAIGN_ID` remains a fallback for requests without a recognized campaign subdomain.
The API key must never be exposed through a public environment variable or client-side bundle.

## Cloudflare configuration

Production settings live in `frontend/wrangler.production.jsonc`:

- Worker: `pendragon-campaign-chronicle`
- API origin: the production Cloud Run service
- campaign domain: `pendragon-chronicle.dwarvenbard.com`
- wildcard route: `*.pendragon-chronicle.dwarvenbard.com/*`
- concrete custom domain: `salisbury.pendragon-chronicle.dwarvenbard.com`

The wildcard DNS record must be proxied through Cloudflare. A wildcard Worker route handles request
routing, but certificate coverage for a nested hostname is a separate concern. Register each live
campaign hostname as a concrete Worker custom domain unless the zone has another certificate product
that explicitly covers the nested wildcard. The concrete custom domain provisions the required TLS
certificate for Salisbury.

Do not attach a production campaign hostname to the retained private Sites prototype. A Sites custom
domain takes ownership of the hostname and can return the private “Sign in required” page before the
production Worker handles the request. The old Salisbury Sites binding was removed during the
Cloudflare cutover.

## GitHub Actions

`.github/workflows/deploy-frontend.yml` runs for relevant pushes to `main` and can also be started
manually. It:

1. installs Node.js 22.13 and npm 11.6.2;
2. installs the locked dependencies with `npm ci`;
3. runs ESLint;
4. builds the vinext Worker and static assets;
5. deploys with `wrangler.production.jsonc`;
6. binds `PENDRAGON_API_KEY` to the newly deployed Worker version.

The repository must contain these Actions secrets:

| Secret | Purpose |
| --- | --- |
| `CLOUDFLARE_API_TOKEN` | Account API token for Worker script deployment and route management |
| `PENDRAGON_API_KEY` | FastAPI credential bound only to the server-side Worker runtime |

The Cloudflare account ID is non-secret deployment configuration and is declared in the workflow.

## Adding a campaign hostname

Synchronizing a new campaign creates the data needed for slug-based lookup, but it does not by itself
provision a TLS certificate. Before giving players a new hostname:

1. confirm the campaign has a unique API slug;
2. add `{slug}.pendragon-chronicle.dwarvenbard.com` as a concrete custom-domain route in
   `frontend/wrangler.production.jsonc`;
3. merge the change to `main` and allow GitHub Actions to deploy it;
4. verify both the page and `/api/campaign` return HTTP 200 for the new hostname.

The existing proxied wildcard DNS record means a separate DNS record is not normally required for
each slug. The explicit custom-domain entry is currently required for certificate issuance.

## Verification

After deployment, verify the page and live projection:

```powershell
$baseUrl = "https://salisbury.pendragon-chronicle.dwarvenbard.com"
(Invoke-WebRequest $baseUrl -UseBasicParsing).StatusCode
(Invoke-WebRequest "$baseUrl/api/campaign" -UseBasicParsing).StatusCode
```

Both requests should return `200`. The API response should identify the expected campaign and contain
player-safe events, families, and manors.

## Troubleshooting

- **Private ChatGPT sign-in page:** remove the hostname from the private Sites project's custom
  domains, then redeploy the Worker so Cloudflare can claim the hostname and issue its certificate.
- **TLS secure-channel or certificate error:** confirm a concrete Worker custom domain exists and
  wait for certificate provisioning to complete.
- **401 from the backend path:** confirm the Actions secret `PENDRAGON_API_KEY` is current and that
  the post-deploy secret-binding step succeeded.
- **Missing generated module:** keep the `ESModule` rules in `wrangler.production.jsonc`; vinext's
  server imports generated modules such as `__vite_rsc_assets_manifest.js`.
- **`npm ci` lock mismatch:** regenerate and commit `frontend/package-lock.json` using the npm version
  pinned by the deployment workflow.
