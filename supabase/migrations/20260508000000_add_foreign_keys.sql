-- Add foreign key constraints (idempotent — safe to re-run)

DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'fk_rooms_property'
  ) THEN
    ALTER TABLE rooms
      ADD CONSTRAINT fk_rooms_property
      FOREIGN KEY (property_id) REFERENCES properties(id)
      ON DELETE RESTRICT;
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'fk_devices_property'
  ) THEN
    ALTER TABLE devices
      ADD CONSTRAINT fk_devices_property
      FOREIGN KEY (property_id) REFERENCES properties(id)
      ON DELETE RESTRICT;
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'fk_devices_room'
  ) THEN
    ALTER TABLE devices
      ADD CONSTRAINT fk_devices_room
      FOREIGN KEY (room_id) REFERENCES rooms(id)
      ON DELETE SET NULL;
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'fk_alerts_device'
  ) THEN
    ALTER TABLE alerts
      ADD CONSTRAINT fk_alerts_device
      FOREIGN KEY (device_id) REFERENCES devices(id)
      ON DELETE CASCADE;
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'fk_state_history_device'
  ) THEN
    ALTER TABLE state_history
      ADD CONSTRAINT fk_state_history_device
      FOREIGN KEY (device_id) REFERENCES devices(id)
      ON DELETE CASCADE;
  END IF;
END $$;
