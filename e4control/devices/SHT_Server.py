import socket
from sht_sensor import Sht
from subprocess import call
import signal
#declare sensor on pins 14 and 4
sens1 = Sht(14,4)
#declare sensor on pins 8 and 11
sens2 = Sht(8,11)
#setup server/socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#def handler(signum, frame):
#   raise IOError('SHT not answering.')

try:
    s.bind(("",50000))
    s.listen(1)

    while True:
        komm, addr = s.accept()
        connected = True
        while connected:
            data = komm.recv(1024)
            print(data)
            data = data.decode('utf-8')
            if data == 'READ2':
                   # signal.signal(signal.SIGALRM, handler)
                    #signal.alarm(1)
                    temp1 = sens1.read_t()
                    hum1 =  round(sens1._read_rh(temp1),2)
                    try:
                        temp2 = sens2.read_t()
                        hum2 =  round(sens2._read_rh(temp2),2)
                        #signal.alarm(0)
                    except:
                        temp2 = temp1
                        hum2 = hum1
                    answer = str('%.2f' % temp1) + ',' +  str('%.2f' % hum1) + ',' + str('%.2f' % temp2)  + ',' +  str('%.2f' % hum2)
                    komm.send(answer.encode())
                    print(answer)
            elif data == 'READ':
                    temp1 = sens1.read_t()
                    hum1 =  round(sens1._read_rh(temp1),2)
                    answer = str('%.2f' % temp1) + ',' +  str('%.2f' % hum1)
                    komm.send(answer.encode())
                    print(answer)
            else:
                answer = 'command unknown'
                komm.send(answer.encode())
        break
finally:
        print('\n Socket closed')
        s.close()
