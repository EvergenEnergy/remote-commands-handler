from dataclasses import dataclass
import yaml

@dataclass
class Coil:
    name: str
    address: list[int]

@dataclass
class HoldingRegister:
    name: str
    byte_order: str
    data_type: str
    scale: float
    address: list[int]

@dataclass
class MqttSettings:
    host: str
    port: int

class Configuration:

    def __init__(
            self, 
            coils: list[Coil],
            holding_registers: list[HoldingRegister], 
            mqtt_settings: MqttSettings,
            ):
        self.coils_map = { x.name: x for x in coils }
        self.holding_register_map = { x.name: x for x in holding_registers }
        self.mqtt_settings = mqtt_settings

    @classmethod
    def from_file(cls, path: str):
        yaml_data = path_to_yaml_data(path)
        coils, holding_registers = _coils_data_from_yaml_data(yaml_data)
        mqtt_settings = _mqtt_settings_from_yaml_data(yaml_data)
        return cls(coils, holding_registers, mqtt_settings)
    
    def get_coil(self, name: str) -> Coil:
        return self.coils_map[name]
    
    def get_holding_register(self, name: str) -> HoldingRegister:
        return self.holding_register_map[name]
    
    def get_mqtt_settings(self) -> MqttSettings:
        return self.mqtt_settings

def path_to_yaml_data(path):
    with open(path, "r", encoding="UTF8") as file:
        return yaml.safe_load(file)

def _mqtt_settings_from_yaml_data(data) -> MqttSettings:
        mqtt_settings = data["mqtt_settings"]
        return MqttSettings(mqtt_settings["host"], mqtt_settings["port"])

def _coils_data_from_yaml_data(data):
    modbus_mapping = data.get("modbus_mapping", {})
    coils = [Coil(coil["name"], coil["address"]) for coil in modbus_mapping.get("coils", [])]
    holding_registers = [
        HoldingRegister(register["name"], register["byte_order"], register["data_type"], register["scale"], register["address"]) 
        for register in modbus_mapping.get("holding_registers", [])
    ]
        
    return coils,holding_registers
