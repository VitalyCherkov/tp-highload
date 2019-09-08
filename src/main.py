import sys
import socket

from config import Config
import init_workers
import handle_http_request


DEFAULT_CONFIG_FILE = '/etc/httpd.conf'


def main():
    # 1й аргумент — расположение файла конфига
    config_file = DEFAULT_CONFIG_FILE if len(sys.argv) < 2 else sys.argv[1]

    config = Config(config_file)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((config.host, config.port))
        sock.listen(config.queue_size)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        init_workers.do(sock, config, handle_http_request.do)


if __name__ == '__main__':
    main()
