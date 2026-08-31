# Code Review Checklist

⚠️ **CRITICAL:** This review is NOT about code style or patterns. It's about ensuring code **WORKS END-TO-END** across:
- Frontend UI → API calls → Backend logic → Database → Response → Frontend display

**If any section is skipped, production will break.** See "End-to-End Integration" section below.

## Before You Review

- [ ] Branch is up to date with develop
- [ ] All tests pass locally
- [ ] No merge conflicts
- [ ] Pre-commit hooks run clean
- [ ] **READ the entire PR description** - understand what changed and why
- [ ] **Understand the user flow** - what does this feature do from user perspective?

## Architecture & Design

- [ ] Changes follow established patterns in the codebase
- [ ] No unnecessary abstractions or over-engineering
- [ ] Dependencies are properly managed
- [ ] No circular dependencies
- [ ] Error handling is appropriate

## Code Quality

- [ ] Code is readable and well-named
- [ ] Comments explain *why*, not *what*
- [ ] No dead code or commented-out sections
- [ ] Consistent with project style guides
- [ ] Type hints are correct (mypy passes)

## Testing

- [ ] New functionality has tests
- [ ] Tests verify the happy path and edge cases
- [ ] Integration tests use real database (not mocks)
- [ ] No flaky or timing-dependent tests
- [ ] Test coverage is reasonable

## Database & Persistence

- [ ] Schema changes are migration-safe
- [ ] No N+1 queries
- [ ] Proper use of indexes
- [ ] Row-level security is considered
- [ ] **[CRITICAL] ORM model matches migration schema**
  - [ ] All model fields have corresponding columns
  - [ ] Column types match field types
  - [ ] Constraints in code match database constraints
  - [ ] All nullable fields are correctly marked
  - [ ] Indexes defined in model are in migration
- [ ] **[CRITICAL] Migration chain is correct**
  - [ ] down_revision points to PREVIOUS migration (not future)
  - [ ] Migration revision ID is unique (no duplicates)
  - [ ] Both upgrade() and downgrade() functions work
  - [ ] No orphaned migrations
  - [ ] **[CRITICAL] Only ONE migration head**
    - [ ] Run: `alembic heads`
    - [ ] Should return exactly ONE head revision
    - [ ] If multiple heads: broken migration chain
    - [ ] If error "Cycle detected": circular dependency
  - [ ] **[CRITICAL] No circular dependencies**
    - [ ] A → B → C (correct)
    - [ ] A → B → A (WRONG - creates cycle)
    - [ ] Check that down_revision never points forward
  - [ ] Migration chain is sequential
    - [ ] Each migration depends on the one before it
    - [ ] No parallel branches that don't merge

## Security

- [ ] No hardcoded secrets or credentials
- [ ] Input validation at system boundaries
- [ ] SQL injection prevention
- [ ] XSS prevention (frontend)
- [ ] CSRF protection (if applicable)

## Performance

- [ ] No unnecessary database queries
- [ ] Reasonable algorithm complexity
- [ ] Caching strategy is sound
- [ ] API response times are acceptable

## Frontend (if applicable)

- [ ] Components follow React best practices
- [ ] Props are properly typed
- [ ] No unnecessary re-renders
- [ ] Accessibility is considered
- [ ] Mobile responsive (if applicable)

## Backend (if applicable)

- [ ] API endpoints follow REST conventions
- [ ] Request/response schemas are validated
- [ ] Proper HTTP status codes
- [ ] Error messages are user-friendly

## Documentation

- [ ] README updated if needed
- [ ] Complex logic is documented
- [ ] API changes documented
- [ ] Breaking changes clearly noted

## End-to-End Integration (CRITICAL - Do Not Skip)

**This section ensures changes work across the entire system, not just individual components.**

### Frontend → Backend Contract
- [ ] API endpoints exist that frontend calls
- [ ] Request body shape matches backend schema
- [ ] Response body shape matches frontend types
- [ ] HTTP status codes are handled correctly
- [ ] Error responses are in expected format
- [ ] All required query parameters are documented
- [ ] Auth headers are properly handled

### Backend → Database
- [ ] All database queries use correct table/column names
- [ ] Query results map to ORM models correctly
- [ ] Soft delete logic (deleted_at) is implemented correctly
- [ ] Foreign key relationships exist
- [ ] Organization/tenant boundaries are enforced
- [ ] Indexes exist for all query filters

### Migrations → Production Ready
- [ ] Migration creates all required tables
- [ ] Migration adds/modifies all required columns
- [ ] Column types in migration match ORM Mapped types
- [ ] Default values in migration match model defaults
- [ ] Indexes in migration match model indexes
- [ ] Migration doesn't break existing data
- [ ] Downgrade works (if needed for rollback)
- [ ] Migration chain is sequential with no gaps

### Complete Feature Flow (Test Manual)
**For ANY backend feature, manually test the full flow:**
1. Frontend calls API endpoint with test data
2. Backend receives request → validates → processes
3. Database stores/retrieves data correctly
4. Frontend receives response → parses → displays
5. User sees correct result in UI

**Example: Creating an Integration**
- [ ] User clicks "Connect Bluetooth"
- [ ] Frontend POST /integrations with correct body
- [ ] Backend validates organization_id
- [ ] Database INSERT creates integration record
- [ ] Database SELECT retrieves it correctly
- [ ] Frontend receives response
- [ ] Frontend parses response
- [ ] Integration appears in UI list
- [ ] No errors in browser console
- [ ] No errors in server logs

### Common End-to-End Failures to Catch
- [ ] ❌ API endpoint doesn't exist → 404
- [ ] ❌ Wrong column name in query → Database error
- [ ] ❌ ORM field missing from migration → UndefinedColumnError
- [ ] ❌ Type mismatch (str vs UUID) → Validation error
- [ ] ❌ Missing foreign key → Constraint violation
- [ ] ❌ Auth not checked → Security bypass
- [ ] ❌ Response format wrong → Frontend parse error
- [ ] ❌ Migration doesn't run → Deployment fails

### Migration Chain Failures to Catch
- [ ] ❌ Multiple migration heads
  - Error: `Multiple head revisions are present for given argument 'head'`
  - Cause: Two independent migration chains that don't connect
  - Fix: Ensure each migration's `down_revision` points to previous one only
- [ ] ❌ Circular migration dependency
  - Error: `Cycle is detected in revisions`
  - Cause: A migration points forward (or creates a loop)
  - Example: A→B→C→A (wrong!) or A→B→A (wrong!)
  - Fix: Verify `down_revision` only points backward
- [ ] ❌ Orphaned migration
  - Cause: Migration with no parent (down_revision=None) when it should have one
  - Fix: Set down_revision to the migration before it
- [ ] ❌ Broken migration chain
  - Cause: Migration points to non-existent previous migration
  - Fix: Verify down_revision matches actual previous migration ID

## Deployment

- [ ] Fly.toml changes are appropriate
- [ ] Environment variables are configured
- [ ] Database migrations will work in production
- [ ] Health checks are properly configured
- [ ] Grace periods are sufficient for long operations
- [ ] **Migrations run BEFORE app starts** (if needed)
- [ ] **Rollback plan exists** if migration fails

## Final Checks - Can This Ship?

Ask yourself: **"If I merge this and deploy it, will it work?"**

- [ ] Commit messages follow NEM-XX format
- [ ] No unintended files committed
- [ ] Branch has meaningful history (not too many tiny commits)
- [ ] **Frontend can call backend endpoints** ✅
- [ ] **Backend receives/validates data correctly** ✅
- [ ] **Database stores/retrieves data correctly** ✅
- [ ] **Migrations run without errors** ✅
- [ ] **Feature works end-to-end in the app** ✅
- [ ] **No console errors** ✅
- [ ] **No server errors** ✅
- [ ] Ready for production deployment

**DO NOT APPROVE if:**
- ❌ API endpoint doesn't exist (only frontend code)
- ❌ Model field has no database column
- ❌ Migration doesn't match ORM schema
- ❌ No migration when database changes
- ❌ Feature only works "in theory" but untested
- ❌ Missing validation or error handling
- ❌ Security issues (auth, input validation, etc.)

## What Went Wrong (Lessons Learned)

**NEM-114 Failure:** PR was approved with database schema mismatch
- ✅ Code was clean
- ✅ Tests passed
- ✅ API logic was correct
- ❌ **ORM model fields ≠ Database columns**
- ❌ **No end-to-end test**
- ❌ **Migration wasn't verified**

**Result:** 2 days of debugging, production errors, user impact.

**Prevention:** This checklist must be followed for EVERY backend PR.

## Notes

<!-- Add any review notes or observations here -->
