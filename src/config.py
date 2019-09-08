DEFAULT_CPU_LIMIT = 4
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = '80'
DEFAULT_DOCUMENT_ROOT = '/var/www/html'
DEFAULT_QUEUE_SIZE = 8
DEFAULT_THREAD_COUNT = 64


class Config:
    __slots__ = [
        'cpu_limit',
        'host',
        'port',
        'document_root',
        'queue_size',
        'thread_count',
    ]

    def __init__(self, file_name: str):
        self.cpu_limit = DEFAULT_CPU_LIMIT
        self.host = DEFAULT_HOST
        self.port = DEFAULT_PORT
        self.document_root = DEFAULT_DOCUMENT_ROOT
        self.queue_size = DEFAULT_QUEUE_SIZE
        self.thread_count = DEFAULT_THREAD_COUNT

        self._read(file_name)

    def _read(self, file_name):
        with open(file_name, 'r') as file:
            for line in file.read().splitlines():
                key, value = line.split(' ')
                if hasattr(self, key):
                    if key in ['cpu_limit', 'port', 'thread_count', 'queue_size']:
                        parsed = int(value, 10)
                        setattr(self, key, parsed)
                    else:
                        setattr(self, key, value)

    def __str__(self):
        return 'cpu_limit={}\ndocument_root={}\nhost={}\nport={}\n'.format(
            self.cpu_limit,
            self.document_root,
            self.host,
            self.port,
        )
