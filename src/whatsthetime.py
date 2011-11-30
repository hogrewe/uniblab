import re,redis,datetime
from uniblab_message import MessageResponse

whatsthetime_pattern = re.compile("^what time is it\??", re.I)

class WhatsTheTime:
    def __init__(self, uniblab):
        self.uniblab = uniblab

    def get_commands(self):
        return {'What time is it?' : 'Responds with the server time'}

    def message(self, m, uniblab):
        if m.subject == None:
            return
        whatsthetime = whatsthetime_pattern.match(m.subject)
        if(whatsthetime):
            response = "It's now " + str(datetime.datetime.today())
            return MessageResponse(response, True)

