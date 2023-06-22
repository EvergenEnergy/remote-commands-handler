"""Remote Commands Handler.

This module provides a remote commands handler that listens to MQTT messages and writes
the received data to Modbus coils and holding registers based on the specified configuration.

The remote commands handler connects to an MQTT broker and a Modbus server, and subscribes
to a specific MQTT topic for receiving commands. It retrieves the configuration from a YAML
file and allows overriding certain configuration parameters through command-line arguments.

Example:
    Run the remote commands handler:

    ```
    python remote_commands_handler.py --configuration_path config/configuration.yaml
    ```

Note:
    This module requires the `paho-mqtt` and `pymodbus` packages to be installed.

"""

import logging
import os

import argparse
import signal
import sys
import paho.mqtt.client as mqtt
from pymodbus.client import ModbusTcpClient

from app.error_handler import ErrorHandler
from app.modbus_client import ModbusClient
from app.mqtt_reader import MqttReader
from app.configuration import Configuration, ModbusSettings, MqttSettings
from app.exceptions import (
    ConfigurationFileNotFoundError,
    ConfigurationFileInvalidError,
)


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
        "--mqtt_command_topic",
        help="The MQTT topic to subscribe to. Expected to be a string.",
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
        args_as_dict.get("mqtt_command_topic") or mqtt_settings.command_topic,
        mqtt_settings.error_topic,
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
        configuration.get_site_settings(),
    )


def setup_error_handler(configuration: Configuration) -> ErrorHandler:
    return ErrorHandler.from_config(configuration, mqtt.Client())


def setup_modbus_client(
    configuration: Configuration, error_handler: ErrorHandler
) -> ModbusClient:
    return ModbusClient(
        configuration,
        ModbusTcpClient(
            configuration.get_modbus_settings().host,
            port=configuration.get_modbus_settings().port,
        ),
        error_handler,
    )


def setup_mqtt_client(
    configuration: Configuration, error_handler: ErrorHandler
) -> MqttReader:
    return MqttReader(
        configuration.get_mqtt_settings().host,
        configuration.get_mqtt_settings().port,
        [configuration.mqtt_settings.command_topic],
        mqtt.Client(),
        error_handler,
    )


def main():
    loglevel = os.getenv("LOGLEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, loglevel),
        format="%(asctime)s:%(levelname)s:%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    args = handle_args()

    try:
        configuration = get_configuration_with_overrides(args)
    except (ConfigurationFileNotFoundError, ConfigurationFileInvalidError) as ex:
        logging.info(ex)
        logging.error("Error retrieving configuration, exiting")
        sys.exit(1)

    logging.info(
        f"Starting service at {configuration.get_site_settings().site_name}"
        f"/{configuration.get_site_settings().serial_number}"
    )
    error_handler = setup_error_handler(configuration)
    modbus_client = setup_modbus_client(configuration, error_handler)
    mqtt_reader = setup_mqtt_client(configuration, error_handler)

    def write_to_modbus(message):
        try:
            modbus_client.write_command(message["action"], message["value"])
        except Exception as e:
            logging.error(f"Error writing to modbus: {e}")

    mqtt_reader.add_message_callback(write_to_modbus)

    def signal_handler(signum, _):
        logging.info(f"Received signal {signum}, shutting down...")
        mqtt_reader.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    mqtt_reader.run()


if __name__ == "__main__":
    main()
