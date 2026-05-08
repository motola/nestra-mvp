-- =============================================
-- ALPHACON AI — FRESH INSTALL
-- Run this once on a new Supabase project
-- =============================================

-- STEP 1: organisations
CREATE TABLE IF NOT EXISTS organisations (
  id         UUID PRIMARY KEY
             DEFAULT gen_random_uuid(),
  name       TEXT NOT NULL,
  plan       TEXT DEFAULT 'free',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- STEP 2: properties
CREATE TABLE IF NOT EXISTS properties (
  id              UUID PRIMARY KEY
                  DEFAULT gen_random_uuid(),
  organisation_id UUID REFERENCES
                  organisations(id)
                  ON DELETE CASCADE,
  name            TEXT NOT NULL,
  address         TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- STEP 3: rooms
CREATE TABLE IF NOT EXISTS rooms (
  id          UUID PRIMARY KEY
              DEFAULT gen_random_uuid(),
  property_id UUID NOT NULL REFERENCES
              properties(id)
              ON DELETE CASCADE,
  name        TEXT NOT NULL,
  floor       INTEGER,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- STEP 4: devices
CREATE TABLE IF NOT EXISTS devices (
  id          UUID PRIMARY KEY
              DEFAULT gen_random_uuid(),
  property_id UUID REFERENCES
              properties(id)
              ON DELETE CASCADE,
  room_id     UUID REFERENCES
              rooms(id)
              ON DELETE SET NULL,
  vendor      TEXT NOT NULL,
  vendor_id   TEXT,
  name        TEXT NOT NULL,
  model       TEXT,
  ip_address  TEXT,
  mac         TEXT,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- STEP 5: alerts
CREATE TABLE IF NOT EXISTS alerts (
  id            UUID PRIMARY KEY
                DEFAULT gen_random_uuid(),
  device_id     UUID REFERENCES
                devices(id)
                ON DELETE CASCADE,
  device_name   TEXT,
  property_id   UUID REFERENCES
                properties(id)
                ON DELETE CASCADE,
  property_name TEXT,
  type          TEXT,
  severity      TEXT DEFAULT 'info',
  message       TEXT,
  dismissed     BOOLEAN DEFAULT FALSE,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- STEP 6: state_history
CREATE TABLE IF NOT EXISTS state_history (
  id          UUID PRIMARY KEY
              DEFAULT gen_random_uuid(),
  device_id   UUID REFERENCES
              devices(id)
              ON DELETE CASCADE,
  event_type  TEXT NOT NULL,
  value       TEXT,
  property_id UUID REFERENCES
              properties(id)
              ON DELETE CASCADE,
  recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- STEP 7: indexes
CREATE INDEX IF NOT EXISTS idx_properties_org
  ON properties(organisation_id);
CREATE INDEX IF NOT EXISTS idx_rooms_property
  ON rooms(property_id);
CREATE INDEX IF NOT EXISTS idx_devices_property
  ON devices(property_id);
CREATE INDEX IF NOT EXISTS idx_devices_room
  ON devices(room_id);
CREATE INDEX IF NOT EXISTS idx_alerts_property
  ON alerts(property_id);
CREATE INDEX IF NOT EXISTS idx_alerts_device
  ON alerts(device_id);
CREATE INDEX IF NOT EXISTS idx_alerts_dismissed
  ON alerts(dismissed);
CREATE INDEX IF NOT EXISTS idx_state_history_device
  ON state_history(device_id);
CREATE INDEX IF NOT EXISTS idx_state_history_time
  ON state_history(recorded_at DESC);

-- STEP 8: seed default organisation
INSERT INTO organisations (name, plan)
VALUES ('Alphacon Demo', 'free')
ON CONFLICT DO NOTHING;
