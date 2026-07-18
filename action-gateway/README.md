# Pendragon Custom GPT Action gateway

This Cloudflare Worker gives each focused Custom GPT Action a distinct API hostname while proxying
all operations to the same Cloud Run backend. It preserves the `X-API-Key` header and rewrites each
filtered OpenAPI document's `servers` entry to the hostname from which it was requested.

Current Action hosts:

| Host | Backend schema |
| --- | --- |
| `play-api.pendragon-chronicle.dwarvenbard.com` | `/openapi-gpt-play.json` |
| `dynasty-api.pendragon-chronicle.dwarvenbard.com` | `/openapi-gpt-dynasty.json` |
| `winter-api.pendragon-chronicle.dwarvenbard.com` | `/openapi-gpt-winter.json` |

## Add another Action

1. Add the hostname and backend schema path to `ACTION_SCHEMAS` in `worker/index.js`.
2. Add both a concrete `custom_domain` entry and an exact `hostname/*` zone route to
   `wrangler.jsonc`. The custom domain provisions TLS; the exact route outranks the player
   chronicle's broader wildcard Worker route.
3. Add a schema-selection test and update the Custom GPT setup documentation.
4. Run `npm ci`, `npm test`, and `npx wrangler deploy --config wrangler.jsonc --dry-run`.
5. Deploy through GitHub Actions or Wrangler and verify `/openapi.json`, `/privacy`, and one
   authenticated read through the new hostname.

The gateway stores no API credential. ChatGPT supplies `X-API-Key` for operation calls, and the
Worker forwards it to Cloud Run. Never add the key to Worker variables, source, or OpenAPI schemas.
