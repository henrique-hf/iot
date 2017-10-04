import requests
import json


class Channels(object):
    def __init__(self):
        #read json file with configurations
        self.file = open("conf.json", "r")
        self.conf = json.load(self.file)
        self.file.close()
        # print 'conf file (' + str(type(self.conf)) + '): '
        # print self.conf

        self.user = self.conf["user"]
        self.apiKey = self.conf["key"]
        # print 'user (' + str(type(self.user)) + '): ' + self.user
        # print 'API Key (' + str(type(self.apiKey)) + '): ' + self.apiKey

    # OK
    def deleteAll(self):
        channels = requests.get("https://api.thingspeak.com/users/" + self.user + "/channels.json").content
        channelsJSON = json.loads(channels)

        listID = []

        for ch in channelsJSON["channels"]:
            listID.append(str(ch.get('id')))
        # print 'listID (' + str(type(listID)) + '): '
        # print listID

        for id in listID:
            delChannel = requests.delete('https://api.thingspeak.com/channels/' + id + '.json?api_key=' + self.apiKey)
            # print delChannel

    # OK
    # Obs: we can create multiple channels with the same name
    def create(self, name):
        data = {'name': name, 'api_key': self.apiKey, 'public_flag': 'true',
                self.conf['topics']['temperature']: 'Temperature', self.conf['topics']['humidity']: 'Humidity',
                self.conf['topics']['latitude']: 'Latitude', self.conf['topics']['longitude']: 'Longitude'}
        jsonData = json.dumps(data)
        # send the POST request to create the new channel
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        channel = requests.post('https://api.thingspeak.com/channels.json', data=jsonData, headers=headers)
        return channel

    # OK
    def getChannelID(self, name):
        channels = requests.get("https://api.thingspeak.com/users/" + self.user + "/channels.json").content
        channelsJSON = json.loads(channels)

        for ch in channelsJSON["channels"]:
            if ch.get("name") == str(name):
                channelID = str(ch.get('id'))
                # print 'channel ID (' + str(type(channelID)) + '): '
                # print channelID
                return channelID

    # OK
    def getChannelKey(self, channelID):
        channel = requests.get('https://api.thingspeak.com/channels/' + channelID + '.json?api_key=' + self.apiKey).content
        channelJSON = json.loads(channel)

        for i in channelJSON['api_keys']:
            if i['write_flag'] == True:
                channelKey = i['api_key']
                # print 'channel key (' + str(type(channelKey)) + '): '
                # print channelKey
                return channelKey


if __name__ == "__main__":

    channel = Channels()

    # clean thingspeak
    channel.deleteAll()

    for truck in channel.conf['trucks']:
        name = truck.get('channelName')
        # print name

        channel.create(name)

        # add channel id and key to the dict
        id = channel.getChannelID(name)
        key = channel.getChannelKey(id)

        truck['channelID'] = id
        truck['channelKey'] = key
        # print channel.conf

    finalFile = open('catalog.json', 'w')
    finalFile.write(json.dumps(channel.conf))
    finalFile.close()
