import re,redis,datetime
from time import sleep
from icalendar import Calendar,Event
from threading import Thread
import httplib2
from uniblab_message import MessageResponse
from pytz import timezone

prod2_errors_pattern = re.compile("^\[(prod-.*@ftci[^\]]*)\]\[\{severe=(.*)\}]")
error_query_pattern = re.compile("^How many errors in prod today\??", re.I)
debug_ignore_sender = True

class ProdErrorsCounter:
    def __init__(self, uniblab):
        self.uniblab = uniblab

    def message(self, m, uniblab):
        if m.subject == None:
            print 'Got email with no subject'
            return
        prod2_errors = prod2_errors_pattern.search(str(m.subject))
        if prod2_errors:
            if (m.sender.count('nucleus_error') > 0) or debug_ignore_sender:
                now = str(datetime.date.today())
                uniblab.redis_client.hincrby('proderrors:'+now, prod2_errors.group(1), int(prod2_errors.group(2)))

class HowManyProdErrors:
    def __init__(self, uniblab):
        self.uniblab = uniblab

    def get_commands(self):
        return {'How many errors in prod today?' : 'Respond with the number of severe log entries for each server in prod today' }

    def message(self, m, uniblab):
        if m.subject == None:
            return
        error_query = error_query_pattern.match(m.subject)
        if(error_query):
            now = str(datetime.date.today())
            error_counts = uniblab.redis_client.hgetall('proderrors:'+now)
            response = 'Prod error counts:\n'
            response += '\n'.join(machine+' has had '+count+' errors today' for (machine,count) in error_counts.items())
            print 'Returning prod error counts:', response
            return MessageResponse(response, True)
