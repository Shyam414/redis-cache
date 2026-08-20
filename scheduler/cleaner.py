import time


def cleaner_worker(storage, is_running, interval=1):

    while is_running():
        storage.remove_expired()
        time.sleep(interval)