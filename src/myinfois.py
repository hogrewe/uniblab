import re,redis,datetime
from uniblab_message import MessageResponse

setmyinfo_pattern = re.compile("^Uniblab[ ]*:[ ]*My *(.*) (?:is|are) (.*)", re.I)
unsetmyinfo_pattern = re.compile("^Uniblab[ ]*:[ ]*Unset my (.*)", re.I)

class SetMyInfo:
    def __init__(self, uniblab):
        self.uniblab = uniblab

    def get_commands(self):
        return {'Uniblab: My foo is bar' : 'Sets the value of your user property foo to bar'}

    def message(self, m, uniblab):
        if m.subject == None:
            print 'Got email with no subject'
            return
        mymatch = setmyinfo_pattern.search(str(m.subject))
        if mymatch:
            if m.username:
                userinfo = { mymatch.group(1) : mymatch.group(2) }
                uniblab.set_userinfo(m.username, userinfo)
                print 'Setting userinfo for', m.username, ' info:', userinfo
    def status(self, s, uniblab):
        if s.username:
            if s.subject:
                uniblab.set_userinfo(s.username, { 'status': s.subject })
            else:
                uniblab.unset_userinfo(s.username, 'status')
            

class UnsetMyInfo:
    def __init__(self, uniblab):
        self.uniblab = uniblab

    def get_commands(self):
        return {'Uniblab: Unset my foo' : 'Unsets the value of your user property foo'}

    def message(self, m, uniblab):
        if m.subject == None:
            print 'Got email with no subject'
            return
        mymatch = unsetmyinfo_pattern.search(str(m.subject))
        if mymatch:
            if m.username:
                propname = mymatch.group(1)
                if propname and propname != 'email':
                    uniblab.unset_userinfo(m.username, propname)
                    print 'Unsetting userinfo for', m.username, ' property:', propname

