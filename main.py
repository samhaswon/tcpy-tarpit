import asyncio
from datetime import datetime
from functools import partial
import os
import signal
import socket
# import time
from threading import Thread
from typing import TYPE_CHECKING, Union


class Server:
    def __init__(self, address: str = "0.0.0.0", port: int = 8080):
        self.__port = port
        self.__address = address

        """
        # Async setup
        if loop is None:
            self.__loop = asyncio.get_event_loop()
        else:
            self.__loop = loop
        """

        if TYPE_CHECKING:
            self.__server_socket: Union[socket.socket, None] = None

    def start(self):
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.bind((self.__address, self.__port))
        self.__server_socket.listen(1024)
        self.__server_socket.setblocking(True)

        log(f'Server started at http://{self.__address}:{self.__port}')

    async def run(self):
        while True:
            client_socket, client_address = self.__server_socket.accept()
            log(f'Connection from {client_address}')

            # Handle the request in a separate function
            try:
                child = Thread(target=self.handle_request, args=[client_socket])
                child.start()
            except Exception as e:
                print("Threading error:\n\n", e)

    def handle_request(self, client_socket):
        try:
            client_socket.recv(1024)

            # Send HTTP headers
            response_headers = (
                'HTTP/1.1 200 OK\r\n'
                'Content-Type: application/x-binary\r\n'
                'Transfer-Encoding: chunked\r\n'
                '\r\n'
            )
            client_socket.send(response_headers.encode('utf-8'))

            # Send the response in chunks
            while True:
                chunk = os.urandom(1024 * 128)
                chunk_size = f"{len(chunk):X}\r\n"
                client_socket.send(chunk_size.encode('utf-8') + chunk + b'\r\n')
                # client_socket.send(chunk.encode('utf-8'))
                # client_socket.send(b'\r\n')
        except ConnectionError or ConnectionResetError:
            ...

        # Send the final chunk
        # client_socket.send(b'0\r\n\r\n')

        # Close the connection
        client_socket.close()
        log("Socket closed")

    def stop(self):
        self.__server_socket.close()


def log(message: str) -> None:
    print(f"[{datetime.now().__str__()[:-7]}] {message}")


def exit_handler(exit_event: asyncio.Event, *args):
    if exit_event.is_set():
        log("Received another stop signal. Crashing and burning...")
        exit(1)
    log("Received stop signal. Committing seppuku...")
    exit_event.set()


async def main(main_loop):
    server = Server()
    server.start()
    server_runner = asyncio.run_coroutine_threadsafe(server.run(), loop=main_loop)

    # Exit setup
    exit_event = asyncio.Event()
    signal_handler = partial(exit_handler, exit_event)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    await exit_event.wait()
    server.stop()
    server_runner.cancel()


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
