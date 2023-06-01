import unittest
import socket
import threading
from multiprocessing import Pipe

from pymodbus.client import ModbusTcpClient
from app.memory_order import MemoryOrder

from app.modbus_client import ModbusClient
from app.configuration import (
    Coil,
    Configuration,
    HoldingRegister,
    ModbusSettings,
    MqttSettings,
)


class TestModbusClient(unittest.TestCase):
    def setUp(self):
        # This method will be called before every test
        self.coils = [Coil("test_coil", [1])]
        self.holding_registers = [
            HoldingRegister("test_register", MemoryOrder("AB"), "INT16", 1.0, [1]),
            HoldingRegister(
                "float_register", MemoryOrder("BA"), "FLOAT32-IEEE", 1.0, [1]
            ),
        ]
        self.mqtt_settings = MqttSettings("test", 100, "test")

    def start_local_tcp_client(self, f):
        read, write = Pipe(duplex=False)
        tcp_thread = threading.Thread(target=self.setup_tcp_client, args=(f, write))
        tcp_thread.start()
        port = read.recv()
        return tcp_thread, port

    def handle_socket_message(self, client_socket: socket.socket, call_back):
        message = client_socket.recv(40)
        client_socket.send(message)
        call_back(message)

    def setup_tcp_client(self, f, chan) -> threading.Thread:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = "localhost"
        port = 8080
        while True:
            try:
                # Attempt to bind the socket to the host and port
                server_socket.bind((host, port))
                break
            except socket.error:
                port += 1
        chan.send(port)
        # Listen for incoming connections
        server_socket.listen()
        # Accept a client connection
        client_socket, _ = server_socket.accept()
        # Create a new thread to handle the client connection
        client_thread = threading.Thread(
            target=self.handle_socket_message, args=(client_socket, f)
        )
        client_thread.start()
        return port

    def test_write_coil(self):
        read, write = Pipe(duplex=False)

        def test(_message):
            write.send(True)

        thread, port = self.start_local_tcp_client(test)
        modbus_settings = ModbusSettings("localhost", port)
        configuration = Configuration(
            self.coils, [], self.mqtt_settings, modbus_settings
        )
        client = ModbusClient(configuration, ModbusTcpClient("localhost", port=port))
        client.write_coil("test_coil", True)
        sent = read.recv()
        thread.join()
        self.assertTrue(sent)

    def test_write_coils(self):
        read, write = Pipe(duplex=False)

        def test(_message):
            write.send(True)

        thread, port = self.start_local_tcp_client(test)
        modbus_settings = ModbusSettings("localhost", port)
        configuration = Configuration(
            self.coils, [], self.mqtt_settings, modbus_settings
        )
        client = ModbusClient(configuration, ModbusTcpClient("localhost", port=port))
        client.write_coils("test_coil", [True, True])
        sent = read.recv()
        thread.join()
        self.assertTrue(sent)

    def test_write_int_to_holding_registers(self):
        read, write = Pipe(duplex=False)

        def test(_message):
            write.send(True)

        thread, port = self.start_local_tcp_client(test)
        modbus_settings = ModbusSettings("localhost", port)
        configuration = Configuration(
            [], self.holding_registers, self.mqtt_settings, modbus_settings
        )
        client = ModbusClient(configuration, ModbusTcpClient("localhost", port=port))
        client.write_register("test_register", 10)
        sent = read.recv()
        thread.join()
        self.assertTrue(sent)

    def test_write_float_to_holding_registers(self):
        read, write = Pipe(duplex=False)

        def test(_message):
            print(_message)
            write.send(True)

        thread, port = self.start_local_tcp_client(test)
        modbus_settings = ModbusSettings("localhost", port)
        configuration = Configuration(
            [], self.holding_registers, self.mqtt_settings, modbus_settings
        )
        client = ModbusClient(configuration, ModbusTcpClient("localhost", port=port))
        client.write_register("float_register", 32.3)
        sent = read.recv()
        thread.join()
        self.assertTrue(sent)


if __name__ == "__main__":
    unittest.main()
