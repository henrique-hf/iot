import requests
import json
import datetime
import pymysql
import cherrypy
import webbrowser


class Packet(object):
    exposed = True

    def __init__(self):
        ############# change the address of the webserver
        self.host = requests.get('http://127.0.0.1:8089/database').content
        self.topics = requests.get('http://127.0.0.1:8089/topics').content
        self.topicsJSON = json.loads(self.topics)
        self.lat = self.topicsJSON['latitude']
        self.long = self.topicsJSON['longitude']

    # generates an IdNumber for the packet based on the date
    def idNumber(self):
        time = datetime.datetime.today()
        """Generate a number based on timestamp that will be used as the channel
        name of that package"""

        return "%04d%02d%02d%02d%02d%02d" % (
            time.year, time.month, time.day, time.hour, time.minute, time.second)

    # inserts a packet in the DB
    def insertPacket(self, packet, name, address, n_address, zip, city, telephone, lat, lon):
        script = "INSERT INTO `tracking`.`packet` (`packetid`, `name`, `address`,`n_address`, `zip`, `city`, `telephone`,`lat`,`long`) VALUES ("
        script += "\'" + str(packet) + "\',"
        script += "'" + name + "',"
        script += "'" + address + "',"
        script += "'" + str(n_address) + "',"
        script += "'" + str(zip) + "',"
        script += "'" + city + "',"
        script += "'" + str(telephone) + "',"
        script += "'" + str(lat) + "',"
        script += "'" + str(lon) + "')"

        try:
            db = pymysql.connect(host=self.host, user="root", passwd="", db="tracking")
            cursor = db.cursor()
            cursor.execute(script)
            db.commit()
            print_script = 'SELECT * FROM tracking.packet as tp ORDER BY tp.packetid desc'
            cursor.execute(print_script)
            for row in cursor.fetchall():
                print (row)
            db.close()

        except Exception as e:
            print ('Error in reading database', e)

    # returns 0 if the association is not in the table, 1 otherwise
    def findPacketinTruck(self, packetid, truckid):
        script = 'SELECT DISTINCT COUNT(*) FROM `tracking`.`p_t` WHERE `packetid`=\'' + str(
            packetid) + '\' AND `truckid` = \'' + truckid + '\';'
        print (script)

        try:
            db = pymysql.connect(host=self.host, user="root", passwd="", db="tracking")
            cursor = db.cursor()
            cursor.execute(script)
            x = cursor.fetchone()[0]
            db.close()
            return x

        except:
            print ('Error in reading database')

    # returns 0 if the packet is not in the system, 1 otherwise
    def findPacket(self, packetid):
        script = 'SELECT COUNT(*) FROM `tracking`.`packet` WHERE `packetid`=\'' + str(packetid) + '\';'
        print (script)
        try:
            db = pymysql.connect(host=self.host, user="root", passwd="", db="tracking")
            cursor = db.cursor()
            cursor.execute(script)
            x = cursor.fetchone()[0]
            print (x)
            db.close()
            return x

        except:
            print ('Error in reading database')

    # removes a packet from the DB
    def deletePacket(self, packetid):
        script = "DELETE FROM `tracking`.`packet` WHERE `packetid`='" + str(packetid) + "';"
        try:
            db = pymysql.connect(host=self.host, user="root", passwd="", db="tracking")
            cursor = db.cursor()
            cursor.execute(script)
            db.commit()
            db.close()
            if not self.findPacket(packetid):
                return 1

            else:
                return 0

        except:
            print ('Error in reading database')

    # associates a packet with a truck in the p_t table of the DB
    def insertPacketInTruck(self, packetid, truckid):
        script = "INSERT INTO `tracking`.`p_t` (`packetid`, `truckid`) VALUES ('" + packetid + "', '" + truckid + "');"

        try:
            db = pymysql.connect(host=self.host, user="root", passwd="", db="tracking")
            cursor = db.cursor()
            cursor.execute(script)
            db.commit()
            db.close()

            if (self.findPacketinTruck(packetid, truckid)):
                return 1

            else:
                return 0

        except:
            print ('Error in reading database')
            return 0

    # returns the truckid given the id of the packet
    def findTruckAssociation(self, packet):
        if self.findPacket(packet):
            script = 'SELECT truckid FROM p_t' \
                     ' WHERE packetid = ' + packet

            try:
                db = pymysql.connect(host=self.host, user="root", passwd="", db="tracking")
                cursor = db.cursor()
                cursor.execute(script)
                x = cursor.fetchone()
                db.close()
                if x is None:
                    return 0
                else:
                    truckid = x[0]
                    return truckid

            except:
                print ('Error in reading database')
        else:
            return 'Packet' + packet + 'not present in the system'

    # update the status of the delivery to delivered
    def packetDelivered(self, packet, truck):
        if self.findPacketinTruck(packet, truck):
            script = "UPDATE `tracking`.`p_t` SET `delivered`='1' WHERE `packetid`='" + packet + "' and`truckid`='" + truck + "';"
            try:
                db = pymysql.connect(host=self.host, user="root", passwd="", db="tracking")
                cursor = db.cursor()
                cursor.execute(script)
                db.close()
            except:
                print ('Error in reading database')
        else:
            if self.findPacket(packet):
                return 'Packet ' + packet + 'not present in the truck ' + truck
            else:
                return 'Packet ' + packet + ' not present in the system at all'

    # check if a packet has been delivered
    def isDelivered(self, packet, truck):
        script = 'SELECT delivered FROM p_t WHERE packetid = \'' + packet + '\'AND truckid = \'' + truck + '\';'

        if self.findPacketinTruck(packet, truck):
            try:
                db = pymysql.connect(host=self.host, user="root", passwd="", db="tracking")
                cursor = db.cursor()
                cursor.execute(script)
                x = cursor.fetchone()
                db.close()
                return x

            except:
                print ('Error in reading database')

        else:
            return None

    # retrieve list of trucks in the system
    def TrucksInSys(self):
        ##### change address (home catalog)
        data = requests.get('http://127.0.0.1:8089/trucks').content
        dataJSON = json.loads(data)
        trucks = []
        for element in dataJSON:
            trucks.append(element['channelName'])
            # trucks.append('\n')
        return trucks

    # retrieves from ThingSpeak the ID of a channel for a gien truckid
    def channelIDretrieve(self, truckID):
        ##### change address (home catalog)
        data = requests.get('http://127.0.0.1:8089/trucks').content
        dataJSON = json.loads(data)
        for element in dataJSON:
            if element['channelName'] == str(truckID):
                return element['channelID']

    # retrieve the truck associated to the packet
    def retreivePacketAssociation(self, packetid):
        if self.findPacket(packetid):
            truckid = self.findTruckAssociation(packetid)
            return truckid
        else:
            return 0

    # retrieve the position of the packet based on the truck position on T.S.
    def retrievePosition(self, truckid):
        channel = self.channelIDretrieve(truckid)
        url = 'https://api.thingspeak.com/channels/' + str(channel) + '/feeds/last'
        pos = json.loads(requests.get(url).content)
        string = '{"lat" :' + str(pos[self.lat]) + ',"long": ' + str(pos[self.long]) + '}'
        d = json.loads(string)
        return d

    def GET(self, *uri, **params):

        if uri[0] == 'findPacket':
            if self.findPacket(params['packetid']):
                print (params['packetid'])
                truckid = self.findTruckAssociation(params['packetid'])
                channel = self.channelIDretrieve(truckid)
                position = self.retrievePosition(truckid)
                webbrowser.open_new_tab('http://localhost/maps.php/?lat=' + str(position['lat']) + '&long=' + str(
                    position['long']) + '&channel=' + channel)
                # print ('http://localhost/maps.php/?lat='+str(position['lat'])+'&long='+str(position['long']))
            else:
                print ('The id inserted is not valid!')

        if uri[0] == 'listOfTrucks':
            return self.TrucksInSys()

        if uri[0] == 'booleanPacket':
            return str(self.findPacket(params['packetid']))

        if uri[0] == 'packetInTruck':
            return str(self.findPacketinTruck(params['packetid'], params['truckid']))

        if uri[0] == 'create':
            complete_address = params['address'] + " " + params['nr'] + " " + params['zip'] + " " + params['city']
            geometry = json.loads(
                requests.get('https://maps.googleapis.com/maps/api/geocode/json?address=' + complete_address).content)

            lat = geometry['results'][0]['geometry']['location']['lat']
            long = geometry['results'][0]['geometry']['location']['lng']

            self.insertPacket(self.idNumber(), params['name'], params['address'], params['nr'], params['zip'],
                              params['city'], params['telephone'], lat, long)

            return json.dumps(params) + ' INSERTED'

        if uri[0] == 'associate':
            if self.findPacket(params['packetid']):
                try:
                    self.insertPacketInTruck(params['packetid'], params['truckid'])
                    return 'Packet ' + params['packetid'] + ' inserted in truck ' + params['truckid']
                except:
                    return 'Error in inserting the packet'
            else:
                return 'Packet not present in the system'

        if uri[0] == 'delivered':
            if self.findPacket(params['packetid']) and self.findPacketinTruck(params['packetid'], params['truckid']):
                try:
                    self.packetDelivered(params['packetid'], params['truckid'])
                    return 'Packet ' + params['packetid'] + ' delivered ' + params['truckid']

                except:
                    return 'Error in removing the packet'

            else:
                return 'Packet not present in the system'


if __name__ == "__main__":
    conf = {
        "/": {
            "request.dispatch": cherrypy.dispatch.MethodDispatcher(),
            "tools.sessions.on": True,
        }
    }
    cherrypy.tree.mount(Packet(), "/", conf)
    cherrypy.config.update({
        "server.socket_host": '192.168.43.175',
        "server.socket_port": 8089})
    cherrypy.engine.start()
    cherrypy.engine.block()
