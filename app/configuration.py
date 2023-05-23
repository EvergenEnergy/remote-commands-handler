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

class Configuration:

    def __init__(self, coils: list[Coil], holding_registers: list[HoldingRegister]):
        self.coils_map = { x.name: x for x in coils }
        self.holding_register_map = { x.name: x for x in holding_registers }

    @classmethod
    def from_file(cls, path: str):
        coils, holding_registers = _coils_registers_from_file(path)
        return cls(coils, holding_registers)
    
    def get_coil(self, name: str) -> Coil:
        return self.coils_map[name]
    
    def get_holding_register(self, name: str) -> HoldingRegister:
        return self.holding_register_map[name]
    
def _coils_registers_from_file(path):
    with open(path, "r", encoding="UTF8") as file:
        data = yaml.safe_load(file)
        modbus_mapping = data.get("modbus_mapping", {})
        coils = [Coil(coil["name"], coil["address"]) for coil in modbus_mapping.get("coils", [])]
        holding_registers = [
            HoldingRegister(register["name"], register["byte_order"], register["data_type"], register["scale"], register["address"]) 
            for register in modbus_mapping.get("holding_registers", [])
        ]
        
    return coils,holding_registers
