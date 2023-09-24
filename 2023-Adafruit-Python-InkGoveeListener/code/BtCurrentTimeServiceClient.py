# import time

# from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
# from adafruit_ble.characteristics import Characteristic
from adafruit_ble.characteristics import StructCharacteristic
from adafruit_ble.services import Service
from adafruit_ble.uuid import StandardUUID

# Sometimes needed, but not here.
# from adafruit_ble.advertising import Advertisement
# from adafruit_ble.uuid import UUID

# import BtAdvertisementFinder


class BtCurrentTimeServiceClient(Service):
    """Is the CircuitPython minimal mimic of a Bluetooth Current Time Service.
    This is the entire service, not just the data or characteristic.
    """

    uuid = StandardUUID(0x1805)  # UUID of the service
    currentTimeData = StructCharacteristic(
        uuid=StandardUUID(0x2A2B),
        # Don't need to provide these; they should be discovered
        # by the Bluetooth system.
        # properties=Characteristic.READ | Characteristic.NOTIFY,
        struct_format="<HBBBBBBBB",  # https://docs.python.org/3/library/struct.html
    )
    userUnitPreferences = StructCharacteristic(
        uuid=StandardUUID(0x8020),  # Made up number; not part of standard
        # Don't need to provide these; they should be discovered
        # by the Bluetooth system.
        # properties=Characteristic.READ | Characteristic.NOTIFY,
        struct_format="<HHHHHHHH",  # https://docs.python.org/3/library/struct.html
    )

    def GetTimeString(self):
        (y, m, d, hh, mm, ss, j1, j2, j3) = self.currentTimeData
        retval = "{0:04d}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}".format(
            y, m, d, hh, mm, ss
        )
        return retval

    def GetTimeAsStructTime(self):
        # (y, m, d, hh, mm, ss, j1, j2, j3) = timeresult.data
        # where the 'j' values are junk as far as this class is concerned.
        # returns e.g., (year, mon, day, hour, minute, second, 6, 0, 1)
        # https://docs.circuitpython.org/en/latest/shared-bindings/time/index.html#time.struct_time
        dt = self.currentTimeData
        now = (dt[0], dt[1], dt[2], dt[3], dt[4], dt[5], dt[6], 0, 0)
        return now

    def GetUserUnitPreferences(self):
        retval = None
        try:
            retval = self.userUnitPreferences
        except Exception:
            pass
        return retval

