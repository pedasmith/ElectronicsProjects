# Write your code here :-)

class UserPreferences:
    """Trivial class that lists the user's units preferences. For example:
    time type can be either a 24-hour clock or an am/pm type clock
    temperature can be displayed in C or F
    """
    TIME_24HR = 10
    TIME_AMPM = 11
    TEMP_C = 20
    TEMP_F = 21

    def __init__(self):
        self.Time = self.TIME_24HR
        self.Temp = self.TEMP_F

    def TempToStr(self, temp):
        if (temp == self.TEMP_C):
            return "C"
        if (temp == self.TEMP_F):
            return "F"
        return f"?{temp}"

    def TimeToStr(self, time):
        if (time == self.TIME_24HR):
            return "24hr"
        if (time == self.TIME_AMPM):
            return "ampm"
        return f"?{time}"

    def __str__(self):
        retval = f"Units: {self.TimeToStr(self.Time)} {self.TempToStr(self.Temp)}"
        return retval

    def SetFromBtUserUnitPreference(self, value):
        """Given a BT UserUnitPreferences array (an array of ushort that contains
        the BT official 2-byte values for various units like 0x272F for degress C),
        update the user preferences. Note that the incoming preferences include
        "no preference" for some units. For those, we don't update the user preference.
        Also note that the values can be in any order.
        """
        for item in value:
            if (item == 0):
                pass
            elif (item == 0x272F):
                self.Temp = self.TEMP_C
            elif (item == 0x27AC):
                self.Temp = self.TEMP_F
            elif (item == 0x8024):
                self.Time = self.TIME_24HR
            elif (item == 0x8025):
                self.Time = self.TIME_AMPM
            else:
                print(f"TRACE: Unknown unit={hex(item)}")

