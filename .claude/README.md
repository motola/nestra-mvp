# Claude Code Configuration

This directory contains configuration for **Claude Code** users working on this project. If you don't use Claude Code, you can ignore this folder — your existing git hooks and linting tools will enforce the same standards.

## What are these hooks?

Claude hooks ensure that when you use Claude Code to commit code or create pull requests, everything follows our project's coding standards and conventions.

## Our Standards

### Branch Names

All branches must follow the format:

```
<type>/NEM-<number>-<description>
```

Allowed types: `feat`, `fix`, `chore`, `docs`, `refactor`

✅ Good examples:

- `feat/NEM-28-intelligence-backend`
- `fix/NEM-21-property-detail`
- `chore/NEM-14-update-dependencies`

❌ Not allowed:

- `feature/new-feature` (missing NEM number)
- `NEM-28-something` (missing type prefix)

### Commit Messages

All commits must start with:

```
NEM-<number>: <lowercase description>
```

✅ Good:

- `NEM-28: implement device sync pipeline foundation`
- `NEM-21: fix type checking errors in intelligence module`

❌ Not allowed:

- `feat: add new feature` (Conventional Commits)
- `fix(scope): bug fix` (scoped commits)

### Pull Requests

**Title:** Must follow NEM format

```
NEM-<number>: <description>
```

**Description:** Required (minimum 20 characters)

- Explain what changed and why
- Reference related issues if applicable

**Labels:** Suggested categories

- `backend`, `frontend`, `bug`, `enhancement`, `documentation`, `type-checking`

**Why?** Nestra uses NEM issue tracking. Every branch, commit, and PR must reference its issue number for traceability and project management.

### Code Formatting

The `prettier_check` hook validates that code is formatted consistently. Our pre-commit hooks (ruff, prettier) will auto-format most issues, but Claude respects these rules too.

## Setup

If you're a Claude Code user on this project:

1. The hooks are already configured in `.claude/hooks.json`
2. They run automatically when you use Claude Code to:
   - Create commits
   - Create/update pull requests
3. If your commit/PR title doesn't match the pattern, Claude will suggest corrections

## For Non-Claude Users

If you use Git/GitHub directly (without Claude Code):

- Your standard git pre-commit hooks enforce formatting (ruff, prettier, etc.)
- You'll see validation errors if commit messages don't follow `NEM-XX:` format
- These are the same standards, just enforced by different tools

## Questions?

Check the project's main documentation (coming soon in CLAUDE.md) for full coding standards and workflow guidelines.
