import time
import socket


class SHT75:
    dv = None
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    server_address = None

    def __init__(self, adress):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # raspberry on top of the climate chamber in the new clean room
        self.server_address = ('129.217.167.' + str(adress), 50000)
        self.sock.connect(self.server_address)
        pass

    def close(self):
        self.sock.close()

    def userCmd(self, cmd):
        # send command
        self.sock.send(cmd.encode())
        # receive data
        data = self.sock.recv(1024)
        data = data.decode('utf-8')
        return data

    def getValues(self):
        data = self.userCmd('READ')
        data = data.split(',')
        buffer = []
        for x in range(4):
            buffer.append(float(data[x]))
        return buffer

    def getTemperature(self, channels=2):
        data = self.userCmd('READ')
        #data = data.decode('utf-8')
        data = data.split(',')
        temp = []
        temp.append(float(data[0]))
        temp.append(float(data[1]))
        return temp

    def getHumidity(self):
        data = self.userCmd('READ')
        data = data.split(',')
        hum = []
        hum.append(float(data[2]))
        hum.append(float(data[3]))
        return hum
