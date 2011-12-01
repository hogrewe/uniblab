from twisted.internet import protocol
from twisted.internet import ssl
from twisted.mail import imap4

import uniblab_message

class UniblabIMAP4Client(imap4.IMAP4Client):
    def serverGreeting(self, caps):
        self.login(self.factory.transport.mail_user, self.factory.transport.mail_pass
            ).addCallback(self.onLogin, 

    def onLogin(self):
        pass

class UniblabIMAP4ClientFactory(protocol.ReconnectingClientFactory):
    def buildProtocol(self, addr):
        p = UniblabIMAP4Client()
        p.factory = self

        return p
    
    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason

class EmailTransport:
    def __init__(self, uniblab):
        self.uniblab = uniblab

    def config(self, config):
        self.channels = config.get('irc', 'channels').split(',')
        self.irc_host = config.get('irc', 'host')
        self.irc_port = config.getint('irc', 'port')
        self.nickname = config.get('irc', 'nickname')

    def connect(self):
        f = UniblabIMAP4ClientFactory(self.channels, self)
        reactor.connectTCP(self.irc_host, self.irc_port, f)

    def respond(self, m, response):
        if self.client != None:
            if response.respondall and m.receiver != self.nickname:
                user = m.receiver
            else:
                user = m.sender
            self.client.msg(user, response.text)

