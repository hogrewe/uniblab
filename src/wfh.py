import re,redis,datetime
from icalendar import Calendar,Event
import httplib2
from uniblab_message import MessageResponse
from twisted.internet import task
from pytz import timezone

wfh_pattern = re.compile("^(WF.*)|(Working from.*)|(OOO.*)", re.I)
iswfh_pattern = re.compile("where[ ]*is ([^?]*)\?*", re.I)
localtz = timezone('US/Mountain')

class WFH:
    def __init__(self, uniblab):
        self.uniblab = uniblab

    def get_commands(self):
        return {'WFXXX' : 'Sets your work status to the subject',
                'Working from xxx' : 'Sets your work status to the subject',
                'OOO' : 'Sets your work status to the subject'}

    def message(self, m, uniblab):
        if m.subject == None:
            print 'Got email with no subject'
            return
        if(wfh_pattern.search(str(m.subject))):
            if m.username:
                uniblab.set_workstatus(m.username, m.subject)
                print m.username,'is',m.subject
            else:
                username = uniblab.create_user_from_email(m.sender)
                if username:
                    uniblab.set_workstatus(username, m.subject)
                    print username,'is',m.subject


class IsWFH:
    def __init__(self, uniblab):
        self.uniblab = uniblab
        self.defaultstatus = 'in the office'

    def get_commands(self):
        return {'Where is xxx' : 'Replies with the work status of the user xxx (or all users if xxx is everyone)'}

    def message(self, m, uniblab):
        if m.subject == None:
            return
        iswfh = iswfh_pattern.match(m.subject)
        if(iswfh):
            inquiry = iswfh.group(1)
            if inquiry.lower() == "everyone".lower():
                statuses = list()
                for user in uniblab.get_allusers():
                    userstatus = uniblab.get_workstatus(user)
                    statuses.append(' '.join([user,'is',userstatus or self.defaultstatus]))

                response = '\n'.join(statuses)
            else:
                user = inquiry
                userstatus = uniblab.get_workstatus(user)
                response = ' '.join([user,'is',userstatus or self.defaultstatus])
            print 'Question of:', m.subject, 'looking for status of', inquiry, 'Responding with',response
            return MessageResponse(response, True)


class WorkStatusReset:
    def __init__(self, uniblab):
        self.uniblab = uniblab

    def config(self, config):
        self.wiki_user = config.get('wiki', 'user')
        self.wiki_pass = config.get('wiki', 'pass')
        self.wiki_ooo_url = config.get('wiki', 'ooo_url')
    
    def start(self):
        l = task.LoopingCall(self.reset_workstatus)
        l.start(60*60*1, True)

    def reset_workstatus(self):
        # Remove work status if it's a new day.  This should be in the WFH plugin somehow
        statusdate = self.uniblab.redis_client.get('workstatus:date')
        now = str(datetime.date.today())
        if statusdate != now:
            print 'Resetting status for new date' , now
            ooo_emails = self.get_ooo_people()
            ooo_users = set()
            for user_email in ooo_emails:
                ooo_username = self.uniblab.username_from_email(user_email)
                ooo_users.add(ooo_username)
                print ooo_username,'is OOO'
                self.uniblab.set_workstatus(ooo_username, 'Out of Office')
            for user in self.uniblab.get_allusers():
                if user not in ooo_users:
                    self.uniblab.redis_client.hdel(':'.join(['users',user]), 'workstatus')
            self.uniblab.redis_client.set('workstatus:date', now)

        
    def get_ooo_people(self):
        h = httplib2.Http()
        h.add_credentials(self.wiki_user, self.wiki_pass)
        res,icalstring = h.request(self.wiki_ooo_url)
        # Something funky going on in that ical
        icalstring = re.sub('TZOFFSETFROM:-065956', 'TZOFFSETFROM:-0600', icalstring)
        cal = Calendar.from_string(icalstring)
        ooo_emails = list()
        now = datetime.date.today()
        print 'Looking for vacations on', now
        for s in cal.walk('VEVENT'):
            ooo_startdate = s.decoded('DTSTART')
            if type(ooo_startdate) == datetime.datetime:
                ooo_startdate = ooo_startdate.date()

            ooo_enddate = s.decoded('DTEND')
            if type(ooo_enddate) == datetime.datetime:
                ooo_enddate = ooo_enddate.date()

    
            if now >= ooo_startdate and now < ooo_enddate:
                print 'someone is ooo today:',s
                ooo_org = s.decoded('ORGANIZER', default='UNKNOWN')
                ooo_match = re.match('(mailto:)*(.*)', ooo_org)
                if ooo_org != 'UNKNOWN' and ooo_match :
                    ooo_email = ooo_match.group(2)
                    ooo_emails.append(ooo_email)
    
        return ooo_emails
