# Database Scripts

## Fresh install (new Supabase project)

1. Create a new project on supabase.com
2. Go to SQL Editor
3. Paste and run `fresh_install.sql`
4. Copy your project URL and service role key
5. Add to `backend/.env`:
   ```
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   ```
6. Run the backend:
   ```
   uvicorn src.main:app --reload --port 8000
   ```
7. Database is ready. No manual setup needed.

## Migration (existing project with old schema)

Only needed if you were using the app before May 2026.

1. Open Supabase SQL Editor
2. Read `migrate.sql` carefully before running
3. Run Step 1 (backup) and verify counts
4. Run Steps 2–6 in order
5. Re-add your real devices manually
   using the commented INSERT statements
6. Restart the backend

## Schema overview

```
organisations → properties → rooms → devices
                           → alerts
                           → state_history
```

All IDs are UUID.
All foreign keys have `ON DELETE CASCADE`
except `devices.room_id` which is
`ON DELETE SET NULL` so devices are never
lost when a room is deleted.
