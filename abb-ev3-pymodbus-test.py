#!/usr/bin/env python3
"""Pymodbus asynchronous client example.

An example of a single threaded asynchronous client.

usage: simple_async_client.py

All options must be adapted in the code
The corresponding server must be started before e.g. as:
    python3 server_sync.py
"""
import asyncio
import struct
from pprint import pprint

import pymodbus.client as ModbusClient
from pymodbus import (
    ExceptionResponse,
    Framer,
    ModbusException,
    pymodbus_apply_logging_config,
)


async def run_async_simple_client(comm, host, port, framer=Framer.SOCKET):
    """Run async client."""
    # activate debugging
    pymodbus_apply_logging_config("DEBUG")

    print("get client")
    if comm == "tcp":
        client = ModbusClient.AsyncModbusTcpClient(
            host,
            port=port,
            framer=framer,
            timeout=10,
            retries=3,
            # retry_on_empty=False,
            # source_address=("localhost", 0),
        )
    elif comm == "udp":
        client = ModbusClient.AsyncModbusUdpClient(
            host,
            port=port,
            framer=framer,
            # timeout=10,
            # retries=3,
            # retry_on_empty=False,
            # source_address=None,
        )
    elif comm == "serial":
        client = ModbusClient.AsyncModbusSerialClient(
            port,
            framer=framer,
            timeout=10,
            retries=3,
            # retry_on_empty=False,
            # strict=True,
            baudrate=9600,
            bytesize=8,
            parity="E",
            stopbits=1,
            # handle_local_echo=False,
        )
    elif comm == "tls":
        client = ModbusClient.AsyncModbusTlsClient(
            host,
            port=port,
            framer=Framer.TLS,
            # timeout=10,
            # retries=3,
            # retry_on_empty=False,
            # sslctx=sslctx,
            certfile="../examples/certificates/pymodbus.crt",
            keyfile="../examples/certificates/pymodbus.key",
            # password="none",
            server_hostname="localhost",
        )
    else:
        print(f"Unknown client {comm} selected")
        return

    print("connect to server")
    await client.connect()
    # test client is connected
    assert client.connected

    print("get and verify data")
    try:
        # See all calls in client_calls.py
        # serial_number
        #rr = await client.read_holding_registers(0x0402, 3)

        # total_active_power
        #rr = await client.read_holding_registers(0x5b14, 2, slave=1)
        # abb_ev3_active_export_energy_total
        rr = await client.read_holding_registers(0x5000, 4, slave=1)

        # firmware version
        #rr = await client.read_holding_registers(0x8908, 8, slave=1)
        # total power factor
        # rr = await client.read_holding_registers(0x5B3A, 1, slave=1)
    except ModbusException as exc:
        print(f"Received ModbusException({exc}) from library")
        client.close()
        return
    if rr.isError():
        print(f"Received Modbus library error({rr})")
        client.close()
        return
    if isinstance(rr, ExceptionResponse):
        print(f"Received Modbus library exception ({rr})")
        # THIS IS NOT A PYTHON EXCEPTION, but a valid modbus message
        client.close()

    pprint(rr.registers)
    bytestring = struct.pack('>HHHH', *rr.registers)
    value = struct.unpack('>Q', bytestring)[0]
    number_of_decimals = 4

    pprint(float(value) / 10 ** number_of_decimals)

    print("close connection")
    client.close()


if __name__ == "__main__":
    asyncio.run(
        #run_async_simple_client("tcp", "192.168.1.2", 502), debug=True
        run_async_simple_client("tcp", "localhost", 502), debug=True
        #run_async_simple_client("serial", "localhost", "/dev/ttyUSB0", framer=Framer.RTU), debug=True
    )
