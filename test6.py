from datetime import datetime

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def lambda_handler(event, context):
    session_logs = [
        {"session_id": "SESS-1001", "user_id": "USER-44", "event_timestamp_str": "2026-08-13 14:35:10"},
        {"session_id": "SESS-1002", "user_id": "USER-89", "event_timestamp_str": "2026-08-13 18:20:45"},
    ]

    for log in session_logs:
        try:
            dt = datetime.strptime(log["event_timestamp_str"], TIMESTAMP_FORMAT)
            log["session_timestamp"] = dt
        except ValueError as err:
            raise ValueError(
                f"Invalid timestamp format for session {log['session_id']}: "
                f"'{log['event_timestamp_str']}' — expected format '{TIMESTAMP_FORMAT}' (24-hour clock)"
            ) from err

    return {"statusCode": 200, "body": session_logs}
