# The Raspberry Pi Connector is an implementation of the Device Connector that integrates into the
# platform raspberry pi boards. Each raspberry is equipped with motion, temperature and humidity
# sensors to provide environmental information about the status of a room. It provides Rest Web
# Services to retrieve environmental information (i.e. temperature and humidity). It also works as an
# MQTT publisher sending information on user presence (when detected) and environmental data
# (every 5 minutes).

import paho.mqtt.client as client
import Adafruit_DHT
import requests
import json
from uuid import getnode as get_mac
import paho.mqtt.publish as publish
import time

url = 'http://127.0.0.1:8080'

class Sensors(object):
    def __init__(self):
        self.mac = str(get_mac())
        print 'MAC ' + str(type(self.mac))
        print self.mac

        self.config = requests.get(url + '/sensor/' + self.mac).content
        self.configDict = json.loads(self.config)
        self.samplingRate = self.configDict['samplingRate']
        print 'ConfigDict ' + str(type(self.configDict))
        print self.configDict

    def getTemperature(self):
        if self.configDict['temperature']['active'] == True:
            pin = self.configDict['temperature']['pin']
            print 'Pin ' + str(type(pin))
            print pin
            temperature, humidity = Adafruit_DHT.read_retry(11, 2)
            return {'temperature': temperature, 'humidity': humidity}
        else:
            return False



    def getHumidity(self):
        if self.configDict['humidity']['active'] == True:
            pin = self.configDict['humidity']['pin']
            print 'Pin ' + str(type(pin))
            print pin
            humidity = Adafruit_DHT.read_retry(pin)
            return str(humidity)
        else:
            return False

    def getPosition(self):
        if self.configDict['position']['active'] == True:
            pin = self.configDict['position']['pin']
            print 'Pin ' + str(type(pin))
            print pin
            latitude, longitude = Adafruit_DHT.read_retry(pin)
            return {['latitude']: str(latitude), ['longitude']: str(longitude)}
        else:
            return False


class UpdateData(object):
    def __init__(self):
        self.mac = str(get_mac())
        print 'MAC ' + str(type(self.mac))
        print self.mac

        self.config = requests.get(url + '/sensor/' + self.mac).content
        self.configDict = json.loads(self.config)
        print 'ConfigDict ' + str(type(self.configDict))
        print self.configDict

        self.channelKey = self.configDict['channelKey']
        print 'channelKey ' + str(type(self.channelKey))
        print self.channelKey
        self.channelID = self.configDict['channelID']
        print 'channelID ' + str(type(self.channelID))
        print self.channelID

        self.topics = json.loads(requests.get(url + '/topics').content)
        print 'topics ' + str(type(self.topics))
        print self.topics

        self.broker = json.loads(requests.get(url + '/broker').content)
        print 'broker ' + str(type(self.broker))
        print self.broker

    # def connectMQTT(self):

    def publishTemp(self, temp):
        topic = 'channels/' + self.channelID + '/publish/fields/' + self.topics['temperature'] + '/' + self.channelKey
        print 'topic temperature ' + str(type(topic))
        print topic
        try:
            publish.single(topic=topic, payload=temp, hostname=self.broker['address'])
        except:
            print "Error while publishing temperature"

    def publishHum(self, hum):
        topic = 'channels/' + self.channelID + '/publish/fields/' + self.topics['humidity'] + '/' + self.channelKey
        try:
            publish.single(topic=topic, payload=hum, hostname=self.broker['address'])
        except:
            print "Error while publishing humidity"

    def publishPos(self, pos):
        topicLat = 'channels/' + self.channelID + '/publish/fields/' + self.topics['latitude'] + '/' + self.channelKey
        topicLong = 'channels/' + self.channelID + '/publish/fields/' + self.topics['longitude'] + '/' + self.channelKey
        try:
            publish.single(topic=topicLat, payload=pos['latitude'], hostname=self.broker['address'])
        except:
            print "Error while publishing latitude"
        try:
            publish.single(topic=topicLong, payload=pos['longitude'], hostname=self.broker['address'])
        except:
            print "Error while publishing longitude"

    # def disconnectMQTT(self):


if __name__ == "__main__":
    sensor = Sensors()
    update = UpdateData()

    sample = 0

    for sample in range(5):
        data = sensor.getTemperature()
        temp = data['temperature']
        hum = data['humidity']

        if temp != False:
            update.publishTemp(temp)

        if hum != False:
            update.publishHum(hum)

        sample = sample + 1

        time.sleep(5)
