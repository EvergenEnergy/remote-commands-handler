"""Configuration Module.

This module provides classes and functions for managing configuration data in the application.
It defines data classes for coils, holding registers, MQTT settings, and Modbus settings.
The `Configuration` class represents the overall configuration, which can be loaded from a YAML file.

Example:
    Load a configuration from a YAML file:

    ```
    configuration = Configuration.from_file("config.yaml")
    coil = configuration.get_coil("coil_name")
    holding_registers = configuration.get_holding_registers()
    mqtt_settings = configuration.get_mqtt_settings()
    modbus_settings = configuration.get_modbus_settings()
    ```

Note:
    This module requires the `pyyaml` package to be installed.

"""

import os
import logging
from dataclasses import dataclass
import yaml
from app.memory_order import MemoryOrder


from app.exceptions import ConfigurationFileNotFoundError, ConfigurationFileInvalidError


@dataclass
class Coil:
    name: str
    address: list[int]


@dataclass
class HoldingRegister:
    name: str
    memory_order: MemoryOrder
    data_type: str
    scale: float
    address: list[int]


@dataclass
class MqttSettings:
    host: str
    port: int
    command_topic: str
    error_topic: str = None
    pub_errors: bool = False

    def __post_init__(self):
        self.pub_errors = self.error_topic is not None and len(self.error_topic) > 0


@dataclass
class ModbusSettings:
    host: str
    port: int


@dataclass
class SiteSettings:
    site_name: str
    serial_number: int


class Configuration:
    def __init__(
        self,
        coils: list[Coil],
        holding_registers: list[HoldingRegister],
        mqtt_settings: MqttSettings,
        modbus_settings: ModbusSettings,
        site_settings: SiteSettings,
    ):
        self.coils_map = {x.name: x for x in coils}
        self.holding_register_map = {x.name: x for x in holding_registers}
        self.mqtt_settings = mqtt_settings
        self.modbus_settings = modbus_settings
        self.site_settings = site_settings

    @classmethod
    def from_file(cls, path: str):
        if not os.path.exists(path):
            raise ConfigurationFileNotFoundError(path)

        try:
            yaml_data = path_to_yaml_data(path)
            yaml_data["site_settings"] = interpolate_environment_vars(
                yaml_data["site_settings"]
            )
        except yaml.YAMLError as exc:
            msg = "Error parsing YAML file"
            if hasattr(exc, "problem_mark"):
                msg = f"Error encountered parsing YAML {str(exc.problem_mark)}"
            raise ConfigurationFileInvalidError(msg)
        except ConfigurationFileInvalidError as ex:
            raise ex

        try:
            _validate_config(yaml_data)

            coils = _coils_data_from_yaml_data(yaml_data)
            holding_registers = _holding_register_from_yaml_data(yaml_data)
            mqtt_settings = _mqtt_settings_from_yaml_data(yaml_data)
            modbus_settings = _modbus_settings_from_yaml_data(yaml_data)
            site_settings = _site_settings_from_yaml_data(yaml_data)
            return cls(
                coils, holding_registers, mqtt_settings, modbus_settings, site_settings
            )
        except TypeError as ex:
            raise ConfigurationFileInvalidError(
                f"Error parsing configuration YAML: {ex}"
            )
        except KeyError as ex:
            raise ConfigurationFileInvalidError(
                f"Error parsing configuration YAML: expected key {ex} was not found"
            )

    def get_coil(self, name: str) -> Coil:
        return self.coils_map.get(name)

    def get_coils(self) -> list[Coil]:
        return list(self.coils_map.values())

    def get_holding_registers(self) -> list[Coil]:
        return list(self.holding_register_map.values())

    def get_holding_register(self, name: str) -> HoldingRegister:
        return self.holding_register_map.get(name)

    def get_mqtt_settings(self) -> MqttSettings:
        return self.mqtt_settings

    def get_modbus_settings(self) -> ModbusSettings:
        return ModbusSettings(self.modbus_settings.host, self.modbus_settings.port)

    def get_site_settings(self) -> SiteSettings:
        return SiteSettings(
            self.site_settings.site_name, self.site_settings.serial_number
        )


def path_to_yaml_data(path: str):
    with open(path, "r", encoding="UTF8") as file:
        return yaml.safe_load(file)


def interpolate_environment_vars(data: dict):
    interpolated = {}
    for key, value in data.items():
        var_name = value
        if value.startswith("$"):
            var_name = value[1:]
            if value == f"${key.upper()}":
                value = os.getenv(var_name, "")
                logging.debug(f"Found value {value!r} in env var {var_name}")
            else:
                raise ConfigurationFileInvalidError(
                    f"Value for {key!r} ({value!r}) looks like an environment variable but has an invalid name."
                )
        if not value:
            raise ConfigurationFileInvalidError(
                f"Missing value for expected environment variable {var_name!r}"
            )
        interpolated[key] = value
    return interpolated


def _site_settings_from_yaml_data(data: dict) -> SiteSettings:
    site_settings = data["site_settings"]
    return SiteSettings(site_settings["site_name"], site_settings["serial_number"])


def _modbus_settings_from_yaml_data(data: dict) -> ModbusSettings:
    modbus_settings = data["modbus_settings"]
    return ModbusSettings(modbus_settings["host"], modbus_settings["port"])


def _mqtt_settings_from_yaml_data(data: dict) -> MqttSettings:
    mqtt_settings = data["mqtt_settings"]
    return MqttSettings(
        mqtt_settings["host"],
        mqtt_settings["port"],
        mqtt_settings["command_topic"],
        mqtt_settings.get("error_topic"),
    )


def _coils_data_from_yaml_data(data: dict):
    modbus_mapping = data.get("modbus_mapping", {})
    coils = [
        Coil(coil["name"], coil["address"]) for coil in modbus_mapping.get("coils", [])
    ]

    return coils


def _holding_register_from_yaml_data(data: dict):
    modbus_mapping = data.get("modbus_mapping", {})

    holding_registers = []
    for register in modbus_mapping.get("holding_registers", []):
        memory_order = MemoryOrder(register["byte_order"])
        register = HoldingRegister(
            register["name"],
            memory_order,
            register["data_type"],
            register.get("scale", 1.0),
            register["address"],
        )
        holding_registers.append(register)

    return holding_registers


def _validate_config(config: dict):
    required_settings = {
        "site_settings": ["site_name", "serial_number"],
        "mqtt_settings": ["host", "port", "command_topic"],
        "modbus_settings": ["host", "port"],
        "modbus_mapping": [],
    }
    try:
        for req_key, req_items in required_settings.items():
            assert req_key in config and isinstance(
                config[req_key], dict
            ), f"No {req_key!r} section provided in configuration"
            for item in req_items:
                assert (
                    item in config[req_key] and config[req_key][item]
                ), f"No {item!r} provided in {req_key!r} section of configuration"

        def _is_valid_mqtt_topic(topic):
            # Command topic must be str, must not have more than 7 levels
            return isinstance(topic, str) and topic.count("/") <= 7

        assert _is_valid_mqtt_topic(
            config["mqtt_settings"]["command_topic"]
        ), "The command topic must be a valid MQTT topic name"

        error_topic = config["mqtt_settings"].get("error_topic")
        if error_topic:
            assert _is_valid_mqtt_topic(
                error_topic
            ), "The error topic must be a valid MQTT topic name"

            assert (
                error_topic.count("#") + error_topic.count("+") == 0
            ), "The error topic must not contain a wildcard character"

        mapping = config["modbus_mapping"]
        keys_defined = sum(
            [len(mapping.get(k, [])) for k in ("holding_registers", "coils")]
        )
        assert keys_defined > 0, "No keys defined in holding_registers or coils"

        section_keys = ["name", "address"]
        for index, ref in enumerate(mapping.get("coils", [])):
            for key in section_keys:
                assert (
                    key in ref
                ), f"Coil reference #{index} has no config setting for {key!r}"

        section_keys.extend(["byte_order", "data_type"])
        for index, ref in enumerate(mapping.get("holding_registers", [])):
            for key in section_keys:
                assert (
                    key in ref
                ), f"Holding register reference #{index} has no config setting for {key!r}"
    except (AssertionError, TypeError, ValueError) as ex:
        raise ConfigurationFileInvalidError(ex)
