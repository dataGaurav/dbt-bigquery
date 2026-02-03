# dbt CI/CD Workflow

## Environments

Two environments, each with its **own BigQuery project**:

| Environment | Use              | BigQuery project      |
|-------------|------------------|------------------------|
| **dev**     | CI (PRs), local  | `DBT_BQ_PROJECT_DEV`   |
| **prod**    | CD (after merge) | `DBT_BQ_PROJECT_PROD`  |

## High-level flow

| Phase      | Trigger                                  | Actions                 | Warehouse        |
|------------|------------------------------------------|-------------------------|------------------|
| **CI**     | PR opened/updated → `main` or `production` | `dbt compile`, `dbt test` | **Dev** BigQuery |
| **Review** | —                                        | Manual approval by leads | (branch protection) |
| **CD**     | Merge to `main` or `production`           | `dbt run`, `dbt test`   | **Prod** BigQuery |

- **CI** runs against the **dev** BigQuery project so PRs never touch prod.
- **Review** is enforced via GitHub branch protection.
- **CD** runs against the **prod** BigQuery project after merge.

## Setup

### 1. GitHub variables (required)

Set your BigQuery project IDs (and optionally datasets) under **Settings → Secrets and variables → Actions → Variables**:

| Variable              | Required | Description                    |
|-----------------------|----------|--------------------------------|
| `DBT_BQ_PROJECT_DEV`  | Yes      | BigQuery project ID for **dev** |
| `DBT_BQ_PROJECT_PROD` | Yes      | BigQuery project ID for **prod** |
| `DBT_BQ_DATASET_DEV`  | No       | Dataset in dev project (default: `dbt_dev`) |
| `DBT_BQ_DATASET_PROD` | No       | Dataset in prod project (default: `dbt_prod`) |

### 2. GitHub secrets (required)

- **`GCP_SA_KEY_DEV`** – Service account key JSON for the **dev** BigQuery project (used in CI).
- **`GCP_SA_KEY_PROD`** – Service account key JSON for the **prod** BigQuery project (used in CD).

Create one service account per project in GCP (IAM → Service accounts → Keys), then add each key’s full JSON as a repository secret.

### 3. Branch protection (review phase)

On `main` and/or `production`:

- **Require a pull request** before merging.
- **Require approvals** (e.g. 1) from your authorized leads.
- Optionally **require status checks** and select the “CI (compile & test)” workflow so merge is blocked until CI passes.

## Local development

Use a `profiles.yml` (not committed) with **dev** and **prod** targets, each pointing at the correct BigQuery project ID, dataset, and keyfile. Example:

```yaml
default:
  target: dev  # or prod
  outputs:
    dev:
      type: bigquery
      method: service-account-json
      project: your-dev-project-id
      dataset: dbt_dev
      keyfile: /path/to/dev-sa-key.json
    prod:
      type: bigquery
      method: service-account-json
      project: your-prod-project-id
      dataset: dbt_prod
      keyfile: /path/to/prod-sa-key.json
```
