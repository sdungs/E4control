# -*- coding: utf-8 -*-

import socket


class Prologix():
    com = None
    host = None
    port = None

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.com = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.com.settimeout(1)

    def open(self):
        self.com.connect((self.host, 1234))
        self.setup()

    def close(self):
        self.com.close()

    def read(self, num_bytes=1024):
        self.select()
        self.write('++read eoi')
        v = self.com.recv(num_bytes)
        s = v.decode('ascii')
        s = s.replace('\r', '')
        s = s.replace('\n', '')
        return s

    def write(self, cmd):
        self.select()
        self.com.send(('%s\n' % cmd).encode('ascii'))

    def select(self):
        self.com.send(('++addr %i\n' % int(self.port)).encode('ascii'))

    def setup(self):
        self.write('++mode 1')
        self.write('++auto 0')
        self.write('++eos 3')
        self.write('++read_tmo_ms 1000')
