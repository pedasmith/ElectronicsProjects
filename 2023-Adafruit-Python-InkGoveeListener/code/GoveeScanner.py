import time
import adafruit_ble
from Govee5074 import Govee5074


class GoveeScanner:
    """Knows how to look for a BLE GoveeH5074 temperature / humidity sensor. Knows
    enough that it only scans for 5 seconds because we know the device sends data
    out more often than that. Will initialize to the available BLE radio."""
    def __init__(self, ble=None):
        self.LOGNAME = "Govee"
        if ble is None:
            ble = adafruit_ble.BLERadio()
        self.ble = ble

    def Scan(self, annunciator, ble=None, GOAL_TIME=5):
        """Returns a Govee5074 data value (possibly with IsOk==False), or None,
        based on the results of a short (5 second?) scan"""
        annunciator.Start()

        if ble is None:
            ble = self.ble

        retval = None  # will be a Govee5074
        maxTime = GOAL_TIME
        startTime = time.monotonic()
        goveeAdverts = {}
        try:
            while (maxTime > 0) and (retval is None):
                timeUsed = time.monotonic() - startTime
                maxTime = GOAL_TIME - timeUsed
                scanTime = 0.1
                retval = self.ScanOnce(annunciator, goveeAdverts, scanTime)
        except Exception as e:
            annunciator.NotFound()
            print("ERROR: exception " + self.LOGNAME + " reason: " + str(e))
            print("...exiting from GoveeScanner", str(type(e)))

        annunciator.End()
        return retval

    def ScanOnce(self, annunciator, goveeAdverts, maxTime):
        """Do one Bluetooth scan and return a Govee5074 with IsOk or not"""
        retval = None
        if (maxTime < 0.1):
            # Have to scan for more than some minimum, otherwise you
            # end up with a ValueError "non-zero timeout must be >= interval"
            return retval

        annunciator.Tick()

        list = self.ble.start_scan(timeout=maxTime)
        # No need to set extended to true.

        # We get a list right away. It will actually be filled in over time
        # and will stop only after the timeout.

        for advert in list:
            if advert is None:
                print("TRACE: 22: Advert is None??")
                continue
            if advert.scan_response:
                # Check to make sure that this response address is in the list
                # of adverts that have the right name ("Govee_H5074...")
                # You can't tell from just the response advert; you need the
                # original advert, too.
                if advert.address not in goveeAdverts:
                    # very frequent -- set is only govee adverts, but the
                    # scan_response can be for anything
                    # print("TRACE: 15: not in set", advert.address)
                    continue
                MANUFACTURER_SECTION = 0xFF  # Per Bluetooth SIG
                if (MANUFACTURER_SECTION in advert.data_dict):
                    annunciator.Found()
                    buffer = advert.data_dict[MANUFACTURER_SECTION]

                    g5074 = Govee5074(buffer)
                    if (g5074.IsOk):
                        annunciator.Read()
                        if retval is None:  # only print the first one
                            print("TRACE: 28: GOT DATA", g5074)
                        retval = g5074
                    else:
                        print("TRACE: 26: unusable sensor len=", len(buffer))
                        annunciator.NotFound()

                continue
            name = advert.complete_name
            if (name is not None) and ("Govee_H5074" in name):
                # print("TRACE: 30: Found main govee advert", advert.address, name)
                goveeAdverts[advert.address] = advert

        # Should pair up the start_scan with stop_scan.
        self.ble.stop_scan()
        return retval
