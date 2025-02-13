import asyncio
from datetime import datetime, timedelta
from functools import partial
import os
import signal
import socket
import time
from threading import Thread
from typing import TYPE_CHECKING, Union, List


CRASH_AND_BURN = False


class Server:
    def __init__(self, address: str = "0.0.0.0", port: int = 8080):
        self.__port = port
        self.__address = address

        self.__threads: List[Thread] = []

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
                child = Thread(target=self.handle_request, args=[client_socket, client_address])
                child.start()
                self.__threads.append(child)
            except Exception as e:
                print("Threading error:\n\n", e)

            # Prune dead threads
            self.__threads = [t for t in self.__threads if t.is_alive()]

    def handle_request(self, client_socket, client_address) -> None:
        """
        Handles a client request.
        :param client_socket: The received socket from the client.
        :param client_address: The address information of the client.
        :return: None.
        """
        global CRASH_AND_BURN
        start = time.perf_counter()
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
                if CRASH_AND_BURN:
                    client_socket.close()
                    return
                chunk = os.urandom(1024 * 128)
                chunk_size = f"{len(chunk):X}\r\n"
                client_socket.send(chunk_size.encode('utf-8') + chunk + b'\r\n')
                # client_socket.send(chunk.encode('utf-8'))
                # client_socket.send(b'\r\n')
        except ConnectionError or ConnectionResetError:
            ...
        finally:
            end = time.perf_counter()

        # Send the final chunk
        # client_socket.send(b'0\r\n\r\n')

        # Close the connection
        client_socket.close()
        log(f"Kept client {client_address} busy for {self.time_format(start, end)}")

    def stop(self):
        log("Stopping...")
        global CRASH_AND_BURN
        CRASH_AND_BURN = True
        for thread in self.__threads:
            thread.join()
        self.__server_socket.close()

    @staticmethod
    def time_format(start: float, end: float) -> str:
        """
        Format the given time difference as days, hours, minutes, and seconds.
        :param start: The start time (float).
        :param end: The end time (float).
        :return: The formatted date string.
        """
        time_diff = timedelta(seconds=(end - start))
        days = time_diff.days
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        seconds = (end - start) % 60

        result = ""
        if days == 1:
            result += "1 day, "
        elif days > 1:
            result += f"{days} days, "

        if hours == 1:
            result += "1 hour, "
        elif hours > 1:
            result += f"{hours} hours, "

        if minutes == 1:
            result += "1 minute, "
        elif minutes > 1:
            result += f"{minutes} minutes, "

        result += f"{seconds:.4f} seconds"
        return result


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
