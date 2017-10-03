import cherrypy
import json


@cherrypy.expose
class Catalog(object):
    expose = True

    def __init__(self):
        self.file = open("catalog.json", "r")
        self.catalog = json.load(self.file)
        self.file.close()

    def GET(self, *uri):
        # OK
        if uri[0] == 'topics':
            print self.catalog['topics']
            print type(self.catalog['topics'])
            return json.dumps(self.catalog['topics'])

        # OK
        elif uri[0] == 'broker':
            print self.catalog['broker']
            print type(self.catalog['broker'])
            return json.dumps(self.catalog['broker'])

        # OK
        elif uri[0] == 'telegram':
            print self.catalog['telegram']
            print type(self.catalog['telegram'])
            return json.dumps(self.catalog['telegram'])

        # OK
        elif uri[0] == 'key':
            print self.catalog['key']
            print type(self.catalog['key'])
            return self.catalog['key']

        # OK
        elif uri[0] == 'user':
            print self.catalog['user']
            print type(self.catalog['user'])
            return self.catalog['user']

        # OK
        elif uri[0] == 'sensor':
            for truck in self.catalog['trucks']:
                if uri[1] == truck['raspberryMAC']:
                    return json.dumps(truck)


if __name__ == "__main__":
    conf = {
        "/": {
            "request.dispatch": cherrypy.dispatch.MethodDispatcher(),
            "tools.sessions.on": True,
        }
    }
    # cherrypy.tree.mount(Catalog(), "/", conf)
    # cherrypy.engine.start()
    # cherrypy.engine.block()
    cherrypy.quickstart(Catalog(), '/', conf)
