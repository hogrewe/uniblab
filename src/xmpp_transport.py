from twisted.words.xish import domish
from twisted.words.protocols.jabber import jid
from twisted.internet import reactor, protocol
from twisted.application import service
from wokkel.xmppim import MessageProtocol, PresenceClientProtocol, RosterClientProtocol
from wokkel.xmppim import AvailablePresence
from wokkel.client import XMPPClient


import uniblab_message

class UniblabXMPPProtocol(MessageProtocol, PresenceClientProtocol,RosterClientProtocol):
    transport_type = 'gtalk'

    def connectionInitialized(self):
        print 'Initializing connection'
        MessageProtocol.connectionInitialized(self)
        PresenceClientProtocol.connectionInitialized(self)
        RosterClientProtocol.connectionInitialized(self)
        self.getRoster().addCallback(self.processRoster)

    def connectionMade(self):
        print "Connected!"
        self.available(None, None, {None: 'Being a bot'})


    def processRoster(self, roster):
        print 'Processing roster'
        for name,item in roster.items():
            print 'Processing item', name
            if not item.subscriptionTo:
                'Subscribing to', item.jid
                self.subscribe(item.jid)

    def connectionLost(self, reason):
        print "Disconnected!"

    def typing_notification(self, jid):
        """Send a typing notification to the given jid."""

        msg = domish.Element((None, "message"))
        msg["to"] = jid
        msg["from"] = self.transport.xmpp_user
        msg.addElement(('jabber:x:event', 'x')).addElement("composing")

        self.send(msg)

    def send_plain(self, user, content):
        msg = domish.Element((None, "message"))
        msg["to"] = user
        msg["from"] = self.parent.jid.full()
        msg["type"] = 'chat'
        msg.addElement("body", content=content)

        self.send(msg)

    def onMessage(self, msg):
        if msg["type"] == 'chat' and hasattr(msg, "body") and msg.body:
            self.typing_notification(msg['from'])
            user = msg['from'].split('/')[0]
            username = self.transport.uniblab.username_from_gtalk(user.strip().lower())
            message = uniblab_message.uniblab_message(msg['from'], self.transport.xmpp_user, str(msg.body), None, self.transport_type, username)
            self.transport.uniblab.message(message,self.transport )

    # presence stuff
    def availableReceived(self, entity, show=None, statuses=None, priority=0):
        user = entity.full().split('/')[0]
        username = self.transport.uniblab.username_from_gtalk(user.strip().lower())
        new_status = None
        if statuses:
            new_status = statuses[None]
        message = uniblab_message.uniblab_message(entity.full(), self.transport.xmpp_user, new_status, None, self.transport_type, username)
        self.transport.uniblab.status(message,self.transport )
        print "Available from %s (%s, %s)" % (entity.full(), show, statuses)

    def unavailableReceived(self, entity, statuses=None):
        print "Unavailable from %s" % entity.userhost()

    def subscribedReceived(self, entity):
        print "Subscribed received from %s" % (entity.userhost())
        self.subscribe(entity)
        self.subscribed(entity)
        self.send_plain(entity.full(), "Yo, I'm a bot.  Ask me: 'uniblab: what can you do?'")

    def unsubscribedReceived(self, entity):
        print "Unsubscribed received from %s" % (entity.userhost())
        self.unsubscribe(entity)
        self.unsubscribed(entity)

    def subscribeReceived(self, entity):
        print "Subscribe received from %s" % (entity.userhost())
        self.subscribe(entity)
        self.subscribed(entity)

    def unsubscribeReceived(self, entity):
        print "Unsubscribe received from %s" % (entity.userhost())
        self.unsubscribe(entity)
        self.unsubscribed(entity)

    def onRosterSet(self, item):
        if not item.subscriptionTo:
            self.subscribe(item.jid)
        print 'Roster set', item.jid.full()

    def onRosterRemove(self, entity):
        print 'Roster removed', entity.full()
     


class XMPPTransport:
    def __init__(self, uniblab):
        self.uniblab = uniblab

    def config(self, config):
        self.xmpp_host = config.get('xmpp', 'xmpp_host')
        self.xmpp_port = config.get('xmpp', 'xmpp_port')
        self.xmpp_user = config.get('xmpp', 'xmpp_user')
        self.xmpp_pass = config.get('xmpp', 'xmpp_pass')

    def connect(self):
        application = service.Application('UniblabXMPP')

        xmppclient = XMPPClient(jid.internJID(self.xmpp_user), self.xmpp_pass)
        self.client=UniblabXMPPProtocol()
        self.client.transport = self
        self.client.setHandlerParent(xmppclient)
        xmppclient.setServiceParent(application)

        xmppclient.startService()
        

    def respond(self, m, response):
        if self.client != None:
            if response.respondall and m.receiver != self.xmpp_user:
                user = m.receiver
            else:
                user = m.sender
            self.client.send_plain(user, response.text)
        
