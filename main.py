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

import signal
import sys
import paho.mqtt.client as mqtt
from pymodbus.client import ModbusTcpClient

from app.error_handler import ErrorHandler
from app.modbus_client import ModbusClient
from app.mqtt_reader import MqttReader
from app.configuration import Configuration
from app.exceptions import (
    ConfigurationFileNotFoundError,
    ConfigurationFileInvalidError,
)
from app.remote_command_handler import RemoteCommandHandler


def setup_error_handler(configuration: Configuration) -> ErrorHandler:
    return ErrorHandler(configuration, mqtt.Client(mqtt.CallbackAPIVersion.VERSION2))


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
        configuration,
        mqtt.Client(mqtt.CallbackAPIVersion.VERSION2),
        error_handler,
    )


def main():
    loglevel = os.getenv("LOGLEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, loglevel),
        format="%(asctime)s:%(levelname)s:%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = RemoteCommandHandler()
    args = handler.parse_arguments(sys.argv[1:])

    try:
        configuration = handler.get_configuration_with_overrides(args)
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
        modbus_client.write_command(message)

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
