"""
Background TTL cleaner.
"""

import time


def cleaner_worker(
    storage,
    is_running,
    interval=1
):
    """
    Periodically removes expired keys.
    """

    while is_running():

        keys = storage.keys()

        for key in keys:

            node = storage.get_node(key)

            if node is None:
                continue


            if node.is_expired():

                print(
                    f"TTL expired: {key}"
                )

                storage.delete(key)


        time.sleep(interval)