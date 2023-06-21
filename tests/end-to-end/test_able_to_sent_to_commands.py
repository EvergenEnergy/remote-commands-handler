import os
import time
import json
import random

import pytest

import paho.mqtt.client as mqtt
from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian


@pytest.fixture(scope="module")
def mqtt_client():
    client = mqtt.Client()
    client.connect("localhost", 1883, 60)
    yield client  # provide the client for tests
    client.disconnect()  # disconnect after tests


@pytest.fixture(scope="module")
def modbus_client():
    client = ModbusTcpClient("localhost", 5020)
    client.connect()
    yield client  # provide the client for tests
    client.close()  # close after tests


@pytest.mark.end_to_end
@pytest.mark.parametrize("coil_value", [False, True])
def test_able_to_update_coil(
    mqtt_client: mqtt.Client, modbus_client: ModbusTcpClient, coil_value: bool
):
    message_dictionary = {"action": "testCoil", "value": coil_value}
    message = json.dumps(message_dictionary)

    mqtt_client.publish("commands/test", message)

    time.sleep(1)

    value = modbus_client.read_coils(504, 1, 1)

    assert value.bits[0] is coil_value


@pytest.mark.end_to_end
def test_able_to_send_integer16(
    mqtt_client: mqtt.Client, modbus_client: ModbusTcpClient
):
    random_value = random.randint(0, 30)
    message_dictionary = {"action": "testRegister", "value": random_value}

    message = json.dumps(message_dictionary)

    mqtt_client.publish("commands/test", message)

    time.sleep(1)

    value = modbus_client.read_holding_registers(1, 1, 1)

    assert value.registers[0] == random_value


@pytest.mark.end_to_end
def test_able_to_send_float32(mqtt_client: mqtt.Client, modbus_client: ModbusTcpClient):
    random_value = random.uniform(0, 30)
    message_dictionary = {"action": "testFloatRegister", "value": random_value}

    message = json.dumps(message_dictionary)

    mqtt_client.publish("commands/test", message)

    time.sleep(1)

    value = modbus_client.read_holding_registers(2, 4, 1)

    decoder = BinaryPayloadDecoder.fromRegisters(
        value.registers, Endian.Big, wordorder=Endian.Big
    )

    assert round(decoder.decode_32bit_float(), 4) == round(random_value, 4)


@pytest.mark.end_to_end
def test_able_to_send_command_with_float64(
    mqtt_client: mqtt.Client, modbus_client: ModbusTcpClient
):
    random_value = random.uniform(0, 30)
    message_dictionary = {"action": "testFloat64Register", "value": random_value}

    message = json.dumps(message_dictionary)

    mqtt_client.publish("commands/test", message)

    time.sleep(1)

    value = modbus_client.read_holding_registers(3, 8, 1)

    decoder = BinaryPayloadDecoder.fromRegisters(
        value.registers, Endian.Big, wordorder=Endian.Big
    )
    assert decoder.decode_64bit_float() == random_value


@pytest.mark.end_to_end
def test_able_to_send_integer64(
    mqtt_client: mqtt.Client, modbus_client: ModbusTcpClient
):
    random_value = random.randint(0, 100)
    message_dictionary = {"action": "testInt64Register", "value": random_value}

    message = json.dumps(message_dictionary)

    mqtt_client.publish("commands/test", message)

    time.sleep(1)

    value = modbus_client.read_holding_registers(20, 8, 1)

    decoder = BinaryPayloadDecoder.fromRegisters(
        value.registers, Endian.Big, wordorder=Endian.Big
    )

    assert decoder.decode_64bit_int() == random_value


@pytest.mark.end_to_end
def test_able_to_send_uint64(mqtt_client: mqtt.Client, modbus_client: ModbusTcpClient):
    random_value = random.randint(0, 100)
    message_dictionary = {"action": "testUInt64Register", "value": random_value}

    message = json.dumps(message_dictionary)

    mqtt_client.publish("commands/test", message)

    time.sleep(1)

    value = modbus_client.read_holding_registers(30, 8, 1)

    decoder = BinaryPayloadDecoder.fromRegisters(
        value.registers, Endian.Big, wordorder=Endian.Big
    )

    assert decoder.decode_64bit_uint() == random_value


@pytest.mark.end_to_end
def test_read_error_messages(mqtt_client: mqtt.Client):
    # Subscribe to the error topic and write messages to file
    msg_log = "/tmp/message_log"
    if os.path.exists(msg_log):
        os.remove(msg_log)

    def read_error(_client, _userdata, message):
        # When we get an error message from MQTT, write it to file
        msg_str = message.payload.decode()
        msg_obj = json.loads(msg_str)
        with open(msg_log, "a") as err:
            err.write(f"{msg_str}\n")
        return msg_obj

    mqtt_client.subscribe("error/#")
    mqtt_client.on_message = read_error

    # Generate two error messages by sending bad commands
    def send_bad_command(msg_obj):
        message = json.dumps(msg_obj)
        mqtt_client.publish("commands/test", message)

    send_bad_command({"invalid": ["message", "structure"]})
    send_bad_command({"action": "NotARealCoil", "value": 0})

    # Run the client loop to allow the callback to be executed
    mqtt_client.loop_start()
    time.sleep(1)
    mqtt_client.loop_stop()

    # Check the file for error messages
    with open(msg_log) as err_in:
        line1 = err_in.readline()
        line2 = err_in.readline()
    assert "InvalidMessage" in line1
    assert "UnknownCommand" in line2

    os.remove(msg_log)
