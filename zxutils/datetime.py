import datetime
import time
def create_unix_timestamp() -> int:
    now = datetime.datetime.now()
    # convert now to unix timestamp milliseconds
    unix_timestamp = int(now.timestamp() * 1000)
    return unix_timestamp

def random_sleep(min=10, max=30, auto_increment_max = True):
    """
    Sleeps for a random amount of time
    """
    import random
    if max < min and not auto_increment_max:
        raise ValueError("max must be greater than min")

    if max < min and auto_increment_max:
        max = min + max

    sleep_time = random.randint(min, max)
    time.sleep(sleep_time)