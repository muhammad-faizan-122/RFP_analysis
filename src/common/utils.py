from contextlib import contextmanager
import time


@contextmanager
def measure_time(label, log):
    start = time.time()
    yield
    end = time.time()
    log.info(f"{label} took {end - start:.2f} seconds")
