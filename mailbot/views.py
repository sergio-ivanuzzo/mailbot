# -*- coding: utf-8 -*-

from django.http import HttpResponse

import urllib, pycurl, cStringIO, re, time

# for output cURL result
data = cStringIO.StringIO()

# OPTIONS

URL_AUTH = 'https://m.facebook.com/login.php'
URL_NEXT = 'https://facebook.com/friends'
URL_SEND_MSG = 'https://m.facebook.com/messages/send'

EMAIL = ['obsidian.inf@gmail.com', 'sergio.ivanuzzo@gmail.com', 'xspectr@gmail.com']
PASSWORD = ['facebookPASS235', 'facebookPASS234', 'facebookPASS237']

account_number = 2

AUTHDATA = {
        'email': EMAIL[account_number],
        'pass':PASSWORD[account_number],
        }

USERAGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'

# param, which use in private message sending
FB_DTSG = ['AQB5FnCU', 'AQAoKq39', 'AQBqnU8M']
fb_dtsg = FB_DTSG[account_number]

PROXY = ['190.96.64.234:8080', '78.129.233.67:3128', '213.141.236.133:8090']
proxy = PROXY[2]

msg = 'тестовое сообщение, не отвечайте (test message, do not reply)'

COOKIES = 'mailbot/cookie.ini'

def index(request):
    
    html_template = open('mailbot/templates/index.html','r')
    
    account_page = get_page()
    friends = get_friends_from(account_page)
    
    send_msg_to(msg, friends)
    
    return HttpResponse(html_template.read().format(info=friends))

def do_login():
    
    curl = pycurl.Curl()
    
    curl.setopt(pycurl.URL, URL_AUTH)
    curl.setopt(pycurl.FOLLOWLOCATION, 1)
    curl.setopt(pycurl.POST, 1)
    curl.setopt(pycurl.COOKIEJAR, COOKIES)
    curl.setopt(pycurl.USERAGENT, USERAGENT)
    curl.setopt(pycurl.HEADER, 1)
    """curl.setopt(pycurl.PROXY, PROXY)
    curl.setopt(pycurl.CONNECTTIMEOUT, 15)
    curl.setopt(pycurl.TIMEOUT, 18)"""
    curl.setopt(pycurl.POSTFIELDS, urllib.urlencode(AUTHDATA))
    curl.setopt(pycurl.VERBOSE, 1)
    
    curl.perform()
    curl.close()
    
def get_page():
    
    do_login()
    curl = pycurl.Curl()
    
    curl.setopt(pycurl.URL, URL_NEXT)
    curl.setopt(pycurl.FOLLOWLOCATION, 1)
    curl.setopt(pycurl.POST, 0)
    curl.setopt(pycurl.COOKIEFILE, COOKIES)
    curl.setopt(pycurl.SSL_VERIFYPEER, 0)
    curl.setopt(pycurl.USERAGENT, USERAGENT)
    """curl.setopt(pycurl.PROXY, proxy)
    curl.setopt(pycurl.CONNECTTIMEOUT, 15)
    curl.setopt(pycurl.TIMEOUT, 18)"""
    curl.setopt(pycurl.VERBOSE, 1)
    curl.setopt(pycurl.WRITEFUNCTION, data.write)
    
    curl.perform()
    curl.close()

    return data.getvalue()

def get_friends_from(html):
    
    friends_ids = []
    # find links to friends pages by special class
    links = re.findall(r'class=[\'"]?[^<>]*lfloat[^<>]+[\'"]?[^<>]* href=[\'"]?(http[^>\'"]*)[\'"]?', html)
    
    for link in links:
        # if address have "id" param 
        if re.search(r'profile.php[?]{1}id=', link):
            friend_id = re.search(r'id=([^?&]+)', link)
            friends_ids.append(friend_id.group(1))
        else :
            # if there are alias instead of id, visiting graph.facebook.com for getting id
            id_from = re.sub(r'www', 'graph', link)
            id_from = urllib.urlopen(id_from)
            get_id = id_from.read()
            
            friend_id = re.search(r'id[":\s"]+([^"]+)', get_id)
            friends_ids.append(friend_id.group(1))
            
    return friends_ids

def send_msg_to(msg, friends):
    
    curl = pycurl.Curl()

    for friend in friends:
        
        MSG = {'body':msg, 'ids['+friend+']':friend, 'fb_dtsg':fb_dtsg, 'send':'Ответить'}
        
        curl.setopt(pycurl.URL, URL_SEND_MSG)
        curl.setopt(pycurl.FOLLOWLOCATION, 1)
        curl.setopt(pycurl.POST, 0)
        curl.setopt(pycurl.COOKIEFILE, COOKIES)
        curl.setopt(pycurl.SSL_VERIFYPEER, 0)
        curl.setopt(pycurl.USERAGENT, USERAGENT)
        """curl.setopt(pycurl.PROXY, proxy)
        curl.setopt(pycurl.CONNECTTIMEOUT, 15)
        curl.setopt(pycurl.TIMEOUT, 18)"""
        curl.setopt(pycurl.VERBOSE, 1)
        curl.setopt(pycurl.POSTFIELDS, urllib.urlencode(MSG))
    
        curl.perform()
        # making 1 second delay, cause we're not spammers
        time.sleep(1)

    curl.close()