
import math
import time

class Annunciator_Clock:
    def __init__(self, led):  # led is a neopixel
        self.led = led
        self.Off = (0x00, 0x00, 0x00)
        self.Dark = (0x0, 0x0, 0x10)
        self.Mid = (0x0, 0x0, 0x60)
        self.Bright = (0x0, 0x0, 0xFF)
        self.Fail = (0x90, 0x0, 0x0)
        self.FlashTime = 0.1
        self.curr_tick = 0

    def Start(self):
        print("BT: Start clock")
        self.led[0] = self.Mid

    def Tick(self):
        tick = self.curr_tick % 4
        if (tick < 2):
            self.led[0] = self.Dark
            self.curr_tick = self.curr_tick + 1
        else:
            self.led[0] = self.Mid
            self.curr_tick = self.curr_tick + 1

    def End(self):
        print("BT: End clock")
        self.led[0] = self.Off

    def Found(self):
        print("BT: Clock found")
        self.led[0] = self.Bright
        time.sleep(self.FlashTime)
        self.led[0] = self.Mid

    def NotFound(self):
        print("BT: Clock not found")
        self.led[0] = self.Fail
        time.sleep(self.FlashTime)
        self.led[0] = self.Dark

    def Read(self):
        print("BT: Clock read")
        self.led[0] = self.Bright
        time.sleep(self.FlashTime)
        self.led[0] = self.Mid

class Wave_Sin:
    """ Given a number 0..1 produces a sin wave """
    def value(self, time):
        radian = time * 2.0 * math.pi
        retval = math.sin(radian)
        return retval


class Annunciator_Sensor:
    def __init__(self, led):
        self.led = led
        self.Off = (0x00, 0x00, 0x00)
        self.Dark = (0x0, 0x0, 0x10)
        self.Mid = (0x0, 0x0, 0x60)
        self.Bright = (0x0, 0x00, 0xff)
        self.Fail = (0x90, 0x0, 0x0)
        self.FlashTime = 0.1
        self.curr_tick = 0
        self.wave = Wave_Sin()

    def Start(self):
        print("BT: Start sensor")
        self.led[0] = self.Mid

    def Tick(self):
        value = self.wave.value(self.curr_tick)
        delta = self.Mid[2] - self.Dark[2]
        rgb = (self.Mid[0], self.Mid[1], self.Dark[2]+(delta*value))
        self.led[0] = rgb
        self.curr_tick = self.curr_tick + 0.1

    def End(self):
        print("BT: End ")
        self.led[0] = self.Off

    def Found(self):
        print("BT: Sensor found")
        self.led[0] = self.Bright
        time.sleep(self.FlashTime)
        self.led[0] = self.Mid

    def NotFound(self):
        print("BT: Sensor not found")
        self.led[0] = self.Fail
        time.sleep(self.FlashTime)
        self.led[0] = self.Dark

    def Read(self):
        print("BT: Sensor read")
        self.led[0] = self.Bright
        time.sleep(self.FlashTime)
        self.led[0] = self.Mid



