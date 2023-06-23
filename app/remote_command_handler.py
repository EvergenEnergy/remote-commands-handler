from app.configuration import Configuration, MqttSettings, ModbusSettings
import argparse


class RemoteCommandHandler:
    @classmethod
    def parse_arguments(cls, args: list[str]) -> argparse.Namespace:
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

        return parser.parse_args(args)

    def get_configuration_with_overrides(self, args: argparse.Namespace):
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
