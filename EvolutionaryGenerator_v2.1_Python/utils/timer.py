"""Translation of ``Utils.Timer``."""

import time


class Timer:
    """Provides the methods to create and use timers.

    The Java version measures CPU time of the current thread through a
    ``ThreadMXBean``; ``time.thread_time_ns`` is its counterpart in Python.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: José Carlos Ortiz Bayliss
    :original version: 1.0
    """

    def __init__(self):
        """Creates a new instance of ``Timer``."""
        self.time_limit = 0
        self.start_time = 0

    def start(self, time_limit: int = -1) -> None:
        """Starts the timer with the time limit provided.

        :param time_limit: The maximum time allowed for the timer to work (in
            milliseconds). If this value is set to a negative number, no time limit
            is imposed to the timer.
        """
        if time_limit >= 0:
            self.time_limit = time_limit * 1000000
        else:
            self.time_limit = -1
        self.start_time = self._current_thread_cpu_time()

    def get_elapsed_time(self) -> int:
        """Returns the elapsed time since the search started.

        :return: The elapsed time since the search started.
        """
        return int((self._current_thread_cpu_time() - self.start_time) / 1000000)

    def get_remaining_time(self) -> int:
        """Returns the remaining time for the search.

        :return: The remaining time for the search.
        """
        tmp = int((self.time_limit - (self._current_thread_cpu_time() - self.start_time)) / 1000000)
        if tmp > 0:
            return tmp
        return 0

    def is_time_over(self) -> bool:
        """Verifies if the allowed running time is over.

        :return: ``True`` if the maximum allowed running time has been reached,
            ``False`` otherwise.
        """
        return (self.time_limit >= 0) and (self._current_thread_cpu_time() - self.start_time >= self.time_limit)

    @staticmethod
    def _current_thread_cpu_time() -> int:
        """Returns the CPU time consumed by the current thread, in nanoseconds."""
        return time.thread_time_ns()
