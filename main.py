import os
import json

from app.modbus_client import ModbusClient
from app.mqtt_client import MqttClient
from app.configuration import Configuration

import argparse

SLAVE=0x01

def handle_args():
    # Create the argument parser
    parser = argparse.ArgumentParser(description='remote commands handler')

    # Add the optional arguments
    parser.add_argument('--configuration_path', required=True, help='Configuration path')
    parser.add_argument('--modbus_port', type=int, help='Modbus port')
    parser.add_argument('--modbus_host', help='Modbus host')
    parser.add_argument('--mqtt_port', type=int, help='MQTT port')
    parser.add_argument('--mqtt_host', help='MQTT host')

    return parser.parse_args()

def setup_modbus_client(configuration: Configuration, args) -> ModbusClient:
    modbus_settings = configuration.modbus_settings
    modbus_host = args.modbus_host if args.modbus_host else modbus_settings.host 
    modbus_port = args.modbus_port if args.modbus_port else modbus_settings.port 
    return ModbusClient(configuration, modbus_host, modbus_port)

def setup_mqtt_client(mqtt_settings, args) -> MqttClient:
    mqtt_host = args.mqtt_host if args.mqtt_host else mqtt_settings.host 
    mqtt_port = args.mqtt_port if args.mqtt_port else mqtt_settings.port 
    return MqttClient(mqtt_host, mqtt_port)


def main():
    args = handle_args()

    configuration = Configuration.from_file(args.configuration_path)
    modbus_client = setup_modbus_client(configuration, args)

    mqtt_settings = configuration.mqtt_settings
    mqtt_client = setup_mqtt_client(mqtt_settings, args)

    mqtt_client.subscribe_topics([mqtt_settings.command_topic])

    def write_to_modbus(marshalled_message):
        message = json.loads(marshalled_message)
        modbus_client.write_coil(message["action"], message["value"])

    mqtt_client.add_message_callback(write_to_modbus)

    mqtt_client.run()



if __name__ == '__main__':
    main()
