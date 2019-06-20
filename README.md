# spring_break
Python and Arduino code to send measurements from an ultrasonic rangefinder to Kafka and/or Splunk in real time.

I broke my ankle in February 2018 and spent all of Spring Break laid up on the couch.  I was working for Splunk at the time, and keen to add real-time sensor data to the platform.  Lately, I've been playing around with Confluent and Kafka, and discovered how easy it is to get data in. 

This is a pretty simple POC, using an arduino to send data from a distance sensor (https://www.parallax.com/product/28015) to a Raspberry Pi that can then stream data to Kafka or Splunk.  It also sends a readout of the data to a serial-controlled LCD panel, because it looks cool. https://www.sparkfun.com/products/10097

The code sends data to Splunk's HTTP Event Collector (HEC) http://dev.splunk.com/view/event-collector/SP-CAAAE6M and sends data to Kafka using kafka-python https://kafka-python.readthedocs.io/en/master/

