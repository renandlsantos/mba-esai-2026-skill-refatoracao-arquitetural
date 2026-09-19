from datetime import datetime, timezone


def utc_now():
    # The existing SQLite schema stores UTC without timezone metadata.
    return datetime.now(timezone.utc).replace(tzinfo=None)
