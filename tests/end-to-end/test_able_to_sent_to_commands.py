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
def test_able_to_update_coil(mqtt_client: mqtt.Client, modbus_client: ModbusTcpClient):
    random_value = random.randint(1, 2) % 2 == 0

    message_dictionary = {"action": "testCoil", "value": random_value}
    message = json.dumps(message_dictionary)

    mqtt_client.publish("commands/test", message)

    time.sleep(1)

    value = modbus_client.read_coils(504, 1, 1)

    assert value.bits[0] is random_value


@pytest.mark.end_to_end
def test_able_to_send_integer16(mqtt_client: mqtt.Client, modbus_client: ModbusTcpClient):
    random_value = random.randint(0, 30)
    message_dictorionary = {"action": "testRegister", "value": random_value}

    message = json.dumps(message_dictorionary)

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
def test_able_to_send_command_with_float64(mqtt_client: mqtt.Client, modbus_client: ModbusTcpClient):
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
def test_able_to_send_integer64(mqtt_client: mqtt.Client, modbus_client: ModbusTcpClient):
    random_value = random.randint(0, 100)
    message_dictorionary = {"action": "testInt64Register", "value": random_value}

    message = json.dumps(message_dictorionary)

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
    message_dictorionary = {"action": "testUInt64Register", "value": random_value}

    message = json.dumps(message_dictorionary)

    mqtt_client.publish("commands/test", message)

    time.sleep(1)

    value = modbus_client.read_holding_registers(30, 8, 1)

    decoder = BinaryPayloadDecoder.fromRegisters(
        value.registers, Endian.Big, wordorder=Endian.Big
    )

    assert decoder.decode_64bit_uint() == random_value
