# Database Connection Pool Fix - Report

**Date:** August 22, 2026
**Issue:** `sqlalchemy.exc.DBAPIError: connection was closed in the middle of operation`
**Status:** ✅ Fixed

---

## Problem Summary

The backend experienced intermittent database connection failures during login attempts. The error occurred because the SQLAlchemy connection pool was using default configuration, which led to stale connections being reused.

### Root Cause

**Before the fix**, the database engine was created with no explicit pool configuration:

```python
create_async_engine(settings.database_url, echo=settings.debug)
```

This resulted in:

- **Default pool_size=5** - Only 5 connections maintained in pool
- **No connection health checks** - Dead connections were reused
- **No connection recycling** - Connections lived indefinitely until PostgreSQL closed them
- **Connection timeout mismatch** - PostgreSQL's 30-minute idle timeout caused stale connections

### What Happens

1. PostgreSQL closes idle connections after ~30 minutes
2. Application's pool still thinks connection is alive
3. New request tries to use dead connection
4. Query fails mid-operation: `connection was closed`

---

## Solution

Added explicit connection pool configuration to `backend/src/db/db.py`:

```python
create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=10,           # Maintain 10 ready connections
    max_overflow=20,        # Allow 20 additional connections if needed
    pool_pre_ping=True,     # Test connection before use (catches dead ones)
    pool_recycle=3600,      # Recycle connections after 1 hour
)
```

### How It Works

| Setting              | Purpose                     | Benefit                                   |
| -------------------- | --------------------------- | ----------------------------------------- |
| `pool_size=10`       | Base pool connections       | More connections ready, less waiting      |
| `max_overflow=20`    | Extra connections available | Handles traffic spikes gracefully         |
| `pool_pre_ping=True` | Health check before use     | **Detects and discards dead connections** |
| `pool_recycle=3600`  | Auto-refresh after 1 hour   | Prevents stale connection buildup         |

### The Key Fix: `pool_pre_ping=True`

Before using a connection from the pool, SQLAlchemy now sends a simple "ping" query:

- **If connection is alive** → Use it immediately
- **If connection is dead** → Discard it, create a fresh one

This prevents the "connection was closed" error.

---

## What is a Connection Pool?

A **connection pool** is a collection of pre-established, ready-to-use database connections.

**Without pooling:**

```
Request → Create connection → Query → Close connection (slow)
```

**With pooling:**

```
Request → Grab ready connection → Query → Return to pool (fast)
```

Think of it like:

- **Without pool** = Calling someone on phone each time (dial, connect, hang up)
- **With pool** = Having 10 phone lines always open and ready

---

## Impact

✅ **Eliminates intermittent login failures**
✅ **Improves query performance** (no connection overhead)
✅ **Handles concurrent traffic** (20 max connections available)
✅ **Prevents stale connection bugs** (auto-health checks)

---

## Testing Notes

The fix was verified in production environment:

- Login attempts now succeed consistently
- No more "connection was closed" errors
- Database load properly distributed across connection pool

---

## References

- **File Changed:** `backend/src/db/db.py`
- **Commit:** `NEM-70: improve database connection pool to prevent stale connection errors`
- **SQLAlchemy Docs:** https://docs.sqlalchemy.org/en/20/core/pooling.html
