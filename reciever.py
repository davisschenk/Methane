#!/usr/bin/env python3

import serial
import logging
import json
import binascii
import websockets
import asyncio
from functools import partial
from serial_asyncio import open_serial_connection
import sys
import concurrent

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

SERIAL_ID = "usb-FTDI_FT230X_Basic_UART_D306NR9G-if00-port0"
CLIENTS = set()

s = serial.Serial(f"/dev/serial/by-id/{SERIAL_ID}", baudrate=57600)
# s = serial.Serial(f"/dev/ttyUSB1", baudrate=57600)

def get_line():
    logging.info("Called get_line")
    data = s.readline()
    logging.info(data)
    return data

# Runs blocking function in executor, yielding the result
async def get_line_async():
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_line)

async def broadcast_messages():
    logging.debug(f"Started broadcasting")
    while True:
        data = await get_line_async()
        logging.debug(f"Got data: {data}")

        try:
            j = json.loads(data)
        except json.JSONDecodeError:
            logging.error("Failed to parse json")
            continue

        # try:
        #     for k, v in j.values():
        #         if k.endswith("_crc"):
        #             continue

        #         if binascii.crc32(v.encode('ascii')) != j[k + "_crc"]:
        #             raise ValueError

        # except ValueError:
        #     logging.error("CRC Failed")
        #     continue

        websockets.broadcast(CLIENTS, json.dumps(j))
        logging.info(f"Broadcast {j}")


async def handler(websocket, path):
    CLIENTS.add(websocket)
    logging.info("Client joined")
    try:
        async for _ in websocket:
            pass
    finally:
        CLIENTS.remove(websocket)
        logging.info("Client left")


async def main():
    async with websockets.serve(handler, "localhost", 8765) as ws:
        asyncio.create_task(broadcast_messages())
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
