class uniblab_message:
    def __init__(self, sender, receiver, subject, body, transport_type, username):
        self.sender = sender
        self.receiver = receiver
        self.subject = subject
        self.body = body
        self.username = username
        self.transport_type = transport_type
    
    def __str__(self):
        return ''.join( ['From:', str(self.sender),',To:',str(self.receiver),',Subject:',str(self.subject),',Body:',str(self.body)])

class MessageResponse:
    def __init__(self, text, respondall=False):
        self.respondall = respondall
        self.text = text

