#!/usr/bin/python

import time
import serial
import splunk_hec_sender
import os
import re
import smbus
from kafka import KafkaProducer
from kafka.errors import KafkaError

producer = KafkaProducer(bootstrap_servers=['10.100.0.151:9092'])

# The Arduino talks to the Pi over serial on USB
ser = serial.Serial(
 port='/dev/ttyUSB0',
 baudrate = 9600,
 parity=serial.PARITY_NONE,
 stopbits=serial.STOPBITS_ONE,
 bytesize=serial.EIGHTBITS,
 timeout=1
)

# The Pi sends data to the serial LCD using GPIO pins
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
# This is the i2c address of the arduino ?

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
	# format output and send to serial LCD pack
	# LCD is 16 characters by two rows
	line = data
	# incoming data looks like cm=99 in=13
	kv = re.split(' ', line)
	for pair in kv:
		n = 15
		data_length = len(pair)
		padding = n - data_length
		padding = int(padding)
		padding = str(' ' * padding)
		e = pair + ' ' +  padding
		print(e) # send to on screen output
		# Send to serial LCD	
		ser1.write(e.encode(encoding='UTF-8'))
		time.sleep(.25)

def to_hec(data):
	e = splunk_hec_sender.EventPreamble()
	event_list = e.create_event_base(this_pid_str,this_script)
	e_notice = data
	event = [e_notice]
	event_list.extend(event)
	splunk_hec_sender.create_json_data(event_list,this_script)

def to_kafka(data):
	# From https://kafka-python.readthedocs.io/en/master/usage.html
	# Asynchronous by default
	future = producer.send('noodles', data)

	# Block for 'synchronous' sends
	try:
    		record_metadata = future.get(timeout=10)
	except KafkaError:
    		# Decide what to do if produce request failed...
    		log.exception()
    		pass

	# Successful result returns assigned partition and offset
	# uncomment for debugging
	# print (record_metadata.topic)
	# print (record_metadata.partition)
	# print (record_metadata.offset)

while 1:
 # send a "1" to the arduino on the I2C bus to get this party started
 # otherwise it runs its code at boot
 write_byte(1,1)
 data=ser.readline()
 data=str(data)
 nice_data = clean_data(data)
 # send data to Splunk HEC
 to_hec(nice_data)
 # send data to serial LCD
 sweet_16(nice_data, 16)
 # send data to Kafka
 to_kafka(nice_data)
