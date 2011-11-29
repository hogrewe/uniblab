import re,redis,datetime
from uniblab_message import MessageResponse

whois_pattern = re.compile("^who[ ]*is ([^?]*)\?*", re.I)

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
            response = user + ' info\n'
            response += '\n'.join(k + ' : ' + v for (k,v) in userstatus.items())
            print 'Question of:', m.subject, 'looking for who is ', inquiry, 'Responding with',response
            return MessageResponse(response, True)

