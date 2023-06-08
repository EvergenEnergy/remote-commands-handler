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


@dataclass
class ModbusSettings:
    host: str
    port: int


class Configuration:
    def __init__(
        self,
        coils: list[Coil],
        holding_registers: list[HoldingRegister],
        mqtt_settings: MqttSettings,
        modbus_settings: ModbusSettings,
    ):
        self.coils_map = {x.name: x for x in coils}
        self.holding_register_map = {x.name: x for x in holding_registers}
        self.mqtt_settings = mqtt_settings
        self.modbus_settings = modbus_settings

    @classmethod
    def from_file(cls, path: str):
        if not os.path.exists(path):
            raise ConfigurationFileNotFoundError(path)

        try:
            yaml_data = path_to_yaml_data(path)
        except yaml.YAMLError as exc:
            msg = "Error parsing YAML file"
            if hasattr(exc, "problem_mark"):
                msg = f"Error encountered parsing YAML {str(exc.problem_mark)}"
            raise ConfigurationFileInvalidError(msg)

        _validate_config(yaml_data)

        coils = _coils_data_from_yaml_data(yaml_data)
        holding_registers = _holding_register_from_yaml_data(yaml_data)
        mqtt_settings = _mqtt_settings_from_yaml_data(yaml_data)
        modbus_settings = _modbus_settings_from_yaml_data(yaml_data)
        return cls(coils, holding_registers, mqtt_settings, modbus_settings)

    def get_coil(self, name: str) -> Coil:
        return self.coils_map[name]

    def get_coils(self) -> list[Coil]:
        return list(self.coils_map.values())

    def get_holding_registers(self) -> list[Coil]:
        return list(self.holding_register_map.values())

    def get_holding_register(self, name: str) -> HoldingRegister:
        return self.holding_register_map[name]

    def get_mqtt_settings(self) -> MqttSettings:
        return self.mqtt_settings

    def get_modbus_settings(self) -> ModbusSettings:
        return ModbusSettings(self.modbus_settings.host, self.modbus_settings.port)


def path_to_yaml_data(path):
    with open(path, "r", encoding="UTF8") as file:
        return yaml.safe_load(file)


def _modbus_settings_from_yaml_data(data) -> ModbusSettings:
    modbus_settings = data["modbus_settings"]
    return ModbusSettings(modbus_settings["host"], modbus_settings["port"])


def _mqtt_settings_from_yaml_data(data) -> MqttSettings:
    mqtt_settings = data["mqtt_settings"]
    return MqttSettings(
        mqtt_settings["host"], mqtt_settings["port"], mqtt_settings["command_topic"]
    )


def _coils_data_from_yaml_data(data):
    modbus_mapping = data.get("modbus_mapping", {})
    coils = [
        Coil(coil["name"], coil["address"]) for coil in modbus_mapping.get("coils", [])
    ]

    return coils


def _holding_register_from_yaml_data(data):
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
        "mqtt_settings": ["host", "port", "command_topic"],
        "modbus_settings": ["host", "port"],
        "modbus_mapping": [],
    }
    try:
        for req_key, req_items in required_settings.items():
            assert (
                req_key in config
            ), f"No {req_key!r} section provided in configuration"
            for item in req_items:
                assert (
                    item in config[req_key]
                ), f"No {item!r} provided in {req_key!r} section of configuration"

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
    except AssertionError as ex:
        raise ConfigurationFileInvalidError(ex)
