import os
import json

import argparse

import paho.mqtt.client as mqtt
from pymodbus.client import ModbusTcpClient

from app.modbus_client import ModbusClient
from app.mqtt_client import MqttClient
from app.configuration import Configuration, ModbusSettings, MqttSettings


def handle_args():
    # Create the argument parser
    parser = argparse.ArgumentParser(
        description="remote commands handler",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Add the optional arguments
    parser.add_argument(
        "--configuration_path",
        help='Path to the configuration file. By default, this is "config/configuration.yaml".',
        default="config/configuration.yaml",
    )
    parser.add_argument(
        "--modbus_port",
        type=int,
        help="The port number for the Modbus server. Expected to be an integer.",
    )
    parser.add_argument(
        "--modbus_host",
        help="The host address for the Modbus server. Expected to be a string.",
    )
    parser.add_argument(
        "--mqtt_port",
        type=int,
        help="The port number for the MQTT server. Expected to be an integer.",
    )
    parser.add_argument(
        "--mqtt_host",
        help="The host address for the MQTT server. Expected to be a string.",
    )
    parser.add_argument(
        "--mqtt_topic", help="The MQTT topic to subscribe to. Expected to be a string."
    )

    return parser.parse_args()


def get_configuration_with_overrides(args):
    args_as_dict = vars(args)
    configuration = Configuration.from_file(args.configuration_path)

    mqtt_settings = configuration.get_mqtt_settings()
    modbus_settings = configuration.get_modbus_settings()

    mqtt_settings_with_override = MqttSettings(
        args_as_dict.get("mqtt_host") or mqtt_settings.host,
        args_as_dict.get("mqtt_port") or mqtt_settings.port,
        args_as_dict.get("mqtt_topic") or mqtt_settings.command_topic,
    )

    modbus_settings_with_override = ModbusSettings(
        args_as_dict.get("modbus_host") or modbus_settings.host,
        args_as_dict.get("modbus_port") or modbus_settings.port,
    )

    return Configuration(
        configuration.get_coils(),
        configuration.get_holding_registers(),
        mqtt_settings_with_override,
        modbus_settings_with_override,
    )


def setup_modbus_client(configuration: Configuration) -> ModbusClient:
    return ModbusClient(
        configuration,
        ModbusTcpClient(
            configuration.get_modbus_settings().host,
            port=configuration.get_modbus_settings().port,
        ),
    )


def setup_mqtt_client(configuration: Configuration) -> MqttClient:
    return MqttClient(
        configuration.get_mqtt_settings().port,
        configuration.get_mqtt_settings().host,
        mqtt.Client(),
    )


def main():
    args = handle_args()

    configuration = get_configuration_with_overrides(args)

    modbus_client = setup_modbus_client(configuration)
    mqtt_client = setup_mqtt_client(configuration)

    mqtt_client.subscribe_topics([configuration.mqtt_settings.command_topic])

    def write_to_modbus(marshalled_message):
        message = json.loads(marshalled_message)
        modbus_client.write_coil(message["action"], message["value"])

    mqtt_client.add_message_callback(write_to_modbus)

    mqtt_client.run()


if __name__ == "__main__":
    main()
