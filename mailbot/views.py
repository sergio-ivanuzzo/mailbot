# -*- coding: utf-8 -*-

from django.http import HttpResponse

import urllib, pycurl, cStringIO, re, time, lxml.html

# for output cURL result
data = cStringIO.StringIO()

# OPTIONS

URL_AUTH = 'https://m.facebook.com/login.php'
URL_MAIN_PAGE = 'https://m.facebook.com/home.php'
URL_NEXT = 'https://facebook.com/friends'
URL_SEND_MSG = 'https://m.facebook.com/messages/send'

EMAIL = ['obsidian.inf@gmail.com', 'sergio.ivanuzzo@gmail.com', '@gmail.com']
PASSWORD = ['facebookPASS235', 'facebookPASS234', '']

account_number = 1

AUTHDATA = {
        'email': EMAIL[account_number],
        'pass':PASSWORD[account_number],
        }

USERAGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'

# param, which use in private message sending
FB_DTSG = ['AQB5FnCU', 'AQAoKq39', 'AQBqnU8M']
token = FB_DTSG[account_number]

PROXY = ['190.96.64.234:8080', '78.129.233.67:3128', '213.141.236.133:8090']
proxy = PROXY[2]

msg = u'тестовое сообщение, не отвечайте (test message, do not reply)'

COOKIES = 'mailbot/cookie.ini'

def index(request):
    
    html_template = open('mailbot/templates/index.html','r')
    page = get_page(URL_NEXT)
    #test = get_url_from_page(account_page, '<a.*accesskey=[\'"]?1[\'"]?.*href=[\'"]?([^\'">]+)[\'"]?')
    friends = get_friends_from(page)
    #send_msg_to(friends)
    
    return HttpResponse(html_template.read().format(info=friends))

def do_login():

    curl(url = URL_AUTH, postdata = AUTHDATA, proxy = None, method = 'post')
    
def get_page(url):
    
    do_login()
    curl(url, postdata = None, proxy = None)

    return data.getvalue()

def get_friends_from(html):
    
    friends_ids = list()
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

def send_msg_to(friends):

    friends = str(friends)[1:-1]    
    MSG = {'body':msg, 'ids['+friends+']':friends, 'fb_dtsg':token, 'send':'Ответить'}
    
    curl(url = URL_SEND_MSG, postdata = MSG, proxy = None, method = 'post')

def curl(url, postdata = None, proxy = None, method = None):
    
    curl = pycurl.Curl()
    
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.FOLLOWLOCATION, 1)
    curl.setopt(pycurl.SSL_VERIFYPEER, 0)
    
    if method :
        curl.setopt(pycurl.POST, 1)
    else :
        curl.setopt(pycurl.POST, 0)
        
    curl.setopt(pycurl.COOKIEJAR, COOKIES)
    curl.setopt(pycurl.COOKIEFILE, COOKIES)
    curl.setopt(pycurl.USERAGENT, USERAGENT)
    curl.setopt(pycurl.HEADER, 0)
    curl.setopt(pycurl.VERBOSE, 0)
    
    if postdata :
        curl.setopt(pycurl.POSTFIELDS, urllib.urlencode(postdata))
    
    if proxy :
        curl.setopt(pycurl.PROXY, proxy)
        curl.setopt(pycurl.CONNECTTIMEOUT, 15)
        curl.setopt(pycurl.TIMEOUT, 18)    
        
    curl.setopt(pycurl.WRITEFUNCTION, data.write)
    
    curl.perform()
    curl.close()
       