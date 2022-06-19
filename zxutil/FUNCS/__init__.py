import datetime

def create_timestamp() -> int:
    """
    creates a unix timestamp
    """
    now = datetime.datetime.now()
    # convert now to unix timestamp milliseconds
    unix_timestamp = int(now.timestamp() * 1000)
    return unix_timestamp