 # Branch and Commit Conventions

*How we name branches and write commit messages on `nestra-mvp`. Applies to everyone, including Claude Code.*

---

## Branch naming

Format:

```
<type>/<TICKET>-<short-slug>
```

Examples:

```
feat/NEM-12-setup-project
feat/NEM-23-add-user-aggregate
fix/NEM-45-rls-policy-edge-case
chore/NEM-67-bump-fastapi-version
docs/NEM-89-update-glossary
refactor/NEM-91-extract-tenant-scope-helper
test/NEM-104-add-rls-isolation-tests
```

### Allowed type prefixes

Use only these. Don't invent new ones.

| Prefix | When to use |
|---|---|
| `feat/` | New functionality, new endpoints, new components |
| `fix/` | Bug fixes (something was wrong, now it's right) |
| `chore/` | Dependency bumps, tooling, formatting, build config — anything that isn't user-visible |
| `docs/` | Documentation only — no code changes |
| `refactor/` | Restructuring without behaviour change |
| `test/` | Adding or updating tests only — no production code changes |

If you genuinely can't decide between two, pick the more specific one (`fix/` over `chore/` if a bug is involved, `feat/` over `refactor/` if any new behaviour ships).

### Rules

- **Lowercase slug only.** Capitals confuse case-insensitive filesystems on some Macs and look messy in tooling.
- **Slug ≤ 30 characters.** Long branch names get truncated in PR lists and IDE branch pickers.
- **Always a ticket number.** No `feat/quick-fix` or `wip/random-experiment` against `main`. Every branch traces back to a Jira ticket. If there's no ticket, create one — even for a one-line typo fix.
- **One branch per ticket. One ticket per branch.** If you want to do "two tickets in one branch," split into two branches. Reviewers thank you, blast radius stays small, rollbacks are clean.
- **Delete after merge.** Both locally (`git branch -d`) and on GitHub. Repo settings should auto-delete merged branches; if yours doesn't, turn it on.
- **Keep branches short-lived.** Aim for less than 3 days from branch creation to merge. Long-running branches diverge from `main` and become painful to rebase.

---

## Commit messages

Format:

```
<TICKET>: <descriptive message>
```

The ticket key, a colon, a single space, then a clear description in present tense and lowercase.

### Examples

Good:

```
NEM-12: set up nestra-mvp foundational structure with architecture
NEM-23: add user aggregate root with email validation
NEM-45: fix RLS policy edge case for cross-organization queries
NEM-67: bump fastapi from 0.115 to 0.116
NEM-89: clarify difference between Stay and Tenant in glossary
NEM-104: add isolation test for cross-organization queries
```

Bad (will be blocked by `commitlint`):

```
fixed the bug                          ← no ticket key
WIP                                    ← never commit WIP to a branch you'll merge
NEM-12: update                         ← description too short and vague
NEM-12 added user model.               ← no colon, capital A, ends with period
nem-12: add user                       ← lowercase ticket key
NEM-12:add user aggregate              ← no space after colon
```

### The rules

- **Ticket key uppercase**, exactly as it appears in Jira (`NEM-12`, not `nem-12`).
- **Colon and a single space** after the ticket key.
- **Description in present-tense imperative**: "add user aggregate", not "added user aggregate" or "adding user aggregate". Reads like an instruction the commit fulfils.
- **Lowercase first letter** of the description, no period at the end. Treat it as a phrase, not a sentence.
- **At least 10 characters** in the description. Longer is fine; "fix" and "wip" are not.
- **Wrap at ~72 characters.** Git tools display 72-char lines comfortably; longer lines wrap awkwardly in `git log`, IDE blame views, and Jira's commit panel.

### One commit, one logical change

Each commit should make sense on its own. If you find yourself writing "and also X" in a commit message, that's two commits.

```
✗ NEM-23: add user aggregate and update glossary and bump fastapi
✓ NEM-23: add user aggregate root
✓ NEM-23: add User entry to glossary
✓ NEM-67: bump fastapi to 0.116
```

Three small commits are always better than one big one for code review. If multiple commits in the same branch belong to the same ticket, that's fine — the ticket key is the same on each.

### Why this format

Three reasons it works for us:

1. **The ticket is the classifier.** Jira already knows whether NEM-12 is a Story, Bug, or Chore. We don't need a `feat/fix/chore` prefix on the commit too — that's redundant.
2. **It reads cleanly in `git log --oneline`** — `NEM-12: set up project` is easier to scan than `feat(identity): add user aggregate root with email validation`.
3. **It pairs with the YAML you've configured for Jira-GitHub linking** — the ticket key at the start is the most reliable pattern for any integration to detect.

---

## Pull request hygiene

- **PR title** mirrors a commit message: `NEM-12: set up nestra-mvp foundational structure with architecture`. Don't write `[NEM-12] Setup` or "Final version, please review."
- **PR description** explains *what* and *why*, not *how* — the diff shows how. Include manual verification steps if any are needed.
- **Keep PRs small.** Aim for less than 400 lines changed. Larger PRs get worse review attention; reviewers skim. If a PR exceeds 400 lines, ask whether it should be split.
- **CI must pass before requesting review.** Don't waste reviewers' time on a PR that's red.
- **Address review comments in new commits**, not by force-pushing over old ones. The reviewer needs to see what changed in response to their comments. Squash on merge if you want a clean history on `main`.
- **Squash merge to `main`.** One commit per merged PR. Repo settings should enforce this.

---

## Merge strategy on `main`

- **`main` is always deployable** (once we're deploying — for now, "always green and tested")
- **No direct pushes to `main`.** Branch protection enforces this.
- **Squash merge from PRs.** Keeps `main`'s history one-commit-per-feature, easy to revert.
- **Rebase to update branches**, not merge from `main` into your branch. Linear history is easier to read.

---

## Pre-commit enforcement

The repo's pre-commit hooks (configured in Batch 2) enforce these conventions. Specifically:

- **`commitlint`** validates commit messages against the regex pattern: `^NEM-\d+: [a-z].{9,}$` — ticket key, colon, space, lowercase first character, at least 10 characters of description.
- **`gitleaks`** blocks any commit containing API keys, passwords, or other secrets.
- **`ruff`** and **`eslint`** block commits with lint errors.

Don't bypass these with `--no-verify`. If a hook fires legitimately, fix the issue. If it's a false positive, raise it before bypassing.

---

## A note on commit messages and Claude Code

When Claude Code commits on your behalf, it follows the same conventions. If a Claude Code commit doesn't match this format, that's a bug — flag it and ask Claude to amend. Don't bypass `commitlint` with `--no-verify` to get a malformed message through.