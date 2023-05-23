import socket
import threading
from multiprocessing import Pipe

from app.modbus_client import ModbusClient
from app.configuration import Coil, Configuration, HoldingRegister

def test_write_coil():
    coils = [
        Coil("test_coil", 1)
    ]
    holding_registers = []
    configuration = Configuration(coils, holding_registers)

    read, write = Pipe(duplex=False)

    def test(_message):
        write.send(True)
    thread, port = start_local_tcp_client(test)

    client = ModbusClient(configuration, port, "localhost")
    client.write_coil("test_coil", True)

    sent = read.recv()
    thread.join()
    assert sent is True

def test_write_coils():
    coils = [
        Coil("test_coil", 1)
    ]
    holding_registers = []
    configuration = Configuration(coils, holding_registers)

    read, write = Pipe(duplex=False)

    def test(_message):
        write.send(True)
    thread, port = start_local_tcp_client(test)

    client = ModbusClient(configuration, port, "localhost")
    client.write_coils("test_coil", [True, True])

    sent = read.recv()
    thread.join()
    assert sent is True

def test_write_holding_registers():
    coils = []
    holding_registers = [
        HoldingRegister(
            "test_register",
            "AB",
            "INT16",
            1.0,
            1
        )
    ]
    configuration = Configuration(coils, holding_registers)

    read, write = Pipe(duplex=False)

    def test(_message):
        print(_message)
        write.send(True)
    thread, port = start_local_tcp_client(test)

    client = ModbusClient(configuration, port, "localhost")
    client.write_register("test_register", 10)

    sent = read.recv()
    thread.join()
    assert sent is True

def start_local_tcp_client(f):
    read, write = Pipe(duplex=False)
    tcp_thread = threading.Thread(target=setup_tcp_client, args=(f, write))
    tcp_thread.start()
    port = read.recv()
    return tcp_thread, port

def handle_socket_message(client_socket: socket.socket, call_back):
   message = client_socket.recv(40) 
   client_socket.send(message)
   call_back(message)

def setup_tcp_client(f, chan) -> threading.Thread:
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
    client_thread = threading.Thread(target=handle_socket_message, args=(client_socket, f))
    client_thread.start()
    return port

