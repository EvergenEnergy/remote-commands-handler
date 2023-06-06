from pymodbus.payload import BinaryPayloadBuilder
from app.memory_order import MemoryOrder


class PayloadBuilder:
    def set_data_type(self, data_type: str):
        self.data_type = data_type

    def set_value(self, value: any):
        self.value = value

    def set_memory_order(self, memory_order: MemoryOrder):
        self.memory_order = memory_order

    def build(self):
        if self.memory_order is None:
            raise AttributeError("set memory order")

        if self.data_type is None:
            raise AttributeError("set data type")

        if self.value is None:
            raise AttributeError("set value")

        byte_order, word_order = self.memory_order.order()
        res = BinaryPayloadBuilder(None, byte_order, word_order)

        match self.data_type:  # noqa
            case "FLOAT64-IEEE":
                res.add_64bit_float(self.value)
            case "FLOAT32-IEEE" | "FLOAT32":
                res.add_32bit_float(self.value)
            case "FLOAT16-IEEE":
                res.add_16bit_float(self.value)
            case "INT8":
                res.add_8bit_int(self.value)
            case "UINT8":
                res.add_8bit_uint(self.value)
            case "INT16":
                res.add_16bit_int(self.value)
            case "UINT16":
                res.add_16bit_uint(self.value)
            case "INT32":
                res.add_32bit_int(self.value)
            case "UINT32":
                res.add_32bit_uint(self.value)
            case "INT64":
                res.add_64bit_int(self.value)
            case "UINT64":
                res.add_64bit_uint(self.value)
            case "STRING":
                res.add_string(self.value)
            case _:
                raise RuntimeError(f"unknown data type {self.data_type}")

        return res.to_registers()
