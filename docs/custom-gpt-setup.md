# Connect a Custom GPT to the Pendragon Campaign API

This guide connects a private Custom GPT Gamemaster to the deployed Pendragon Campaign API through GPT Actions.

## What the connection does

ChatGPT calls the API from OpenAI's servers over HTTPS. The request reaches Cloud Run, FastAPI validates the API key, and the API reads or writes campaign data in Supabase.

```text
Custom GPT
  -> HTTPS request with X-API-Key
  -> Google Cloud Run
  -> FastAPI
  -> Supabase PostgreSQL
```

This is a server-to-server connection. Browser CORS settings for the Foundry VTT sites do not need an OpenAI or ChatGPT origin.

## Required values

- API server: `https://pendragon-campaign-api-wetwnuz4jq-uc.a.run.app`
- OpenAPI schema: `https://pendragon-campaign-api-wetwnuz4jq-uc.a.run.app/openapi.json`
- Authentication header: `X-API-Key`
- Authentication value: the latest enabled version of the `pendragon-api-key` Google Cloud secret

Never store the API key in this repository, GPT instructions, GPT knowledge files, the OpenAPI schema, a URL, or a conversation.

## Retrieve the API key

1. Open [the API-key secret in Google Secret Manager](https://console.cloud.google.com/security/secret-manager/secret/pendragon-api-key/versions?project=pendragon-campaign-manager-api).
2. Open the latest enabled secret version.
3. Select **View secret value**.
4. Copy the value temporarily for entry into the GPT Action authentication dialog.
5. Clear it from the clipboard after the Action is saved.

Do not send the value in chat or paste it into any GPT text field.

## Create the GPT Action

1. Open ChatGPT and edit the Custom GPT.
2. Open **Configure**.
3. Find **Actions** and select **Create new action**.
4. Choose **Import from URL**.
5. Enter the OpenAPI schema URL:

   ```text
   https://pendragon-campaign-api-wetwnuz4jq-uc.a.run.app/openapi.json
   ```

6. Confirm that the editor detects the API operations without schema errors.
7. Open the Action's **Authentication** settings.
8. Select **API Key** authentication.
9. Select the custom-header option.
10. Set the header name to:

    ```text
    X-API-Key
    ```

11. Paste the secret value into the API-key field.
12. Save the authentication configuration and the GPT.

The OpenAPI schema declares the same `X-API-Key` security scheme. The key is injected into Action requests by ChatGPT and is not exposed to the model as ordinary instruction text.

## Recommended GPT instructions

Add behavioral guidance similar to the following to the Custom GPT's instructions. Do not include credentials.

```text
Use the Pendragon Campaign API as the canonical persistent memory for campaign facts.
Select the correct campaign before reading or writing campaign-scoped records.
Never invent UUIDs; list or create records to obtain valid IDs.
Treat events, ledgers, family history, inheritance transfers, and other historical records as append-only.
Record important narrative changes as events and link related domain records when supported.
Do not disclose gm_only information in player-facing responses.
Confirm uncertain campaign facts with the GM instead of fabricating them.
```

The full operating guidance is in [ChatGPT Actions guide](chatgpt-actions.md).

## Test the connection

Test read-only behavior first in the GPT Preview window.

1. Ask: `List the available Pendragon campaigns.`
2. Approve the Action call if ChatGPT requests confirmation.
3. Confirm that the `list_campaigns` operation succeeds.
4. Ask ChatGPT to describe the selected campaign without making changes.
5. Only after reads work, test a reversible development write such as creating a clearly named test campaign or note.

Remove any test record through the appropriate archival operation rather than deleting historical campaign data directly.

## Troubleshooting

### Schema import fails

- Confirm that the schema URL opens without authentication.
- Use the `/openapi.json` URL, not `/docs`.
- Check that the GPT workspace permits Actions and the Cloud Run domain.
- Re-import the schema after a deployment that changes API operations.

### `401 Missing or invalid API key`

- Confirm the Action uses API-key authentication.
- Confirm the custom header is exactly `X-API-Key`.
- Re-enter the latest enabled Secret Manager value.
- Do not add `Bearer` before the key.

### `404 Not Found`

- Confirm the Action is using the deployed server from the schema.
- For campaign records, list entities and use a real UUID from the selected campaign.

### `409 Conflict`

The requested change conflicts with existing historical state, such as a current manor holder or family relationship. Inspect the existing records before attempting a correction.

### `422 Unprocessable Entity`

The request body is missing required fields or contains invalid values. Review the validation response and the operation schema, then correct the request rather than retrying unchanged.

### `503 Service Unavailable`

Check [API readiness](https://pendragon-campaign-api-wetwnuz4jq-uc.a.run.app/ready). Do not attempt writes until it returns `{"status":"ready"}`.

## Security and publication

- The current API key grants GM-level access. Keep the GPT private unless its sharing model and authentication have been reviewed.
- Rotate the Google secret if the key is exposed, then update the GPT Action authentication value.
- A GPT published publicly or by link may require a valid privacy-policy URL.
- User-specific access and player-safe authorization should use scoped credentials or OAuth in a future security phase; the shared GM API key is intended for the private development deployment.

## Related documentation

- [Live OpenAPI schema](https://pendragon-campaign-api-wetwnuz4jq-uc.a.run.app/openapi.json)
- [Versioned OpenAPI snapshot](openapi.json)
- [ChatGPT Actions operating guide](chatgpt-actions.md)
- [API notes](api.md)
- [Cloud Run deployment](cloud-run.md)
- [Schema design](schema.md)
