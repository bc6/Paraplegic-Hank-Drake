#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\carbon\telemetryMarkup.py
from contextlib import contextmanager
try:
    import blue
    blueAvailable = True
except ImportError:
    blueAvailable = False

if blueAvailable:

    @contextmanager
    def TelemetryContext(name):
        blue.statistics.EnterZone(name)
        try:
            yield
        finally:
            blue.statistics.LeaveZone()


else:

    @contextmanager
    def TelemetryContext(name):
        yield