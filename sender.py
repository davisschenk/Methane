#!/usr/bin/env python3

import serial
import json
import time
import memcache

# from itertools import cycle
# from fileinput import FileInput

# fi = cycle(FileInput(["data"]))

# def get_data_dummy():
#     return json.loads(next(fi))

SERIAL_ID = "usb-FTDI_FT230X_Basic_UART_DN0699ZS-if00-port0"
VARS = ["Methane", "GPSTime", "Latitude", "Longitude"]
shared = memcache.Client(['127.0.0.1:11211'], debug=0)



def get_data():
    return shared.get_multi(VARS)

if __name__ == "__main__":
    s = serial.Serial(f"/dev/serial/by-id/{SERIAL_ID}", baudrate=57600)

    while True:
        data = get_data()
        j = json.dumps(data, default=str) + "\n"
        encoded = j.encode('ascii')
        s.write(encoded)
        time.sleep(0.2)
