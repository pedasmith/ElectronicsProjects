import struct

class Govee5074:
    """Knows how to parse data for a Govee 5074 temperature / humidity sensor"""
    def __init__(self, buffer):
        """ Create a Govee5074 from bytes from an advert. Returns None if the
        advert isn't from a Govee 5074."""

        # Sample: 88 ec 00 12 09 99 15 64 02
        # Parsing: 88 ec [company ID is ec88] 00 [junk] 12 09 [temp]
        #        99 15 [hum] 64 [batt] 02 [junk2]
        self.IsOk = False
        if len(buffer) != 9:
            # Surprisingly common to have the wrong sized buffer.
            return

        unpack = struct.unpack("<HbhhBb", buffer)
        self.companyId = unpack[0]
        if (self.companyId != 0xec88):
            print("TRACE: incorrect company Id", hex(self.companyId))
            return

        self.junk1 = unpack[1]
        self.temperatureC = unpack[2] / 100.0
        self.temperatureF = (self.temperatureC * 9.0 / 5.0) + 32
        self.humidity = unpack[3] / 100.0
        self.battery = unpack[4]
        self.IsOk = True
        # print("TRACE: Govee5074", self.temperatureF, self.humidity, self.battery)
        pass

    def __str__(self):
        if (self.IsOk):
            retval = "Govee 5074 " + str(self.temperatureF) + "℉ "
            retval = retval + str(self.humidity) + "% " + str(self.battery)
            return retval
        return "Invalid Govee 5074"



