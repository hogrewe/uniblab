from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

import time, sys

import uniblab_message

class UniblabIRCClient(irc.IRCClient):
    transport_type = 'irc'

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        for c in self.factory.channels:
            self.join(c)

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        pass

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]

        username = self.factory.transport.uniblab.username_from_irc(user.lower())
        message = uniblab_message.uniblab_message(user, channel, msg, None, self.transport_type, username)
        self.factory.transport.uniblab.message(message,self.factory.transport )

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        self.logger.log("* %s %s" % (user, msg))

    # irc callbacks

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]

class UniblabIRCFactory(protocol.ClientFactory):
    def __init__(self, channels, transport):
        self.channels = channels
        self.transport = transport

    def buildProtocol(self, addr):
        p = UniblabIRCClient()
        p.nickname = self.transport.nickname
        p.factory = self
        self.transport.client = p
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason

class IRCTransport:
    def __init__(self, uniblab):
        self.uniblab = uniblab

    def config(self, config):
        self.channels = config.get('irc', 'channels').split(',')
        self.irc_host = config.get('irc', 'host')
        self.irc_port = config.getint('irc', 'port')
        self.nickname = config.get('irc', 'nickname')

    def connect(self):
        f = UniblabIRCFactory(self.channels, self)
        reactor.connectTCP(self.irc_host, self.irc_port, f)

    def respond(self, m, response):
        if self.client != None:
            if response.respondall and m.receiver != self.nickname:
                user = m.receiver
            else:
                user = m.sender
            self.client.msg(user, response.text)

