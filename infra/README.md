# infra/

Deployment and infrastructure configuration.

Holds the deploy targets and infrastructure-as-config for the project. CI lives in
`.github/workflows/`; this folder is for the deploy-side config those workflows and
the platforms consume.

- **Fly.io** — backend hosting config (when we deploy — not yet).
- **Vercel** — frontend hosting config (when we deploy — not yet).
- **No secrets** — credentials live in the platform's secret store / GitHub Actions
  secrets, never committed here.

Deployment is out of scope for the foundational MVP (see `docs/mvp_scope.md`); this
folder exists so the deploy config has a home when that work lands.
