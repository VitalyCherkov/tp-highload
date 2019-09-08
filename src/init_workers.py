import socket
import typing
from multiprocessing import Process, Queue
from threading import Thread

from config import Config


def _run_worker(sock: socket.socket, config: Config, worker):
    while True:
        conn, addr = sock.accept()
        try:
            worker(conn, config)
        except Exception as e:
            print('exception while reading', e)
        finally:
            conn.close()


def _init_threads(sock: socket.socket, config: Config, worker):
    thread_pool: typing.List[Thread] = []

    for index in range(config.thread_count):
        thread = Thread(target=_run_worker, args=(sock, config, worker,))
        thread.start()

    for thread in thread_pool:
        print('Join thread')
        thread.join()


def do(sock: socket.socket, config: Config, worker):
    process_pool: typing.List[Process] = []

    for index in range(config.cpu_limit):
        process = Process(target=_init_threads, args=(sock, config, worker,))
        process.start()
        process_pool.append(process)

    try:
        for process in process_pool:
            process.join()

    except KeyboardInterrupt:
        for process in process_pool:
            process.terminate()
            print('Terminate')
