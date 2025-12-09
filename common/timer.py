# common/timer.py
import time
from typing import Callable, Any, Tuple


def measure_execution_time(func: Callable, *args, **kwargs) -> Tuple[Any, float]:
    """
    Measures execution time of a function.

    :param func: Function to be measured
    :param args: Positional arguments for the function
    :param kwargs: Keyword arguments for the function
    :return: Tuple containing function result and time taken in seconds
    """
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()

    elapsed_time = end_time - start_time
    return result, elapsed_time
