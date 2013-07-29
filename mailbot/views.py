# -*- coding: utf-8 -*-

from django.http import HttpResponse
from lxml import etree

import urllib, pycurl, cStringIO, re, time

# for output cURL result
data = cStringIO.StringIO()

# OPTIONS

URL_FB = 'https://m.facebook.com'
URL_AUTH = 'https://m.facebook.com/login.php'
URL_HOME = 'https://m.facebook.com/home.php'
URL_FRIENDS = 'https://m.facebook.com/PLACEHOLDERv=friends&refid=17'
URL_SEND_MSG = 'https://m.facebook.com/messages/send/'

EMAIL = ['@gmail.com', '@gmail.com', '@gmail.com']
PASSWORD = ['', '', '']

account_number = 2

AUTHDATA = {
        'email': EMAIL[account_number],
        'pass':PASSWORD[account_number],
        }

USERAGENT = 'Opera/12.02 (Android 4.1; Linux; Opera Mobi/ADR-1111101157; U; en-US) Presto/2.9.201 Version/12.02'

PROXY = ['190.96.64.234:8080', '78.129.233.67:3128', '213.141.236.133:8090']
proxy = PROXY[2]

msg = 'посоветуй, пожалуста, фильм интересный. желательно из жанра фэнтези/фантастика. спасибо заранее!'

COOKIES = 'mailbot/cookie.ini'

def index(request):
    
    html_template = open('mailbot/templates/index.html','r')
    
    do_login(URL_AUTH)
    account_page = get_page(URL_HOME)
    # token for sending messages
    token = get_token_from(account_page)
    
    profile_page = get_url_from(account_page, xpath="//*[@id='viewport']/div[1]span/div[1]/span[2]/a")
    
    # "/profile.php?id=xxxxxxxxxx&" or /xxxxxxxxx?
    page_alias = get_page_alias(profile_page)
    
    url_friends = re.sub('PLACEHOLDER',page_alias,URL_FRIENDS)
    friends_page = get_page(url_friends)
    
    options = {'html':friends_page, 'token': token}
    
    send_msg_to_friends(options)

    return HttpResponse(html_template.read().format(info='OK'))#friends))

def do_login(url):

    curl(url=URL_AUTH, postdata=AUTHDATA, proxy=None, method='post', write_cookies=COOKIES)
    
def get_page(url):
    
    page = curl(url, postdata=None, proxy=None, method=None, write_cookies=None, read_cookies=COOKIES)
    return page

def get_token_from(html):
    
    parser = etree.HTMLParser()
    tree = etree.parse(cStringIO.StringIO(html), parser)
    token = tree.find("//*[@id='composer_form']/input[1]").attrib['value']
    
    return token

def get_page_alias(url):
    # result will be like "/profile.php?id=000000&" or like "/nickname?"
    # result will be replace with PLACEHOLDER (see URL_FRIENDS) 
    if re.search(r'profile.php[?]{1}id=', url):
        alias = re.search('\/([^&]*[?&]?)', url)
        alias = alias.group(1)
    else :
        alias = re.search('\/([^?&]*[?&]?)', url)
        alias = alias.group(1)
        
    return alias

def get_url_from(html, xpath):
    
    parser = parser = etree.HTMLParser()
    tree = etree.parse(cStringIO.StringIO(html), parser)
    url = tree.find(xpath).attrib['href']
    
    return url

def send_msg_to_friends(options):
    
    html = options['html'] # friends page
    token = options['token'] # use for sending messages
    
    friends = []
    
    parser = parser = etree.HTMLParser()
    tree = etree.parse(cStringIO.StringIO(html), parser)
    
    links = tree.xpath("//*[@href and contains(@href, 'fref')]")
        
    for link in links:

        # if address have "id" param 
        if re.search(r'profile.php[?]{1}id=', link.attrib['href']):
            friend_id = re.search(r'id=([^?&]+)', link.attrib['href'])
            friends.append(friend_id.group(1))
        else :
            # if there are alias instead of id, visiting graph.facebook.com for getting id
            id_from = urllib.urlopen('https://graph.facebook.com'+link.attrib['href'])
            get_id = id_from.read()
            
            friend_id = re.search(r'id[":\s"]+([^"]+)', get_id)
            friends.append(friend_id.group(1))
    
    # friends type is list, so after making string from it we must delete "[" and "]"
    #friends = str(friends)[1:-1]
    for friend in friends :  
        MSG = {'body':msg, 'ids['+friend+']':friend, 'fb_dtsg':token, 'send':'Ответить'}
        curl(url=URL_SEND_MSG, postdata=MSG, proxy=None, method='post', write_cookies=None, read_cookies=COOKIES)
    #return MSG
    #time.sleep(2)
    more_friends = tree.xpath("//*[@id='m_more_friends']/a")
    
    if more_friends :
        friends_page = get_page(URL_FB+more_friends[0].attrib['href'])
        options = {'html':friends_page, 'token': token}
        send_msg_to_friends(options)
    else :
        return True

    
def curl(url, postdata=None, proxy=None, method=None, write_cookies=None, read_cookies=None):
    
    curl = pycurl.Curl()
    
    # for output cURL result
    data = cStringIO.StringIO()

    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.FOLLOWLOCATION, 1)
    curl.setopt(pycurl.SSL_VERIFYPEER, 0)
    
    if method :
        curl.setopt(pycurl.POST, 1)
    else :
        curl.setopt(pycurl.POST, 0)
    
    if write_cookies :
        curl.setopt(pycurl.COOKIEJAR, write_cookies)
    if read_cookies :
        curl.setopt(pycurl.COOKIEFILE, read_cookies)
        
    curl.setopt(pycurl.USERAGENT, USERAGENT)
    curl.setopt(pycurl.HEADER, 1)
    curl.setopt(pycurl.VERBOSE, 1)
    
    if postdata :
        curl.setopt(pycurl.POSTFIELDS, urllib.urlencode(postdata))
    
    if proxy :
        curl.setopt(pycurl.PROXY, proxy)
        curl.setopt(pycurl.CONNECTTIMEOUT, 15)
        curl.setopt(pycurl.TIMEOUT, 18)    
        
    curl.setopt(pycurl.WRITEFUNCTION, data.write)
    
    curl.perform()
    curl.close()
    
    return data.getvalue()