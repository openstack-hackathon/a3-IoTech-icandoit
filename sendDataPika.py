import pika
import time, sys, signal, atexit
import mraa
import pyupm_grove as grove #knob, temperature, light
# import pyupm_otp538u as upmOtp538u #temperature
import pyupm_mic as upmMicrophone #mic
import time
import json
from pprint import pprint

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

## Exit handlers ##
# This stops python from printing a stacktrace when you hit control-C
def SIGINTHandler(signum, frame):
    raise SystemExit

# This lets you run code on exit, including functions from myTempIR
def exitHandler():
    print "Exiting"
    sys.exit(0)

def value(sensor):
    if(type(sensor) is grove.GroveRotary):
        return sensor.abs_value()
    elif(type(sensor) is upmMicrophone.Microphone):
        return micValue(sensor)
    elif(type(sensor) is grove.GroveLight):
        return sensor.value()
    elif(type(sensor) is grove.GroveTemp):
        return sensor.value()

def name(sensor):
    if(type(sensor) is grove.GroveRotary):
        return "knob"
    elif(type(sensor) is upmMicrophone.Microphone):
        return "mic"
    elif(type(sensor) is grove.GroveLight):
        return "light"
    elif(type(sensor) is grove.GroveTemp):
        return "temperature"

def micValue(myMic):
    buffer = upmMicrophone.uint16Array(128)
    len = myMic.getSampledWindow(2, 128, buffer);
    if len:
        thresh = myMic.findThreshold(threshContext, 30, buffer, len)
        #myMic.printGraph(threshContext)
        if(thresh):
            return thresh
    return -1

#get the json
with open('cfg.json') as data_file:
    data = json.load(data_file)
pprint(data)

sensors = []

for i in data["sensors"]:
    if i["type"] == "temperature":
        sensors.append(grove.GroveTemp(i["port"]))

    if i["type"] == "knob":
        sensors.append(grove.GroveRotary(i["port"]))

    if i["type"] == "mic":
        mic = upmMicrophone.Microphone(i["port"])
        threshContext = upmMicrophone.thresholdContext()
        threshContext.averageReading = 0
        threshContext.runningAverage = 0
        threshContext.averagedOver = 2
        sensors.append(mic)

    if i["type"] == "light":
        sensors.append(grove.GroveLight(3))
# temp
# analog voltage, usually 3.3 or 5.0
# OTP538U_AREF = 4.0
# temperature = upmOtp538u.OTP538U(0, 1, OTP538U_AREF)
#temperature = grove.GroveTemp(0)

# atexit.register(exitHandler)
# signal.signal(signal.SIGINT, SIGINTHandler)

# knob
# New knob on AIO pin
#knob = grove.GroveRotary(1)

# mic
# Attach microphone to analog port
#mic = upmMicrophone.Microphone(2)
#threshContext = upmMicrophone.thresholdContext()
#threshContext.averageReading = 0
#threshContext.runningAverage = 0
#threshContext.averagedOver = 2

# light
# Create the light sensor object using AIO
#light = grove.GroveLight(3)

credentials = pika.PlainCredentials('harambe3', 'banana')
connection = pika.BlockingConnection(pika.ConnectionParameters(data["ip"], credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue='sensors')

#channel.basic_publish(exchange='',
#                      routing_key='sensors',
#                      body='Hello World!')


while True:
    #print str(value(sensors[0])) + ';' + str(value(sensors[1])) + ';' + str(value(sensors[2])) + ';' + str(value(sensors[3]))
    #client.publish("hello", str(value(sensors[0])) + ';' + str(value(sensors[1])) + ';' + str(value(sensors[2])) + ';' + str(value(sensors[3])))
    for i in sensors:
        channel.basic_publish(exchange='',
                      routing_key='sensors',
                      body = name(i) + ":" + str(value(i)))
        print("sensors", name(i) + ":" + str(value(i)))
    time.sleep(1)
connection.close()