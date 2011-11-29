import re
from uniblab_message import MessageResponse

whatcanyoudo_pattern = re.compile("^uniblab[ ]*:[ ]*what can you do\??", re.I)

class WhatCanYouDo:
    def __init__(self, uniblab):
        self.uniblab = uniblab

    def get_commands(self):
        return {'Uniblab: what can you do' : 'Returns the commands uniblab knows about'}

    def message(self, m, uniblab):
        if m.subject == None:
            return
        whatcanyoudo = whatcanyoudo_pattern.match(m.subject)
        response = 'Uniblab commands:\n'
        if(whatcanyoudo):
            all_commands = list()
            for p in self.uniblab.plugins:
                if hasattr(p, 'get_commands'):
                    for command,description in p.get_commands().items():
                        print command, description
                        all_commands.append('{0:<30} : {1}'.format(command, description))

            response += '\n'.join(all_commands)

            return MessageResponse(response, True)

