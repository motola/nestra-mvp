-- =============================================
-- ALPHACON AI — MIGRATION
-- From TEXT ids to UUID with foreign keys
-- READ EVERYTHING BEFORE RUNNING
-- =============================================

-- STEP 1: backup existing data
CREATE TABLE IF NOT EXISTS
  devices_backup AS
  SELECT * FROM devices;

CREATE TABLE IF NOT EXISTS
  properties_backup AS
  SELECT * FROM properties;

CREATE TABLE IF NOT EXISTS
  rooms_backup AS
  SELECT * FROM rooms;

CREATE TABLE IF NOT EXISTS
  alerts_backup AS
  SELECT * FROM alerts;

CREATE TABLE IF NOT EXISTS
  state_history_backup AS
  SELECT * FROM state_history;

-- Verify backups before continuing
-- You should see row counts here:
SELECT 'devices' AS table_name,
       COUNT(*) AS rows
FROM devices_backup
UNION ALL
SELECT 'properties', COUNT(*)
FROM properties_backup
UNION ALL
SELECT 'rooms', COUNT(*)
FROM rooms_backup;

-- STOP HERE AND CHECK THE COUNTS
-- Only continue if counts look right

-- STEP 2: drop old tables
-- Children first, then parents
DROP TABLE IF EXISTS state_history;
DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS devices;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS properties;
DROP TABLE IF EXISTS organisations;

-- STEP 3: recreate with proper schema
-- (paste fresh_install.sql steps 1-8 here)

-- STEP 4: restore real properties
-- Replace <org-uuid> with the UUID
-- from organisations table after
-- running step 8 above:
-- SELECT id FROM organisations LIMIT 1;

INSERT INTO properties
  (organisation_id, name, address)
SELECT
  (SELECT id FROM organisations LIMIT 1),
  name,
  address
FROM properties_backup
WHERE id NOT LIKE 'demo-%'
AND id NOT LIKE 'prop-00%'
RETURNING id, name;

-- STEP 5: restore real devices
-- After step 4, copy the property UUIDs
-- returned above and insert devices.

-- For Jehn's Shelly:
-- INSERT INTO devices
--   (property_id, vendor, vendor_id,
--    name, model, ip_address, mac)
-- VALUES
--   ('<cedars-property-uuid>',
--    'shelly_local',
--    'shellyplus1pm-048308DE848C',
--    'Jehn''s Shelly',
--    'PlusPlugUK',
--    '192.168.1.76',
--    '048308DE848C');

-- For Matter device:
-- INSERT INTO devices
--   (property_id, vendor, vendor_id,
--    name, model, ip_address, mac)
-- VALUES
--   ('<aldgate-property-uuid>',
--    'matter',
--    'F808125C3B286505',
--    'F808125C3B286505',
--    'Matter Device',
--    '192.168.1.246',
--    'F808125C3B286505');

-- STEP 6: normalise existing room names
-- Converts "BED ROOM", "living room", "BEDROOM" etc. to Title Case.
-- initcap() is Postgres built-in — safe to run multiple times.
UPDATE rooms SET name = initcap(name);

-- STEP 7: verify migration
SELECT
  'organisations' AS t, COUNT(*) AS n
  FROM organisations
UNION ALL
SELECT 'properties', COUNT(*)
  FROM properties
UNION ALL
SELECT 'rooms', COUNT(*)
  FROM rooms
UNION ALL
SELECT 'devices', COUNT(*)
  FROM devices;
