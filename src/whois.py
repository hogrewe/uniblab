import re,redis,datetime
from uniblab_message import MessageResponse

whois_pattern = re.compile("^who[ ]*is ([^?]*)\?*", re.I)
whatis_pattern = re.compile("^what[ ]*(is|are) ([^' ]*)(?:'s)? ([^?]*)\?*", re.I)
whoami_pattern = re.compile("^who[ ]*am[ ]*i\?*", re.I)

class WhoIs:
    def __init__(self, uniblab):
        self.uniblab = uniblab

    def get_commands(self):
        return {'Who is xxx' : 'Replies with all of the information uniblab knows about user xxx'}

    def message(self, m, uniblab):
        if m.subject == None:
            return
        whois = whois_pattern.match(m.subject)
        if(whois):
            inquiry = whois.group(1)
            user = inquiry.lower()
            userstatus = uniblab.get_userinfo(user)
            if userstatus:
                response = user + ' info\n'
                response += '\n'.join(k + ' : ' + v for (k,v) in userstatus.items())
                print 'Question of:', m.subject, 'looking for who is ', inquiry, 'Responding with',response
            else:
                response = "I don't know who " + user + " is"
            return MessageResponse(response, True)

class WhatIs:
    def __init__(self, uniblab):
        self.uniblab = uniblab

    def get_commands(self):
        return {"What is <user>'s <property>" : 'Replies with the <property> info for <user>'}

    def message(self, m, uniblab):
        if m.subject == None:
            return
        whatis = whatis_pattern.match(m.subject)
        if(whatis):
            verb = whatis.group(1)
            user = whatis.group(2)
            user = user.lower()
            prop = whatis.group(3)
            userstatus = uniblab.get_userinfo(user)
            if userstatus:
                if prop in userstatus:
                    propval = userstatus[prop]
                    response = user + "'s " + prop + " " + verb + " " + propval
                else:
                    response = "I don't know what " + user + "'s " + prop + " " + verb
            else:
                response = "I don't know who " + user + " is"
            return MessageResponse(response, True)

class WhoAmI:
    def __init__(self, uniblab):
        self.uniblab = uniblab

    def get_commands(self):
        return {"Who am I?" : 'Replies with the information uniblab knows about you' }

    def message(self, m, uniblab):
        if m.subject == None:
            return
        whoami = whoami_pattern.match(m.subject)
        if(whoami):
            if m.username:
                user = m.username.lower()
                userstatus = uniblab.get_userinfo(user)
                response = user + ' info\n'
                response += '\n'.join(k + ' : ' + v for (k,v) in userstatus.items())
            else:
                response = "I don't know who " + m.sender + " is"

            return MessageResponse(response, True)
