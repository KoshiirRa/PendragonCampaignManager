# Google Cloud Run deployment

Cloud Run hosts the stateless FastAPI container. Supabase remains the PostgreSQL system of record. The same image is used for the web service and a finite migration job.

## Deployment order

The included `cloudbuild.yaml` performs these steps in order:

1. Build and push an immutable image to Artifact Registry.
2. deploy or update the `pendragon-campaign-api-migrate` Cloud Run Job;
3. execute `alembic upgrade head` and wait for success;
4. deploy the web service only after migrations succeed.

The service scales to zero, is capped at two instances for cost control, and listens on Cloud Run's injected `PORT`. `/health` is a process liveness endpoint. `/ready` verifies PostgreSQL connectivity without returning database details.

## Prerequisites

Install and authenticate the Google Cloud CLI, select a project, and enable billing. Choose a region close to the Supabase database; examples below use `us-central1`.

```powershell
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com
```

Create the Artifact Registry repository and runtime service account once:

```powershell
gcloud artifacts repositories create pendragon --repository-format=docker --location=us-central1
gcloud iam service-accounts create pendragon-campaign-api --display-name="Pendragon Campaign API"
```

Grant the runtime identity access only to the two required secrets after creating them:

```powershell
gcloud secrets add-iam-policy-binding pendragon-database-url --member="serviceAccount:pendragon-campaign-api@YOUR_PROJECT_ID.iam.gserviceaccount.com" --role="roles/secretmanager.secretAccessor"
gcloud secrets add-iam-policy-binding pendragon-api-key --member="serviceAccount:pendragon-campaign-api@YOUR_PROJECT_ID.iam.gserviceaccount.com" --role="roles/secretmanager.secretAccessor"
```

Cloud Build's service account also needs permission to push images, deploy Cloud Run services and jobs, execute the migration job, and act as the runtime service account. Assign those roles through IAM using least privilege for your Google Cloud organization.

## Secrets

Create secrets through the Google Cloud Console or CLI. Never place their values in Git, `cloudbuild.yaml`, build substitutions, or command history.

- `pendragon-database-url`: SQLAlchemy async URL for the Supabase session pooler or direct database endpoint, beginning with `postgresql+asyncpg://`.
- `pendragon-api-key`: a cryptographically random development API key.

Cloud Run resolves both secrets before starting the container. Production startup fails closed if `API_KEY` is absent.

The initial API-key mechanism protects development deployments but is not the final player authentication model. A browser user who can inspect a request can see its key. Replace it with world registration and scoped user credentials before exposing player-accessible campaign data.

## Build and deploy

Submit from the repository root. Supply the exact Foundry origin that browsers use, without a trailing slash:

```powershell
gcloud builds submit --config cloudbuild.yaml --substitutions="_REGION=us-central1,_CORS_ORIGINS=https://foundry.example.com"
```

The deployment currently allows browser requests from the two configured Foundry origins:

- `https://pendragon.dwarvenbard.com`
- `https://foundry.starfleetengineers.com`

Cloud Build uses an alternate delimiter for its environment-variable flag so the comma-separated `CORS_ORIGINS` value reaches FastAPI unchanged. Add future Foundry origins to `_CORS_ORIGINS` without paths or trailing slashes.

After deployment:

```powershell
$serviceUrl = gcloud run services describe pendragon-campaign-api --region=us-central1 --format="value(status.url)"
Invoke-RestMethod "$serviceUrl/health"
Invoke-RestMethod "$serviceUrl/ready"
```

The service permits unauthenticated Cloud Run invocation because Foundry runs in end-user browsers that do not possess Google IAM identities. Application routes still require `X-API-Key`; only operational and OpenAPI routes are public.

## Rollback and migration safety

Cloud Run can route traffic back to an earlier service revision, but database migrations are forward-only operationally. Do not run Alembic downgrades against Supabase during an automated rollback. Make schema changes backward-compatible across at least one application revision, and correct deployed schemas with new migrations.

Do not run the pipeline against a populated project until the baseline migration has been tested against a disposable Supabase project.
