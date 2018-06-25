import socket
from sht_sensor import Sht
#declare sensor on pins 7 and 8
sens1 = Sht(14,4)
sens2 = Sht(8,11)
#setup server/socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind(("",50000))
    #s.bind("129.217.167.177", 50000))
    s.listen(1)

    while True:
        komm, addr = s.accept()
        connected = True
        while connected:
            data = komm.recv(1024)
            print(data)
            data = data.decode('utf-8')
            if data == 'READ2':
                    temp1 = sens1.read_t()
                    hum1 =  round(sens1._read_rh(temp1),2)
                    temp2 = sens2.read_t()
                    hum2 =  round(sens2._read_rh(temp2),2)
                    answer = str('%.2f' % temp1) + ',' +  ',' + str('%.2f' % hum1) + ',' + str('%.2f' % temp2)  + str('%.2f' % hum2)
                    komm.send(answer.encode())
                    print(answer)
            elif data == 'READ':
                    temp1 = sens1.read_t()
                    hum1 =  round(sens1._read_rh(temp1),2)
                    answer = str('%.2f' % temp1) + ',' +  str('%.2f' % temp1)
                    komm.send(answer.encode())
                    print(answer)
            else:
                answer = 'command unknown'
                komm.send(answer.encode())
        break
finally:
        print('\n Socket closed')
        s.close()