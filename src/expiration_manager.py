import time
import threading
from collections.abc import MutableMapping

class ExpiringDict(MutableMapping):
    def __init__(self, ttl_seconds, cleanup_interval=1.0):
        self._data = {}
        self._ttl = float(ttl_seconds)
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._cleaner, daemon=True,
                                        args=(cleanup_interval,))
        self._thread.start()

    def _cleaner(self, interval):
        while not self._stop.wait(interval):
            now = time.time()
            with self._lock:
                for k, (v, exp) in list(self._data.items()):
                    if exp < now:
                        del self._data[k]

    def __setitem__(self, key, value):
        with self._lock:
            self._data[key] = (value, time.time() + self._ttl)

    def __getitem__(self, key):
        with self._lock:
            val, exp = self._data[key]
            if exp < time.time():
                del self._data[key]
                raise KeyError(key)
            return val

    def __delitem__(self, key):
        with self._lock:
            del self._data[key]

    def __iter__(self):
        with self._lock:
            return iter([k for k, (_, exp) in self._data.items() if exp >= time.time()])

    def __len__(self):
        with self._lock:
            return sum(1 for _, exp in self._data.values() if exp >= time.time())

    def close(self):
        self._stop.set()
        self._thread.join()