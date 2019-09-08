import mimetypes
import socket
import os
from http import builders, methods, status

from config import Config


DEFAULT_FILE = 'index.html'


def check_path(req: builders.HTTPRequest, config: Config):
    [path, *_] = req.uri.split('?')
    is_index = False

    if path.find('../') >= 0:
        return None, status.FORBIDDEN

    if path[0] != '/':
        path = '/' + path

    if path[-1] == '/':
        path = path + DEFAULT_FILE
        is_index = True

    path = config.document_root + path

    if not os.path.exists(path) or not os.path.isfile(path):
        if is_index:

            return None, status.FORBIDDEN

        return None, status.NOT_FOUND

    if not os.access(path, os.R_OK):
        return None, status.FORBIDDEN

    return path, status.OK


def get_content_type(path):
    mime_type, encoding = mimetypes.guess_type(path)
    encoding_str = f'; {encoding}' if encoding else ''
    return f'{mime_type}{encoding_str}'


def serve_not_found(conn: socket.socket):
    resp = builders.HTTPResponse()
    resp.set_status(status.NOT_FOUND)
    conn.send(resp.to_bytes())


def serve_file(conn: socket.socket, path, req: builders.HTTPRequest):
    try:
        resp = builders.HTTPResponse()
        content_size = os.path.getsize(path)
        content_type = get_content_type(path)
        resp.set_header('Content-Length', content_size)
        resp.set_header('Content-Type', content_type)

        conn.send(resp.to_bytes())

        if req.method == methods.HEAD:
            return

        with open(path, 'rb') as file:
            conn.sendfile(file)

    except Exception as e:
        serve_not_found(conn)


def serve_forbidden(conn: socket.socket):
    resp = builders.HTTPResponse()
    resp.set_status(status.FORBIDDEN)
    conn.send(resp.to_bytes())


def check_is_allowed(req: builders.HTTPRequest) -> bool:
    return req.method in methods.allowed_methods


def serve_not_allowed(conn: socket.socket):
    resp = builders.HTTPResponse()
    resp.set_status(status.NOT_ALLOWED)
    conn.send(resp.to_bytes())


def serve_request(req: builders.HTTPRequest, conn: socket.socket, config: Config):
    if not check_is_allowed(req):
        serve_not_allowed(conn)
        return

    path, st = check_path(req, config)

    if st == status.FORBIDDEN:
        serve_forbidden(conn)
    elif st == status.NOT_FOUND or path is None:
        serve_not_found(conn)
    else:
        serve_file(conn, path, req)


def do(conn: socket.socket, config: Config):
    req = builders.HTTPRequest()
    req.receive(conn)

    if req.ok:
        serve_request(req, conn, config)
    else:
        serve_not_found(conn)
