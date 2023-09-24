# Knows exactly how we want to display data from a 'Govee574' data object
# on the 3-color 2.13 inch e-ink screen. Doesn't know too much about the
# display, but of course knows the exact size the labels will draw at
# and of course knows exactly how we want it layed out.


import displayio
import terminalio
from adafruit_display_text import label
from UserPreferences import UserPreferences

class GoveeDisplay:
    """Creates and updates labels for Govee data. Govee data is just
    temperature and humidity"""
    def __init__(self):   # , group, initialTime="* --:--"):
        self.Font = terminalio.FONT
        self.ColorInk = 0x000000
        # self.ColorBackground = 0x000000

    def MakeDisplayGroup(self, userprefs, width, height):
        """This and ShowGovee are the main methods used to set up and update the
        text labels of the sensor and clock display.
        """
        mainDisplayGroup = displayio.Group()
        bkgtg = self.MakeBackgroundImage(width, height)
        mainDisplayGroup.append(bkgtg)
        clockTextGroup = displayio.Group()  # NOTE: just here
        self.SetupClockTextGroup(userprefs, clockTextGroup)
        mainDisplayGroup.append(clockTextGroup)
        return mainDisplayGroup

    def MakeBackgroundImage(self, width, height):
        """Makes the background image for the display. In this case, it's a plain white
        background.
        """
        # Set a background
        # BLACK = 0x000000
        WHITE = 0xFFFFFF
        # RED = 0xFF0000

        # Change text colors, choose from the following values:
        # BLACK, RED, WHITE

        # FOREGROUND_COLOR = BLACK
        BACKGROUND_COLOR = WHITE

        pic = displayio.Bitmap(width, height, 1)
        # Map colors in a palette
        palette = displayio.Palette(1)
        palette[0] = BACKGROUND_COLOR
        background_tg = displayio.TileGrid(pic, pixel_shader=palette)
        return background_tg

    def SetupClockTextGroup(self, userprefs, group, initialTime="* --:--"):
        """Creates the needed labels (displayio) at the right places for a display"""
        # I decided that there was no value is labeling this.
        # self.ClockTitleLabel = label.Label(
        #     self.Font, color=self.ColorInk, anchor_point=(0, 0),
        #     text="Time", x=20, y=12, scale=3)
        clockX = 125
        if (userprefs.Time == UserPreferences.TIME_AMPM):
            clockX = clockX - 55   # Make room for AM/PM

        self.ClockTimeLabel = label.Label(
            self.Font, color=self.ColorInk, anchor_point=(0, 0),
            text=initialTime, x=clockX, y=12, scale=3)

        self.TemperatureLabel = label.Label(
            self.Font, color=self.ColorInk, anchor_point=(0, 0),
            text="--.-F", x=0, y=55, scale=5)

        self.HumidityLabel = label.Label(
            self.Font, color=self.ColorInk, anchor_point=(0, 0),
            text="--%", x=150, y=100, scale=5)

        self.LastUpdateTimeLabel = label.Label(
           self.Font, color=self.ColorInk, anchor_point=(0, 0),
           text="#.##V+### Update ##:##", x=0, y=115, scale=1)

        self.AboutLabel = label.Label(
            self.Font, color=self.ColorInk, anchor_point=(0, 0),
            text="Govee Ink 2023", x=0, y=105, scale=1)

        # group.append(self.ClockTitleLabel)
        group.append(self.ClockTimeLabel)
        group.append(self.TemperatureLabel)
        group.append(self.HumidityLabel)
        group.append(self.LastUpdateTimeLabel)
        group.append(self.AboutLabel)

    def MakeTimeStr(self, userprefs, dt):
        """Internal method that make a string out of a date given the userprefs.
        Will display either a 24-hour clock (00:00 to 23:59) or a 12-hour clock
        with a proper AM/PM indicator.
        """
        # Set up the 24H version
        timestr = "{:02d}:{:02d}".format(dt.tm_hour, dt.tm_min)
        if (userprefs.Time == UserPreferences.TIME_AMPM):
            h = dt.tm_hour
            ampm = "AM"
            if (h == 0):
                # Example: 00:05 --> 12:05 AM
                h = 12
            elif (h == 12):
                # Example: 12:05 --> 12:05 PM
                ampm = "PM"
            elif (h >= 13):
                # Example: 14:05 -->  2:05 PM
                ampm = "PM"
                h = h - 12
            timestr = "{:2d}:{:02d} {}".format(h, dt.tm_min, ampm)

        return timestr

    def ShowGovee(self, userprefs, govee, dt, voltage):
        """Critical method to update labels based on new govee data and time data. The
        method is smart, and handles the case of the govee data being None
        or where IsOk==False"""
        timestr = self.MakeTimeStr(userprefs, dt)

        if (govee is not None) and (govee.IsOk):
            tempstr = "{:02}°F".format(round(govee.temperatureF, 1))
            if (userprefs.Temp == UserPreferences.TEMP_C):
                tempstr = "{:02}°C".format(round(govee.temperatureC, 1))

            self.TemperatureLabel.text = tempstr
            humstr = "{:02}%".format(round(govee.humidity, 0))
            self.HumidityLabel.text = humstr
            ustr = f"{round(voltage,2)}V+{govee.battery} Update:" + timestr
            self.LastUpdateTimeLabel.text = ustr
            timestr = "  " + timestr
        else:
            timestr = "x " + timestr
            print("TRACE: ShowGovee but it's not ok: ", govee, timestr)
        self.ClockTimeLabel.text = timestr


