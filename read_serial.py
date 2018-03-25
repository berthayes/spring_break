#!/usr/bin/python3

import time
import serial
import splunk_hec_sender
import os
import re
import smbus
 
ser = serial.Serial(
 port='/dev/ttyUSB0',
 baudrate = 9600,
 parity=serial.PARITY_NONE,
 stopbits=serial.STOPBITS_ONE,
 bytesize=serial.EIGHTBITS,
 timeout=1
)

ser1 = serial.Serial(
 port='/dev/ttyAMA0',
 baudrate = 9600,
 parity=serial.PARITY_NONE,
 stopbits=serial.STOPBITS_ONE,
 bytesize=serial.EIGHTBITS,
 timeout=1
)
 
this_script = os.path.basename(__file__)
this_pid_str = str(os.getpid())
bus = smbus.SMBus(1)

arduino_addy = 0x04

def read_words(addr):
        return bus.read_word_data(arduino_addy,addr)

def write_byte(register, value):
        bus.write_byte_data(arduino_addy, register, value)


def clean_data(data):
	dirty_data = data
	# data looks like this
	# b'in=8 cm=22\r\n'
	clean_bits = re.compile(r'b\'(.*)\\r\\n\'')
	clean_stream = clean_bits.sub(r'\1', data)
	return clean_stream

def sweet_16(data, n, c=0):
	line = data
	# incoming data looks like cm=99 in=13
	kv = re.split(' ', line)
	#print()
	#print(kv)
	for pair in kv:
		n = 15
		data_length = len(pair)
		#my_line = "data length is " + str(data_length)
		#print(my_line)
		padding = n - data_length
		#print("padding is")
		#print(str(padding))
		padding = int(padding)
		padding = str(' ' * padding)
		e = pair + ' ' +  padding
		#print(e)
		#return(e)
		ser1.write(e.encode(encoding='UTF-8'))
		to_hec(e)
		time.sleep(.25)
			

#def f(string, n, c=0):
#    if c < n:
#        print(string * n)
#        f(string, n, c=c + 1)

def to_hec(data):
	e = splunk_hec_sender.EventPreamble()
	event_list = e.create_event_base(this_pid_str,this_script)
	e_notice = data
	event = [e_notice]
	event_list.extend(event)
	splunk_hec_sender.create_json_data(event_list,this_script)

while 1:
 # send a "1" to the arduino on the I2C bus to get this party started
 write_byte(0x04,1)
 data=ser.readline()
 data=str(data)
 nice_data = clean_data(data)
 #to_hec(nice_data)
 one_line = sweet_16(nice_data, 16)
# print(one_line)
# ser1.write(one_line.encode(encoding='UTF-8'))
# time.sleep(.25)
