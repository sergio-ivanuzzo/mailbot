# -*- coding: utf-8 -*-

from django.http import HttpResponse
from lxml import etree
from multiprocessing import Process, Queue

import urllib, pycurl, cStringIO, re, time, pickle

# for output cURL result
data = cStringIO.StringIO()

# OPTIONS

URL_FB = 'https://m.facebook.com'
URL_AUTH = 'https://m.facebook.com/login.php'
URL_HOME = 'https://m.facebook.com/home.php'
URL_FRIENDS = 'https://m.facebook.com/PLACEHOLDERv=friends&refid=17'
URL_SEND_MSG = 'https://m.facebook.com/messages/send/'

USERAGENT = 'Opera/12.02 (Android 4.1; Linux; Opera Mobi/ADR-1111101157; U; en-US) Presto/2.9.201 Version/12.02'

def do_send(data):
    
    email, password, message, proxy, cookies = data
    proxy = None
    do_login(URL_AUTH, email, password, cookies)
    account_page = get_page(URL_HOME, proxy, cookies)

    # token for sending messages
    token = get_token_from(account_page)

    if token :
        profile_page = get_url_from(account_page, xpath="//div[@id='viewport']/div[1]/span/div[1]/span[2]/a")
        
        if profile_page :
            # "/profile.php?id=xxxxxxxxxx&" or /xxxxxxxxx?
            page_alias = get_page_alias(profile_page)
            # replace PLACEHOLDER with url to friends page
            url_friends = re.sub('PLACEHOLDER',page_alias,URL_FRIENDS)
            
            friends_page = get_page(url_friends, proxy, cookies)
            #friends_count = get_friends_count(friends_page)
            
            all_friends = get_all_friends_from(friends_page, proxy, cookies)
            send_msg(all_friends, token, message, proxy, cookies)

    #html_template = open('mailbot/templates/index.html','r')
    #return HttpResponse(html_template.read().format(info=profile_page))#friends))

def do_login(url, email, password, cookies):
    
    authdata = {'email':email, 'pass':password}
    curl(url=url, postdata=authdata, proxy=None, method='post', write_cookies=cookies)
    
def get_page(url, proxy, cookies):
    
    page = curl(url, postdata=None, proxy=proxy, method=None, write_cookies=None, read_cookies=cookies)
    return page

def get_token_from(html):
    
    parser = etree.HTMLParser()
    tree = etree.parse(cStringIO.StringIO(html), parser)
    token = tree.xpath("//*[@id='composer_form']/input[@name='fb_dtsg']")
    if token :
        return token[0].attrib['value']
    else :
        return False
    
def get_friends_count(html):
    
    parser = etree.HTMLParser()
    tree = etree.parse(cStringIO.StringIO(html), parser)
    friends_count = tree.xpath('//*[@class="_i3g"]/div[1]/h4')
    if friends_count :
        return friends_count[0].text
    else :
        return False

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
    url = tree.xpath(xpath)
    if url :    
        return url[0].attrib['href']
    else :
        return False

def get_all_friends_from(html, proxy, cookies):
    
    def get_friends(html, friends):
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
                
        return friends
    
    # This method return link to next friends page, if it exists
    def get_more_friends(html):
        parser = parser = etree.HTMLParser()
        tree = etree.parse(cStringIO.StringIO(html), parser)
        more_friends = tree.xpath("//*[@id='m_more_friends']/a")
        
        return more_friends
    
    all_friends = []
    friends = get_friends(html, all_friends)
    more_friends = get_more_friends(html)
    
    while more_friends :
        friends_page = get_page(URL_FB+more_friends[0].attrib['href'], proxy, cookies)
        friends = get_friends(friends_page, all_friends)
        more_friends = get_more_friends(friends_page)

    return friends
    
def send_msg(friends, token, message, proxy, cookies):
    
    file = open("static/text/messages.pkl", "rb")
    messages = pickle.load(file)
    file.close()
    
    for m in messages['all'] :
        if m['title'] == message:
            msg = m['body'].decode('utf-8')   
            
    data = {'body':msg, 'fb_dtsg':token, 'send':'Ответить'}         
    for friend in friends :
        data['ids['+friend+']'] = friend
        
    curl(url=URL_SEND_MSG, postdata=data, proxy=proxy, method='post', write_cookies=None, read_cookies=cookies)
    
def curl(url, postdata=None, proxy=None, method=None, write_cookies=None, read_cookies=None):
    
    curl = pycurl.Curl()
    
    # for output cURL result
    data = cStringIO.StringIO()

    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.FOLLOWLOCATION, 1)
    curl.setopt(pycurl.SSL_VERIFYPEER, 0)
    curl.setopt(pycurl.SSL_VERIFYHOST, 0)
        
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
    curl.setopt(pycurl.NOSIGNAL, 1)
    
    if postdata :
        curl.setopt(pycurl.POSTFIELDS, urllib.urlencode(postdata))
    
    if proxy :
        proxy_addr = proxy[:proxy.find(":")]
        proxy_port = int(proxy[proxy.find(":")+1:])
        
        #print proxy_addr, proxy_port
        
        curl.setopt(pycurl.PROXY, proxy_addr)
        curl.setopt(pycurl.PROXYPORT, proxy_port)
        curl.setopt(pycurl.HTTPPROXYTUNNEL, 1)
            
    curl.setopt(pycurl.TIMEOUT, 18)
    curl.setopt(pycurl.WRITEFUNCTION, data.write)
    
    curl.perform()
    curl.close()
    
    return data.getvalue()