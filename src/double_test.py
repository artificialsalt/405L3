import serial 
from matplotlib import pyplot

with serial.Serial('COM10', 115200, timeout=None) as s_port:
    data_1 = s_port.read_until()
    data_2 = s_port.read_until()

# Create a list of values from the incoming string of data
d1 = data_1.decode('utf-8').split(',')
d2 = data_2.decode('utf-8').split(',')

t1 = []
p1 = []
t2 = []
p2 = []

# Separate time and position values
for i in range(len(d1)):
    if i % 2 == 0:
        t1.append(int(d1[i]))
    else:
        p1.append(int(d1[i]))
for i in range(len(d2)):
    if i % 2 == 0:
        t2.append(int(d2[i]))
    else:
        p2.append(int(d2[i]))

pyplot.plot(t1, p1)
#pyplot.plot(t2, p2)
pyplot.xlabel('Time [ms]')
pyplot.ylabel('Encoder ticks')
pyplot.show()