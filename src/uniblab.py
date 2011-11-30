from time import sleep
import os
import time
import email_transport
import irc_transport
import uniblab_message
import re,redis
import wfh
import whois
import myinfois
import whatcanyoudo
import whatsthetime
import proderrors
import ConfigParser

class Uniblab:
    def __init__(self):
        cp = ConfigParser.SafeConfigParser()
        cp.readfp(open('.uniblab.cfg'))
        self.redis_client = redis.Redis()
        self.plugins = [wfh.WFH(self), wfh.IsWFH(self), wfh.WorkStatusReset(self), whois.WhoIs(self), myinfois.SetMyInfo(self), myinfois.UnsetMyInfo(self),whatcanyoudo.WhatCanYouDo(self),whatsthetime.WhatsTheTime(self),proderrors.ProdErrorsCounter(self),proderrors.HowManyProdErrors(self)]
        for p in self.plugins:
            if hasattr(p, 'config'):
                p.config(cp)
        for p in self.plugins:
            if hasattr(p, 'config'):
                p.config(cp)
        self.transports = [email_transport.EmailTransport(self),irc_transport.IRCTransport(self)]
        for t in self.transports:
            if hasattr(t, 'config'):
                t.config(cp)
        self.httpport = 80

    def start(self):
        for p in self.plugins:
            if hasattr(p, 'start'):
                p.start()
        for t in self.transports:
            t.connect()

    def message(self,m,transport):
        for p in self.plugins:
            if(hasattr(p, 'message')):
                response = p.message(m, self)
                if response != None:
                    transport.respond(m, response)

    def username_from_email(self, email):
        # first look for an email
        username = self.redis_client.hget('useremails', email.lower())

        return username

    def create_user_from_email(self, email):
        # Create the username as the part before the @ in the email
        email_match = re.match('(.*)@.*', email)
        if email_match:
            print "Couldn't find user mapping for email", email,'creating new user'
            username = email_match.group(1)
            self.create_user(username, None, email, None)

    def username_from_irc(self, ircnick):
        username = self.redis_client.hget('userircs', ircnick.lower())
        return username

    def create_user(self, username, realname, email, irc):
        self.redis_client.hset(':'.join(['users',username]), 'email', email)
        self.redis_client.hset('useremails', email, username)
        if irc:
            self.redis_client.hset(':'.join(['users',username]), 'irc', irc)
            self.redis_client.hset('userircs', irc, username)
        if realname:
            self.redis_client.hset(':'.join(['users',username]), 'realname', realname)

    def set_userinfo(self, username, info):
        print info
        for (k,v) in info.items():
            self.redis_client.hset('users:'+username, k, v)
            if k == 'ircnick':
                self.redis_client.hset('userircs', v, username)

    def unset_userinfo(self, username, propname):
        self.redis_client.hdel('users:'+username, propname)
        
    def get_userinfo(self, username):
        userinfo = self.redis_client.hgetall('users:' + username)

        return userinfo

    def get_allusers(self):
        return self.redis_client.hvals('useremails')

    def get_workstatus(self, username):
        return self.redis_client.hget(':'.join(["users", username]), 'workstatus')

    def set_workstatus(self, username, status):
       self.redis_client.hset(':'.join(['users',username]), 'workstatus', status)


def main():
    os.environ['TZ'] = 'US/Mountain'
    time.tzset()
    uniblab = Uniblab()
    uniblab.start()
    while True:
        sleep(60*60*24)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
       print 'Exiting on ^C' 
