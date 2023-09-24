import time
import adafruit_ble
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
# from adafruit_ble.characteristics import Characteristic
# from adafruit_ble.characteristics import StructCharacteristic
# from adafruit_ble.services import Service
# from adafruit_ble.uuid import StandardUUID

from BtCurrentTimeServiceClient import BtCurrentTimeServiceClient
# Sometimes needed, but not here.
# from adafruit_ble.advertising import Advertisement
# from adafruit_ble.uuid import UUID

class BtCurrentTimeServiceClientRunner:
    def __init__(self, ble=None):
        self.LOGNAME = "Govee"
        if ble is None:
            ble = adafruit_ble.BLERadio()
        self.ble = ble

    def Scan(self, annunciator, ble=None, GOAL_TIME=15, do_trace=True):
        if (do_trace):
            print("NOTE: BT scan started for CurrentTimeService")

        if ble is None:
            ble = self.ble

        found = set()
        service = None
        timeServiceConnection = None
        # GOAL_TIME = 15
        maxTime = GOAL_TIME
        startTime = time.monotonic()

        scan = 1
        try:
            while (timeServiceConnection is None) and (maxTime > 0):
                timeUsed = time.monotonic() - startTime
                maxTime = GOAL_TIME - timeUsed
                scanTime = 0.1
                if (scanTime != 0.1):  # Let's do tiny little scans
                    scanTime = 0.1
                timeServiceConnection = self.ScanOnce(ble, found, scanTime)
                if (do_trace):
                    print("*", end="\r")
                annunciator.Tick()
                scan = scan + 1
            if timeServiceConnection is not None:
                service = self.ConnectToCurrentTimeService(ble, timeServiceConnection, do_trace)
                # currTime = service.data
                # timeServiceConnection.disconnect()
                # timeServiceConnection = None
        except Exception as e:
            print("ERROR: exception for Bluetooth:", e)

        return (service, timeServiceConnection)

    def ScanOnce(self, ble, found, maxTime):
        """Do one Bluetooth scan and return a connected CurrentTimeService connection"""
        if (maxTime <= 0):
            return None

        timeServiceConnection = None
        list = ble.start_scan(ProvideServicesAdvertisement, timeout=maxTime)
        # We get the list right away. It will actually be filled in over time
        # and will stop only after the timeout.
        total_advert = 0
        for advert in list:
            total_advert = total_advert + 1
            addr = advert.address
            if advert.scan_response or addr in found:
                # A response is an advertisement response. We're just
                # looking for a plain advert, so skip those.
                # We also don't need to revisit device we're already
                # looked at.
                continue
            found.add(addr)
            if type(advert) is ProvideServicesAdvertisement:
                svs = advert.services
                if BtCurrentTimeServiceClient.uuid in svs:
                    timeServiceConnection = ble.connect(addr)
                    break
        # Should match the start_scan with stop_scan.
        ble.stop_scan()
        return timeServiceConnection

    def ConnectToCurrentTimeService(self, ble, connection, do_trace=True):
        service = None
        if BtCurrentTimeServiceClient.uuid not in connection:
            print("Error: in ConnectToService: expected service UUID in connection")
            return

        if (connection.connected is False):
            print("Error: in ConnectToService: expected a connected connection")
            return

        try:
            service = connection[BtCurrentTimeServiceClient]
            # Gets the entire "Current Time" service with UUID 0x1805 regardless
            # of whether it's got the right characteristics.
            if (service is not None):
                if (do_trace):
                    ts = service.GetTimeString()
                    print("TRACE: BtClock: time_string=", ts)

        except Exception as ex:
            print("ERROR: in ConnectToService: Clock: exception when getting data", ex)
        return service
