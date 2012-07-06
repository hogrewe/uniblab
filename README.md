Overview
========
Uniblab is a simple bot.  The actions he can perform, as well as the transports he listens on, are pluggable. Currently this is configured in code, which is not optimal.  The configuration is in uniblab.py for both.

Configuration
=============
The configuration for each plugin is in one file called `.uniblab.cfg` which should reside in the directory from which you start uniblab.

The file generally looks like this:

    [email]
    imap_host=mail.example.com
    imap_port=993
    user=uniblab
    pass=uniblab
    smtp_host=mail.example.com
    smtp_port=587
    mail_from=uniblab@example.com
    email_address=Uniblab <uniblab@example.com>
    
    [irc]
    channels=uniblabtalk
    host=irc.example.com
    port=6667
    nickname=uniblab
    
    [wiki]
    user=uniblab
    pass=uniblab
    ooo_url=http://example.com/ical
    
    [xmpp]
    xmpp_user=uniblab@example.com/uniblab
    xmpp_pass=uniblab
    xmpp_host=jabber.example.com
    xmpp_port=5223


