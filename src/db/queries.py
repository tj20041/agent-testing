GET_RAW_EVENTS = "SELECT id, raw_payload FROM events_staging WHERE processed = FALSE LIMIT %s;"
UPDATE_EVENT_STATUS = "UPDATE events_staging SET processed = TRUE WHERE id = ANY(%s);"
