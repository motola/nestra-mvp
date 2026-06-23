# AlphaCon AI — Technology Registration Checklist

*Every account you need to create before development starts. Ordered so each unlocks the next.*

---

## How to use this list

Knock them out in a single sitting (~2 hours). Do them in order — later items often depend on earlier ones (e.g., Cloudflare needs the domain registered first; Stripe needs the company entity).

For each, the checklist tells you:
- Why we need it
- What tier to start on (always the cheapest viable option)
- What to write down (account ID, API key, etc.) for the backend `.env` later

**Never** commit any of these credentials to the repo. They go in `.env.local` (in `.gitignore`) for development, and in your hosting provider's secret manager for deployment.

---

## Phase 0 — Foundation (do these first, all free)

### 1. GitHub Organization (or use your existing user)
- **Why:** Source code, CI, issue tracking, branch protection
- **Tier:** Free (private repos are free for organizations and individuals now)
- **Action:** Create org `alphacon-ai` (or use your existing GitHub identity if you prefer for MVP)
- **Write down:** Organization name (used in CI workflow files)

### 2. Domain registration
- **Why:** Need a real domain before SSL/email/Cloudflare configuration
- **Tier:** Use a credible registrar (Namecheap, Porkbun, Cloudflare Registrar). ~£10/year
- **Action:** Register `alphacon.ai` (or your chosen variant — confirm exact name now since branding hangs off it)
- **Write down:** Registrar name (in case you need to transfer later)

### 3. Cloudflare account
- **Why:** DNS, CDN, WAF, R2 (object storage), Turnstile (anti-abuse), Workers (edge webhook verification)
- **Tier:** Free (R2 storage and Workers have generous free tiers)
- **Action:**
  - Sign up at cloudflare.com
  - Add your domain (Cloudflare will give you nameservers; update them at your registrar)
  - Enable Turnstile (under "Turnstile" in dashboard) — note the site key and secret
  - Create an R2 bucket called `alphacon-uploads`
- **Write down:**
  - Cloudflare account ID
  - Zone ID (for the domain)
  - Turnstile site key + secret
  - R2 access key ID + secret access key

---

## Phase 1 — Database, Cache, Auth (free tiers cover MVP)

### 4. Supabase project
- **Why:** Managed Postgres + pgvector + built-in auth (handles email/password and magic link). The single biggest dependency.
- **Tier:** Free (500 MB DB, 2 GB bandwidth, 50,000 monthly active users — way more than MVP needs)
- **Action:**
  - Sign up at supabase.com
  - Create project `alphacon-mvp` in the closest region (`eu-west-2` for UK)
  - Set a strong database password (save in a password manager)
  - Note the project URL and anon key from Settings → API
  - Enable email/password auth (Authentication → Providers)
  - Disable email confirmation for MVP (Authentication → Settings → "Enable email confirmations" off — we'll re-enable for production)
  - Enable Row Level Security in advance: Authentication → Policies (we'll add policies in code)
- **Write down:**
  - Supabase project URL
  - Supabase anon key (frontend)
  - Supabase service role key (backend) — **never expose this to the frontend**
  - Database connection string (for direct Postgres access from backend)

### 5. Upstash Redis
- **Why:** Cache, queue, rate-limit budgets, agent short-term memory
- **Tier:** Free (10,000 commands/day — enough for MVP and early development)
- **Action:**
  - Sign up at upstash.com
  - Create Redis database `alphacon-mvp` in the same region as Supabase
  - Pick "Regional" (cheaper) for MVP — switch to "Global" later if needed
- **Write down:**
  - Redis URL (Upstash gives a `redis://` URL with embedded password)
  - REST URL + token (alternative HTTPS interface — useful from edge functions later)

---

## Phase 2 — AI (paid, but cheap to start)

### 6. Anthropic API account
- **Why:** Claude — the agent
- **Tier:** Pay-as-you-go. Add £20–50 of credits to start; that lasts well into development
- **Action:**
  - Sign up at console.anthropic.com
  - Add billing details
  - Create API key labelled `alphacon-mvp-dev`
  - Note the model IDs you'll use: `claude-haiku-4-5`, `claude-sonnet-4-6`, `claude-opus-4-7`
- **Write down:**
  - Anthropic API key
  - Note: enable prompt caching from day one in code (the architecture decision)

### 7. Voyage AI account *(can skip for foundational MVP — embeddings come with the agent in a later batch)*
- **Why:** Embeddings for the agent's long-term memory (pgvector lookups)
- **Tier:** Pay-as-you-go, very cheap
- **When:** Skip until the agent batch — you don't need this for the foundational MVP
- **Write down (when needed):** Voyage API key

---

## Phase 3 — AWS (security & email — light usage at MVP)

### 8. AWS account
- **Why:** KMS for OAuth credential envelope encryption (security), SES for bulk email
- **Tier:** Free tier covers Phase 1 usage easily; pay-as-you-go for KMS (£0.80/month per key)
- **Action:**
  - Sign up at aws.amazon.com (use the AlphaCon AI Limited company entity, not personal)
  - Verify the email and add billing
  - **Enable MFA on the root account immediately** (use a hardware key or authenticator app)
  - **Don't use root for anything else** — create an IAM user `alphacon-deploy` with programmatic access
  - Create a KMS Customer Managed Key (CMK) called `alphacon-credentials-mvp` in `eu-west-2`
  - Set up SES in `eu-west-2`:
    - Verify your sending domain (`alphacon.ai`) — Cloudflare DNS will need TXT/MX records SES gives you
    - Request production access (sandbox is restrictive — production access takes 24h)
- **Write down:**
  - AWS account ID
  - IAM access key ID + secret (for the `alphacon-deploy` user)
  - KMS key ARN
  - SES SMTP credentials (separate from IAM)
  - SES verified sender email (e.g., `noreply@alphacon.ai`)

### 9. Resend account *(for transactional email)*
- **Why:** Better deliverability and templating than SES for low-volume transactional (signup, password reset). SES handles bulk.
- **Tier:** Free (100 emails/day — way more than MVP needs)
- **Action:**
  - Sign up at resend.com
  - Add and verify your domain
  - Create an API key
- **Write down:**
  - Resend API key

---

## Phase 4 — Hosting (deploy when foundational MVP is done — not yet)

### 10. Fly.io account
- **Why:** Backend + worker container hosting
- **Tier:** Pay-as-you-go (~£10–25/month for MVP)
- **When:** After the foundational MVP runs locally end-to-end. Don't deploy until then.
- **Action:**
  - Sign up at fly.io
  - Add billing (free tier removed but minimum spend is tiny)
  - Install `flyctl` locally
- **Write down:**
  - Fly.io API token (for CI deployments)

### 11. Vercel account *(for frontend hosting)*
- **Why:** Best-in-class Next.js hosting, free for hobby
- **Tier:** Free Hobby tier covers MVP
- **When:** Same as Fly.io — after MVP is locally complete
- **Action:**
  - Sign up at vercel.com (link to your GitHub org)
  - Don't connect the repo yet — we'll do that when ready to deploy
- **Write down:**
  - Vercel account / team slug

---

## Phase 5 — Observability & billing (defer until users exist)

### 12. Sentry account
- **Why:** Error tracking
- **Tier:** Free Developer tier (5K errors/month)
- **When:** Add when deploying — not needed for local dev
- **Write down (when needed):** Sentry DSN

### 13. Stripe account
- **Why:** Subscriptions and billing
- **Tier:** Pay-per-transaction (no monthly fee)
- **When:** When the first paying customer is imminent. Don't bother for the foundational MVP.
- **Important:** Stripe needs the AlphaCon AI Limited company entity verified — they ask for proof of incorporation, ID, address. Can take a few days. Start the verification process early but don't block on it.
- **Write down (when needed):**
  - Stripe publishable key (frontend)
  - Stripe secret key (backend)
  - Stripe webhook signing secret

---

## Summary table — what you'll have after this checklist

| Service | Purpose | Tier | When |
|---|---|---|---|
| GitHub | Source code, CI | Free | Now |
| Domain registrar | Domain | ~£10/yr | Now |
| Cloudflare | DNS, CDN, WAF, R2, Turnstile, Workers | Free | Now |
| Supabase | Postgres + Auth | Free | Now |
| Upstash | Redis | Free | Now |
| Anthropic | Claude API | £20–50 credits | Now |
| Voyage | Embeddings | Skip until agent batch | Later |
| AWS | KMS + SES | ~£1–5/mo | Now |
| Resend | Transactional email | Free | Now |
| Fly.io | Backend hosting | ~£10–25/mo | After MVP done |
| Vercel | Frontend hosting | Free | After MVP done |
| Sentry | Errors | Free | After deploy |
| Stripe | Billing | Per-transaction | First paying user |

**Estimated total monthly cost during MVP development: £0–10.**
**Estimated total cost once deployed with real usage: £30–60/month + LLM costs (£100–300 with caching).**

---

## After this checklist

Save all credentials to a password manager (1Password, Bitwarden) under a "AlphaCon" vault. Use Doppler or `.env.local` files for local development. Never commit secrets — pre-commit hooks (set up in Batch 2) will block this automatically.

Once you've worked through this list and have credentials in your password manager, you're ready for Batch 2 (monorepo skeleton + pre-commit + CI).
