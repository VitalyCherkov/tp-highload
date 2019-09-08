import typing
import socket
import datetime
import urllib.parse
from http import status


class HTTPRequest:
    __slots__ = [
        '__raw',
        '__ok',
        '__method',
        '__uri',
        '__version',
        '__headers',
    ]

    def __init__(self):
        self.__ok = False

        self.__method = None
        self.__uri = None
        self.__version = None
        self.__headers = {}

        self.__raw = ''

    def receive(self, conn: socket.socket, chunk_size=1024):
        chunks: bytes = b''

        while True:
            chunk = conn.recv(chunk_size)
            if not chunk:
                break

            search_pos = max(len(chunks) - 1, 0)
            chunks = b''.join([chunks, chunk])

            if chunks.find(b'\r\n\r\n', search_pos) >= 0:
                break

        self.__raw = chunks.decode('utf-8')
        self._parse()

    def _parse(self):
        if not self.is_finished:
            return

        try:
            # do not process body
            [headers, *_] = self.__raw.split('\r\n\r\n')
            [first_line, *header_lines] = headers.split('\r\n')

            self._process_first_line(first_line)
            self._parse_header_lines(header_lines)
            self.__ok = True
        except Exception:
            pass

    def _process_first_line(self, first_line: str):
        [method, uri, version] = first_line.split(' ')
        self.__method = method
        self.__uri = urllib.parse.unquote(uri)
        self.__version = version

    def _parse_header_lines(self, header_lines: typing.List[str]):
        for line in header_lines:
            [key, val] = line.split(': ')
            self.__headers[key] = val

    def get_header(self, header: str) -> typing.Union[str, None]:
        if header in self.__headers:
            return self.__headers[header]

        return None

    @property
    def is_finished(self):
        return self.__raw.find('\r\n\r\n') >= 0

    @property
    def raw(self) -> str:
        return self.__raw

    @property
    def ok(self) -> bool:
        return self.__ok

    @property
    def method(self) -> str:
        return self.__method

    @property
    def uri(self) -> str:
        return self.__uri

    @property
    def version(self) -> str:
        return self.__version


class HTTPResponse:
    __slots__ = [
        '__version',
        '__status',
        '__headers',
    ]

    def __init__(self):
        self.__version = 'HTTP/1.1'
        self.__status = status.OK
        self.__headers = {
            'Connection': 'close',
            'Server': 'Vitaly Server',
            'Date': datetime.datetime.now()
        }

    def set_version(self, version: str):
        self.__version = version

    def set_status(self, http_status: int):
        self.__status = http_status

    def set_header(self, header: str, value: typing.Union[str, int]):
        self.__headers[header] = value

    def to_bytes(self) -> bytes:
        st = status.codes[self.__status]
        first_line = f'{self.__version} {st}'
        lines: typing.List[str] = [first_line]

        for header in self.__headers:
            line = f'{header}: {self.__headers[header]}'
            lines.append(line)

        lines.append('\r\n')
        return '\r\n'.join(lines).encode()
