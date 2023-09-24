# About the Ink Govee Listener project

This project gathers in Bluetooth sensor data from a Govee 5074 sensor and displays it on an e-ink display. The board used is an Adafruit nrf52840 and is programmed in CircuitPython. The device will be initialized over-the-air from the Simple Current Time Service program from the Microsoft store; that app lets the user set up the current time + user preferences for the units to be displayed (temperature in F or C, and the time as AM/PM or 24 hour).

The device is normally battery powered and is recharged via USB. This is all done with the built-in circuitry of the nrf52840. The same USB is used to program the device.

The device does not include any buttons that the user will normally press.

## Files

* code.py 
* GoveeScanner.py, Govee5074.py
* BtCurrentTimeServiceClient.py, BtCurrentTimeServiceClientRunner.py, UserPreferences.py
* BtNeoPixelAnnunciator.py, GoveeDisplay.py
* Junk files: mainForInvestigatingLabelRedrawBug.py, mainBugLabelRedraw_2.py, code_Demonstrate_Problem_With_Bitmap.py

### Required libraries:

* File: *adafruit_ssd1680.mpy* for the e-ink display
* File: *neopixel.mpy* for the annunciator (blue light)
* Directory: *adafruit_display_text* for all of the labels
* Directory: *adafruit_ble* for the Bluetoth

### code.py

Main program file


### Display + Annunciator: BtNeoPixelAnnunciator.py, GoveeDisplay.py 

BtNeoPixekAnnunciator.py is a simple class that lights up the built-in NeoPixel based on the current state of reading in the clock or the Govee.
GoveeDisplay.py sets up the display. It knows about the goals of the program (e.g., it knows that the temperature should be in a large font), the data available (voltage of the nrf52840, the status of the Govee sensor, data from the real-time clock) and the capabilities of the display.

Note that some of the display code is also in code.py


### Current Time Service + user preference files: BtCurrentTimeServiceClient.py, BtCurrentTimeServiceClientRunner.py, UserPreferences.py

These two files handle reading in the current time from a nearby BT current time service app -- I use the Simple Current Time Service program on the Microsoft store. This also handles the user preferences.

The clock makes use of an *annunciator** to show off what's happening

### Govee files: Govee5074.py, GoveeScanner.py

Govee5074.py knows how to parse an incoming packet (a buffer of bytes) into temperature + humidity (and battery) and holds that data.

GoveeScanner.py is similar to the BtCurrentTimeServiceClientRunner.py. It looks for adverts that match the Govee 5074, then looks for advert responses that match that, and then pulls out the manufacturer section (0xFF per Bluetooth SIG), then pulls out the corrsponding buffer. The buffer is then parsed with the Govee5074.py code. This split makes it simpler to (potentially) support other types of sensors.



### Libraries and Links

The [Simple Bluetooth Current Time Service](https://apps.microsoft.com/store/detail/simple-bluetooth-current-time-service/9NJQ3TD3K06F?hl=en-us&gl=us) app runs on a Windows computer and broadcasts out the current date and time over Bluetooth. This is the app I use to set the clock on the device. 

Specification for the [Current  Time Service](https://www.bluetooth.com/specifications/specs/current-time-service-1-1/) are on the Bluetooth SIG site.


The e-ink uses the **SSD1680** chipset. There's a [learn](https://learn.adafruit.com/adafruit-2-13-eink-display-breakouts-and-featherwings) path, but beware! the path is written for a bunch of different devices at once; you have to keep track of which is which. The [CircuitPython](https://learn.adafruit.com/adafruit-2-13-eink-display-breakouts-and-featherwings/circuitpython-usage) stuff is fiarly far into the learning path.

The display uses digital pins 5, 6, 9, 10. It also uses the SPI, but that's a shared resource.

Available pins are the digital 11, 12, 13, plus D2. Analog pins A0 to A5 are available (but isn't one used for the battery voltage?)

Use the **adafruit_ssd1680.mpy** library file.

Adafruit [nrf52840](https://learn.adafruit.com/introducing-the-adafruit-nrf52840-feather/circuitpython-pins-and-modules) CircuitPython info

The *struct_time* datetime value is documented at [struct_time](https://docs.circuitpython.org/en/latest/shared-bindings/time/index.html#time.struct_time)