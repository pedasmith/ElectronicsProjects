# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2021 Melissa LeBlanc-Williams
# for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

"""Simple test script for 2.13" 250x122 tri-color display.
Supported products:
  * Adafruit 2.13" Tri-Color eInk Display Breakout
    * https://www.adafruit.com/product/4947
  * Adafruit 2.13" Tri-Color eInk Display FeatherWing
    * https://www.adafruit.com/product/4814
  * Adafruit 2.13" Mono eInk Display FeatherWing
    * https://www.adafruit.com/product/4195


"""

import time
import board
from analogio import AnalogIn
import displayio
import adafruit_ssd1680

from GoveeDisplay import GoveeDisplay

import rtc
# import adafruit_ble
import BtCurrentTimeServiceClientRunner
import GoveeScanner
from UserPreferences import UserPreferences
import neopixel
import BtNeoPixelAnnunciator


led = neopixel.NeoPixel(board.NEOPIXEL, 1)
annunciator_clock = BtNeoPixelAnnunciator.Annunciator_Clock(led)
annunciator_sensor = BtNeoPixelAnnunciator.Annunciator_Sensor(led)

# Set up displays
displayio.release_displays()
DISPLAY_WIDTH = 250
DISPLAY_HEIGHT = 122


# This pinout works on a Metro M4 and may need to be altered for other boards.
spi = board.SPI()  # Uses SCK and MOSI
epd_cs = board.D9
epd_dc = board.D10
epd_reset = None  # board.D8  # Set to None for FeatherWing
epd_busy = None  # board.D7  # Set to None for FeatherWing

display_bus = displayio.FourWire(
    spi, command=epd_dc, chip_select=epd_cs, reset=epd_reset, baudrate=1000000
)
time.sleep(1)

# For issues with display not updating top/bottom rows correctly set colstart to 8
display = adafruit_ssd1680.SSD1680(
    display_bus,
    colstart=8,  # NOTE: Use 8 and not 0 for some displays, seemingly at random
    width=DISPLAY_WIDTH,
    height=DISPLAY_HEIGHT,
    busy_pin=epd_busy,
    highlight_color=0xFF0000,
    rotation=270,
)

clock = rtc.RTC()

def SetupRtcClock(userprefs, annunciator):
    annunciator.Start()
    timeservice = BtCurrentTimeServiceClientRunner.BtCurrentTimeServiceClientRunner()
    (service, timeServiceConnection) = timeservice.Scan(annunciator, GOAL_TIME=5)
    if service is None:
        time.sleep(1)
        annunciator.NotFound()
        annunciator.End()
    else:
        # (y, m, d, hh, mm, ss, j1, j2, j3) = timeresult.data
        # returns e.g., (year, mon, day, hour, minute, second, 6, 0, 1)
        # https://docs.circuitpython.org/en/latest/shared-bindings/time/index.html#time.struct_time
        annunciator.Found()
        now = service.GetTimeAsStructTime()
        prefdata = service.GetUserUnitPreferences()
        userprefs.SetFromBtUserUnitPreference(prefdata)

        # Tidy up the Bluetooth bits.
        timeServiceConnection.disconnect()
        timeServiceConnection = None
        service = None  # after the connection is terminated, service is also dead (?)

        clock.datetime = now  # clock.datetime is a time.struct_time
        annunciator.End()

def StressTestClock(annunciator):
    """Stress test getting the clock data to verify that it's working
    reliably to get BT clock.
    """
    # ble = adafruit_ble.BLERadio()
    NSTRESS = 50
    timeservice = BtCurrentTimeServiceClientRunner.BtCurrentTimeServiceClientRunner()
    nok = 0
    nerror = 0
    for i in range(NSTRESS):
        time.sleep(5)
        (service, testconn) = \
            timeservice.Scan(annunciator, GOAL_TIME=2, do_trace=False)
        if service is None:
            nerror = nerror + 1
        else:
            nok = nok + 1
            testconn.disconnect()
            testconn = None
            service = None  # after connection is terminated, service is also dead (?)
    print(f"TRACE: StressTestClock: nok={nok} nerror={nerror}")


def TimeToEvenClock(datetime):
    """Given a datetime (e.g., from rtc.RTC().datetime) struct, return the number of
    seconds until there's a nice even number of minutes on the clock."""
    EVENTIME = 5 * 60
    secs = (datetime.tm_min * 60) + datetime.tm_sec
    nsec = secs % EVENTIME
    retval = EVENTIME - nsec
    if nsec == 0:
        retval = 0
    # ms = f"@{datetime.tm_min}:{datetime.tm_sec}"
    # print(f"TRACE: {ms} secs=", secs, "nsec=", nsec, "retval=", retval)
    return retval


def TimeToEvenClockTestOne(h, m, s, expected):
    nerror = 0
    dt = time.struct_time((2020, 3, 15, h, m, s, 0, -1, -1))
    actual = TimeToEvenClock(dt)
    if actual != expected:
        print(f"ERROR: TimeToEvenClock({h},{m},{s}) s.b.={expected} actual={actual}")
        nerror = nerror + 1
    return nerror


def TimeToEvenClockTest():
    nerror = 0
    nerror += TimeToEvenClockTestOne(0, 0, 0, 0)
    nerror += TimeToEvenClockTestOne(0, 2, 59, 121)
    nerror += TimeToEvenClockTestOne(0, 3, 0, 120)
    nerror += TimeToEvenClockTestOne(0, 3, 1, 119)

    nerror += TimeToEvenClockTestOne(0, 52, 59, 121)
    nerror += TimeToEvenClockTestOne(0, 53, 0, 120)
    nerror += TimeToEvenClockTestOne(0, 53, 1, 119)
    return nerror


def TimeToWaitForEvenClock(datetime):
    """Main function to return how long to wait for a nice even clock time"""
    seconds = TimeToEvenClock(datetime)
    return seconds


#
# Do all the startup self-tests.
# As of 2023-09-06, there's only the one :-)

print("TRACE: SYSTEM_TEST: START")
nerror = 0  # All errors
nerror += TimeToEvenClockTest()
# Works fine as of 2023-09-07 StressTestClock()
print(f"TRACE: SYSTEM_TESTS: DONE with DONE WITH NERROR={nerror}")


# NOTE: originally the idea was to include this background image.
# But it causes redisplay problems: labels get redrawn as all-black
# However, since then I've put in a stronger workaround, and will
# totally redo the display -- so we could have an image.
# pic = displayio.OnDiskBitmap("/background.bmp")
# with open("/background.bmp", "rb") as f:
#    pic = displayio.OnDiskBitmap(f)
# t = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)
# g.append(t)

userprefs = UserPreferences()
doBT = True
if doBT:
    SetupRtcClock(userprefs, annunciator_clock)
    # will fill in the userprefs with data from the BT.


gd = GoveeDisplay()

mainDisplayGroup = gd.MakeDisplayGroup(userprefs, DISPLAY_WIDTH, DISPLAY_HEIGHT)
# TODO: remove all these
# mainDisplayGroupd = displayio.Group()  # reused
# bkgtg = gd.MakeBackgroundImage(DISPLAY_WIDTH, DISPLAY_HEIGHT)  # NOTE: just here
# mainDisplayGroup.append(bkgtg)
# clockTextGroup = displayio.Group()  # NOTE: just here
# gd.SetupClockTextGroup(userprefs, clockTextGroup)  # makes labels + adds them to group
# mainDisplayGroup.append(clockTextGroup)

display.show(mainDisplayGroup)  # won't show until I do a refresh

#
# Power and battery section
#
batteryPin = AnalogIn(board.VOLTAGE_MONITOR)

def get_battery_voltage():
    return 2.0 * (batteryPin.value * 3.3) / 65536.0

goveeScanner = GoveeScanner.GoveeScanner()

# Some of the samples do a sleep of 120. This is wrong in two ways.
# Firstly, you have to sleep for 180 seconds (3 minutes). Secondly,
# there's a new value on the display that says how much longer you
# have to wait. And additionally, different OSes have different amounts
# of variability for sleeping / waiting; some of them can sleep a little
# less than the requested time.
if display.time_to_refresh > 0:
    time.sleep(display.time_to_refresh + 5)

voltage = get_battery_voltage()
scanResult = goveeScanner.Scan(annunciator_sensor)
gd.ShowGovee(userprefs, scanResult, clock.datetime, voltage)
display.refresh()

print("TRACE: Did first refresh; clock started: note TTR=", display.time_to_refresh)

while True:
    tts = 4 * 60
    time.sleep(tts)  # sleep almost 5 minutes
    while display.time_to_refresh > 0:
        time.sleep(display.time_to_refresh + 5)
        # Always refresh a little longer. It's not a problem to refresh
        # a few seconds more, but it's terrible to refresh too early
        # (the display will throw an exception when if the refresh
        # is too soon)

    # Get the latest temp + humidity
    scanResult = goveeScanner.Scan(annunciator_sensor)
    print("TRACE: scan results: ", scanResult, ", about to show and display.refresh")

    #
    # There's a funny problem I have with e-ink displays. When I do
    # an update, and there are multiple labels, and depending on the
    # background image, the labels might update as completely black.
    # AFAICT, this depends on the source of the background image,
    # the number of labels, the font size (IIRC), and the length of
    # the string.
    #
    # My solution is to redo the display setup, which seems to workaround
    # pretty reliably.
    #
    # I also tried setting up a new background and new set of text groups
    # and displaying that, but it didn't help.
    # TODO: don't need to rebuild the display_bus
    displayio.release_displays()
    display_bus = displayio.FourWire(
        spi, command=epd_dc, chip_select=epd_cs, reset=epd_reset, baudrate=1000000
    )
    time.sleep(1)

    # For issues with display not updating top/bottom rows correctly set colstart to 8
    display = adafruit_ssd1680.SSD1680(
        display_bus,
        colstart=8,
        width=DISPLAY_WIDTH,
        height=DISPLAY_HEIGHT,
        busy_pin=epd_busy,
        highlight_color=0xFF0000,
        rotation=270,
    )
    # We can use the existing group with the new display.
    display.show(mainDisplayGroup)

    #
    # Wait for a time that's evenly divisible by 5. That means that sometimes
    # the scan results will be a little late.
    #
    wait = TimeToWaitForEvenClock(clock.datetime)
    if wait < 4 * 60:  # If it's e.g., 3:44:59
        time.sleep(wait)

    voltage = get_battery_voltage()
    gd.ShowGovee(userprefs, scanResult, clock.datetime, voltage)
    display.refresh()

# All done!
