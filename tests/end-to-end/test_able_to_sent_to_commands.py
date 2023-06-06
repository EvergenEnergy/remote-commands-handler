import time
import json
import random

import pytest

import paho.mqtt.client as mqtt
from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

@pytest.mark.end_to_end
def test_able_to_update_coil():
    random_value = random.randint(1, 2) % 2 == 0

    message_dictionary = {
        "action": "testRegister",
        "value": random_value
    }
    message = json.dumps(message_dictionary)

    mqttClient = mqtt.Client()
    modbusClient = ModbusTcpClient(
        "localhost",
        5020,
    )


    modbusClient.connect()
    mqttClient.connect("localhost", 1883, 60)

    mqttClient.publish("commands/test", message)

    time.sleep(5)

    value = modbusClient.read_coils(504, 1, 1)

    assert value.bits[0] is random_value
    modbusClient.close()
    mqttClient.disconnect()

@pytest.mark.end_to_end    
def test_able_to_send_integer16():
    random_value = random.randint(0, 30)
    message_dictorionary = {
        "action": "testRegister",
        "value": random_value
    }

    message = json.dumps(message_dictorionary)

    mqttClient = mqtt.Client()
    modbusClient = ModbusTcpClient(
        "localhost",
        5020,
    )


    modbusClient.connect()
    mqttClient.connect("localhost", 1883, 60)

    mqttClient.publish("commands/test", message)

    time.sleep(1)

    value = modbusClient.read_holding_registers(1, 1, 1)

    assert value.registers[0] == random_value
    modbusClient.close()
    mqttClient.disconnect()

@pytest.mark.end_to_end
def test_able_to_send_float32():
    random_value = random.uniform(0, 30)
    message_dictionary = {
        "action": "testFloatRegister",
        "value": random_value
    }

    message = json.dumps(message_dictionary)

    mqttClient = mqtt.Client()
    modbusClient = ModbusTcpClient(
        "localhost",
        5020,
    )

    modbusClient.connect()
    mqttClient.connect("localhost", 1883, 60)

    mqttClient.publish("commands/test", message)

    time.sleep(1)

    value = modbusClient.read_holding_registers(2, 4, 1)

    decoder = BinaryPayloadDecoder.fromRegisters(value.registers, Endian.Big, wordorder=Endian.Big)

    assert round(decoder.decode_32bit_float(), 4) == round(random_value, 4)
    modbusClient.close()
    mqttClient.disconnect()

@pytest.mark.end_to_end
def test_able_to_send_command_with_float64():
    random_value = random.uniform(0, 30)
    message_dictionary = {
        "action": "testFloat64Register",
        "value": random_value
    }

    message = json.dumps(message_dictionary)

    mqttClient = mqtt.Client()
    modbusClient = ModbusTcpClient(
        "localhost",
        5020,
    )


    modbusClient.connect()
    mqttClient.connect("localhost", 1883, 60)

    mqttClient.publish("commands/test", message)

    time.sleep(1)

    value = modbusClient.read_holding_registers(3, 8, 1)

    decoder = BinaryPayloadDecoder.fromRegisters(value.registers, Endian.Big, wordorder=Endian.Big)
    assert decoder.decode_64bit_float() == random_value
    modbusClient.close()
    mqttClient.disconnect()

@pytest.mark.end_to_end
def test_able_to_send_integer64():
    random_value = random.randint(0, 100)
    message_dictorionary = {
        "action": "testInt64Register",
        "value": random_value
    }

    message = json.dumps(message_dictorionary)

    mqttClient = mqtt.Client()
    modbusClient = ModbusTcpClient(
        "localhost",
        5020,
    )


    modbusClient.connect()
    mqttClient.connect("localhost", 1883, 60)

    mqttClient.publish("commands/test", message)

    time.sleep(1)

    value = modbusClient.read_holding_registers(20, 8, 1)

    decoder = BinaryPayloadDecoder.fromRegisters(value.registers, Endian.Big, wordorder=Endian.Big)

    assert decoder.decode_64bit_int() == random_value
    modbusClient.close()
    mqttClient.disconnect()

@pytest.mark.end_to_end
def test_able_to_send_uint64():
    random_value = random.randint(0, 100)
    message_dictorionary = {
        "action": "testUInt64Register",
        "value": random_value
    }

    message = json.dumps(message_dictorionary)

    mqttClient = mqtt.Client()
    modbusClient = ModbusTcpClient(
        "localhost",
        5020,
    )


    modbusClient.connect()
    mqttClient.connect("localhost", 1883, 60)

    mqttClient.publish("commands/test", message)

    time.sleep(1)

    value = modbusClient.read_holding_registers(30, 8, 1)

    decoder = BinaryPayloadDecoder.fromRegisters(value.registers, Endian.Big, wordorder=Endian.Big)

    assert decoder.decode_64bit_uint() == random_value
    modbusClient.close()
    mqttClient.disconnect()