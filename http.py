import socket
import sys

IP = '127.0.0.1'
PORT = 5050
PATH = './html/'

def http_base_parse(lines, table, end=-1):
    for x in lines[1:end]:
        line = x.split(':')
        table[line[0]] = ':'.join(line[1:])

"""
  Server response:

     HTTP/1.1 200 OK
     Date: Mon, 27 Jul 2009 12:28:53 GMT
     Server: Apache
     Last-Modified: Wed, 22 Jul 2009 19:15:56 GMT
     ETag: "34aa387-d-1568eb00"
     Accept-Ranges: bytes
     Content-Length: 51
     Vary: Accept-Encoding
     Content-Type: text/plain

     Hello World! My payload includes a trailing CRLF.
"""
def http_response_parse(body):
    lines = body.split('\n')
    response_table = {}
    print(lines[0].split())
    protocol, code, *rst = lines[0].split()
    response_table['protocol'] = protocol
    response_table['code'] = code
    response_table['rst'] = ' '.join(rst)
    body_sepa_index = lines.index('')
    http_base_parse(lines[1:], response_table, body_sepa_index)
    response_table['body'] = '\n'.join(lines[body_sepa_index+1:])

    return response_table


"""
Client request:

     GET /hello.txt HTTP/1.1
     User-Agent: curl/7.16.3 libcurl/7.16.3 OpenSSL/0.9.7l zlib/1.2.3
     Host: www.example.com
     Accept-Language: en, mi
"""
def http_request_parse(body):
    lines = body.split('\n')
    request_table = {}
    print(lines[0].split())
    tp, path, protocol = lines[0].split()
    request_table['protocol'] = protocol
    request_table['tp'] = tp
    request_table['path'] = path
    http_base_parse(lines[1:], request_table)

    return request_table

def request(ip, port, path):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))
        s.sendall("""GET {} HTTP/1.1
User-Agent: unche
Host: localhost
Accept-Language: en, mi""".format(path).encode('utf-8'))
        data = s.recv(1024)
        print(http_response_parse(data.decode('utf-8')))

def srv():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((IP, PORT))
        s.listen(1)
        while True:
            conn, addr = s.accept()
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    try:
                        tbl = http_request_parse(data.decode('utf-8'))
                        text = ""
                        with open("./html"+tbl['path']) as f:
                            text = f.read()
                            conn.sendall("""HTTP/1.1 200 OK
Date: Mon, 27 Jul 2009 12:28:53 GMT
Server: unche
Last-Modified: Wed, 22 Jul 2009 19:15:56 GMT
ETag: "34aa387-d-1568eb00"
Accept-Ranges: bytes
Content-Length: 51
Vary: Accept-Encoding
Content-Type: text/html

{}""".format(text).encode('utf-8'))
                    except FileNotFoundError:
                        conn.sendall("""HTTP/1.1 404 Not Found
Server: unche
Date: Mon, 27 Jul 2009 12:28:53 GMT
Content-Length: 51
Content-Type: text/plain
Connection: keep-alive

404 not found...
""".encode('utf-8'))


if __name__ == '__main__':
    if sys.argv[1] == 'clt':
        ip, port, path = sys.argv[2:]
        print(request(ip, int(port), path))
    elif sys.argv[1] == 'srv':
        srv()
