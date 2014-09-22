# coding=utf-8
__author__ = 'SVS'
from datetime import datetime, timedelta
from twisted.internet.task import Clock


# noinspection PyPep8Naming
class ExtendedClock(Clock):
    def __init__(self):
        super(ExtendedClock, self).__init__()
        self._current_time = None
        self.set_current_time(datetime.now())

    def current_datetime(self):
        return self._current_time + timedelta(seconds=self.seconds())

    def set_current_time(self, value):
        self.rightNow = 0.0
        self._current_time = value

    def advance(self, amount):
        """
        Move time on this clock forward by the given amount and run whatever
        pending calls should be run.

        @type amount: C{float}
        @param amount: The number of seconds which to advance this clock's
        time.
        """
        right_now = self.rightNow + amount
        self._sortCalls()
        while self.calls and self.calls[0].getTime() <= right_now:
            self.rightNow = self.calls[0].getTime()
            call = self.calls.pop(0)
            call.called = 1
            call.func(*call.args, **call.kw)
            self._sortCalls()
        self.rightNow = right_now

    def seconds(self):
        return self.rightNow