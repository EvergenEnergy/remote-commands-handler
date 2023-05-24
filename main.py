import os
import json

from app.modbus_client import ModbusClient
from app.mqtt_client import MqttClient
from app.configuration import Configuration

SLAVE=0x01

CONFIGURATION_PATH = os.getenv('CONFIGURATION_PATH', "config/example_configuration.yaml")

def main():
    configuration = Configuration.from_file(CONFIGURATION_PATH)
    mqtt_settings = configuration.mqtt_settings
    modbus_settings = configuration.modbus_settings

    modbus_client = ModbusClient(configuration, mqtt_settings.host, mqtt_settings.port)
    mqtt_client = MqttClient(modbus_settings.host, modbus_settings.port)

    mqtt_client.subscribe_topics([mqtt_settings.command_topic])

    def write_to_modbus(marshalled_message):
        message = json.loads(marshalled_message)
        modbus_client.write_coil(message["action"], message["value"])

    mqtt_client.add_message_callback(write_to_modbus)

    mqtt_client.run()



if __name__ == '__main__':
    main()
