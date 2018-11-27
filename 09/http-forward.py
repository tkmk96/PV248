from sys import argv
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse, error
from urllib.request import Request, urlopen
import json


def create_json_data(code, headers, content):
    data = {'code': code}

    if headers:
        h_dict = dict()
        for header, value in headers:
            h_dict[header] = value
        data['headers'] = h_dict

    if content:
        try:
            data['json'] = json.loads(content)
        except ValueError:
            data['content'] = content

    return json.dumps(data, indent=4)


def validate_data(data):
    if data.get('url') is None:
        raise Exception("invalid json - missing url")
    if data.get('type') is not None and data.get('type') == 'POST' and data.get('content') is None:
        raise Exception("invalid json - missing content")


def HttpHandler(url):
    class Handler(BaseHTTPRequestHandler):
        def send(self, code, json_data):
            self.send_response(code)
            self.send_header('Content-Type', "application/json; charset=UTF-8")
            self.send_header('Content-Length', str(len(json_data)))
            self.end_headers()
            self.wfile.write(bytes(json_data, "UTF-8"))

        def do_GET(self):
            request_url = url
            params = parse.urlparse(self.path).query
            if params:
                request_url += '?' + params
            if 'Host' in self.headers:
                del self.headers['Host']
            self.headers['Accept-Encoding'] = 'identity'
            req = Request(request_url, None, self.headers, method="GET")
            try:
                with urlopen(req, timeout=1) as res:
                    self.send(HTTPStatus.OK, create_json_data(res.status, res.getheaders(), res.read().decode('UTF-8')))

            except error.HTTPError as http_error:
                self.send(HTTPStatus.OK, create_json_data(http_error.code, None, None))
            except:
                self.send(HTTPStatus.OK, create_json_data('timeout', None, None))

        def do_POST(self):
            try:
                content_length = int(self.headers.get('Content-Length'), 0)
                json_data = self.rfile.read(content_length)
                data = json.loads(json_data)
                validate_data(data)

            except:
                self.send(HTTPStatus.OK, create_json_data('invalid json', None, None))
                return

            try:
                method = data['type'] if data.get('type') is not None else 'GET'
                url = data['url']
                headers = data['headers'] if data.get('headers') is not None else dict()
                headers['Accept-Encoding'] = 'identity'
                if headers.get('Content-Type') is None:
                    headers['Content-Type'] = 'application/json; charset=utf-8'
                content = data['content'] if method == 'POST' else None
                json_content = json.dumps(content).encode('UTF-8') if content else None
                timeout = data['timeout'] if data.get('timeout') is not None else 1
                req = Request(url, json_content, headers, method=method)

                with urlopen(req, timeout=timeout) as res:
                    self.send(HTTPStatus.OK, create_json_data(res.status, res.getheaders(), res.read().decode('UTF-8')))
            except error.HTTPError as err:
                self.send(HTTPStatus.OK, create_json_data(err.code, None, None))
            except:
                return self.send(HTTPStatus.OK, create_json_data('timeout', None, None))

    return Handler


def main():
    port = int(argv[1])
    url = argv[2]
    if url.startswith('http://') or url.startswith('https://'):
        pass
    else:
        url = 'http://' + url
    server = HTTPServer(('', port), HttpHandler(url))
    server.serve_forever()


if __name__ == '__main__':
    main()
