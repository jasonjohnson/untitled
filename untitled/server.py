import socket
from threading import Thread
from Queue import Queue
from SocketServer import (StreamRequestHandler, TCPServer, ThreadingMixIn)


class Player(object):
    def __init__(self):
        self.uid = None
        self.location = ()


class World(object):
    def __init__(self):
        self.players = {}


class RequestHandler(StreamRequestHandler):
    def handle_uid(self, payload):
        """payload = ['{uid}']"""
        return "error"

    def handle_move(self, payload):
        """payload = ['{uid},{x},{y}']"""
        return "error"

    def handle_location(self, payload):
        """payload = ['{uid},{x},{y}']"""
        return "error"

    def handle_locations(self, payload):
        """payload = ['{uid},{x},{y}','{uid},{x},{y}','{uid},{x},{y}']"""
        return "error"

    def handle(self):
        """
        The client <-> server line protocol.

        <- uid
        -> uid|{uid}
        -> uid|error

        <- move|{uid},{x},{y}
        -> move|ok
        -> move|error

        <- locations
        -> locations|{uid},{x},{y}|{uid},{x},{y}|{uid},{x},{y}
        -> locations|error

        <- location|{uid}
        -> location|{uid},{x},{y}
        -> location|error
        """
        commands = {
            'uid': self.handle_uid,
            'move': self.handle_move,
            'location': self.handle_location,
            'locations': self.handle_locations
        }

        # Prepare the raw content from the client.
        raw = self.rfile.readline()
        raw = raw.strip()
        raw = raw.split("|")

        # The first element of our list after splitting is always the command
        # from the client. Everything else each handler will need to deal with.
        command = raw[0]
        payload = raw[1:]

        # I want to see KeyError's for now. Will probably be something I've
        # messed up in the client.
        self.wfile.write("%s|%s\n" % (command, commands[command](payload)))


# Instead of setting the world directly, I should probably use thread-safe
# queues to mutate the world state. This would allow me to not only have clients
# send in events - but I could run a thread to send in world "tick" events, too.
class Server(ThreadingMixIn, TCPServer):
    def set_world(self, world):
        self.world = world


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9990

    world = World()

    # At some point I will need to update the world and broadcast entity changes
    # to all of the clients. This broadcast doesn't need to be done in the
    # normal command sequence.
    #
    # world.update()

    server = Server((HOST, PORT), RequestHandler)
    server.set_world(world)
    server.serve_forever()
