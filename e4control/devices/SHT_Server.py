import socket
from sht_sensor import Sht


def read_sensors(sensors):
    answer = ''
    for idx, sensor in enumerate(sensors, start=1):
        try:
            temp = sensor.read_t()
            hum = sensor.read_rh(temp)
        except:
            temp = float('nan')
            hum = float('nan')
            print('Exception while reading the {}. sensor in the sensor list.'.format(idx))
        answer += '{:.2f},{:.2f},'.format(temp, hum)
    komm.send(answer[:-1].encode())
    print(answer[:-1])


# Set VDD and GND to the corresponding pins on the Pi. The standard for SHT is 3.3V.
# Set the data pins according to the definition.
# declare sensor on GPIO pins 14 (SCK) and 4 (DATA)
sens1 = Sht(14, 4)
# declare sensor on GPIO pins 8 and 11
sens2 = Sht(8, 11)
# Possibility to add a third sensor:
sens3 = Sht(20, 26, voltage='5V')
# N.B.: you can always check the pins on the Pi with 'pinout'!

# setup server/socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    s.bind(("", 50000))
    s.listen(5)

    while True:
        komm, addr = s.accept()
        while True:
            data = komm.recv(1024)
            print(data)
            data = data.decode('utf-8')
            if data == 'CLOSE':
                break

            if data == 'READ':
                read_sensors([sens1, sens2])
            elif data == 'READ1':
                sensors = read_sensors([sens1])
            elif data == 'READ2':
                sensors = read_sensors([sens2])
            elif data == 'READ3':
                sensors = read_sensors([sens1, sens2, sens3])
            else:
                answer = 'unknown command'
                komm.send(answer.encode())
            s.close()
        break
finally:
    print('\n Socket closed')
    s.close()
