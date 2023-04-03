#!/usr/bin/env python3

import serial
import logging
import json
import time
import binascii

from itertools import cycle
from fileinput import FileInput

fi = cycle(FileInput(["data"]))

SERIAL_ID = "usb-FTDI_FT230X_Basic_UART_D306NR9G-if00-port0"


def get_data():
    return json.loads(next(fi))

if __name__ == "__main__":
    s = serial.Serial(f"/dev/serial/by-id/{SERIAL_ID}", baudrate=57600)
    # s = serial.Serial(f"/dev/ttyUSB0", baudrate=57600)


    while True:
        data = get_data()
        print(data)
        # for k, v in data.copy().items():
        #     data[k + "_crc"] = binascii.crc32(bytes(v))

        j = json.dumps(data) + "\n"
        encoded = j.encode('ascii')
        s.write(encoded)
        logging.debug("Wrote data")
        time.sleep(1)
