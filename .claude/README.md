# Claude Code Configuration

This directory contains configuration for **Claude Code** users working on this project. If you don't use Claude Code, you can ignore this folder — your existing git hooks and linting tools will enforce the same standards.

## What are these hooks?

Claude hooks ensure that when you use Claude Code to commit code or create pull requests, everything follows our project's coding standards and conventions.

## Our Standards

### Commit & PR Naming

All commits and PRs must follow the format:

```
NEM-<number>: <lowercase description>
```

✅ Good examples:

- `NEM-28: implement device sync pipeline foundation`
- `NEM-21: fix type checking errors in intelligence module`
- `NEM-14: add property detail screen`

❌ Not allowed:

- `feat: add new feature` (Conventional Commits)
- `fix(scope): bug fix` (scoped commits)
- Random descriptions without issue numbers

**Why?** Nestra uses NEM issue tracking. Every commit must reference its issue number for traceability and project management.

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
