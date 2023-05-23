import os
import json

from app.modbus_client import ModbusClient
from app.mqtt_client import MqttClient
from app.configuration import Configuration

SLAVE=0x01

BROKER_HOST = os.getenv('BROKER_HOST')
BROKER_PORT = int(os.getenv('BROKER_PORT'))
MODBUS_HOST = os.getenv('MODBUS_HOST')
MODBUS_PORT = int(os.getenv('MODBUS_PORT'))
COMMANDS_TOPIC = os.getenv('COMMANDS_TOPIC')
CONFIGURATION_PATH = os.getenv('CONFIGURATION_PATH', "config/example_configuration.yaml")

def main():
    configuration = Configuration.from_file(CONFIGURATION_PATH)
    modbus_client = ModbusClient(configuration, MODBUS_HOST, MODBUS_PORT)
    mqtt_client = MqttClient(BROKER_HOST, BROKER_PORT)

    mqtt_client.subscribe_topics([COMMANDS_TOPIC])

    def write_to_modbus(marshalled_message):
        message = json.loads(marshalled_message)
        modbus_client.write_coil(message["action"], message["value"])

    mqtt_client.add_message_callback(write_to_modbus)

    mqtt_client.run()



if __name__ == '__main__':
    main()
