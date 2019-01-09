import socket
from sht_sensor import Sht
from subprocess import call
import signal
#declare sensor on pins 14 and 4
sens1 = Sht(14,4)
#declare sensor on pins 8 and 11
sens2 = Sht(8,11)
#Possibility to add third sensor for Elenas purpose:
sens3 = Sht(20,26, voltage='5V')

#setup server/socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#def handler(signum, frame):
#   raise IOError('SHT not answering.')

try:
    s.bind(("",50000))
    s.listen(1)

    while True:
        komm, addr = s.accept()
        while True:
            data = komm.recv(1024)
            print(data)
            data = data.decode('utf-8')
            if data == 'READ':
                try:
                    temp1 = round(sens1.read_t(),2)
                    hum1 =  round(sens1._read_rh(temp1),2)
                except:
                    temp1 = 'nan'
                    hum1 = 'nan'
                    print('Exception while reading sensor 1.')
                try:
                    temp2 = round(sens2.read_t(),2)
                    hum2 =  round(sens2._read_rh(temp2),2)
                except:
                    temp2 = 'nan'
                    hum2 = 'nan'
                    print('Exception while reading sensor 2.')
                answer = '{},{},{},{}'.format(temp1,hum1,temp2,hum2)
                komm.send(answer.encode())
                print(answer)
            elif data == 'READ1':
                temp = round(sens1.read_t(),2)
                hum =  round(sens1._read_rh(temp),2)
                answer = '{},{}'.format(temp,hum)
                komm.send(answer.encode())
                print(answer)
            elif data == 'READ2':
                temp = round(sens2.read_t(),2)
                hum =  round(sens2._read_rh(temp),2)
                answer = '{},{}'.format(temp,hum)
                komm.send(answer.encode())
                print(answer)
            elif data == 'READ3':
                temp = []
                hum = []
                temp.append(round(sens1.read_t(),2))
                temp.append(round(sens2.read_t(),2))
                temp.append(round(sens3.read_t(),2))
                hum.append(round(sens1.read_rh(),2))
                hum.append(round(sens2.read_rh(),2))
                hum.append(round(sens3.read_rh(),2))
                answer = '{},{},{},{},{},{}'.format(temp[0],hum[0],temp[1],hum[1],temp[2],hum[2])
                komm.send(answer.encode())
                print(answer)

            elif data == 'CLOSE':
                break

            else:
                answer = 'command unknown'
                komm.send(answer.encode())
        break
finally:
        print('\n Socket closed')
        s.close()
