# -*- coding: utf-8 -*-


from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django.utils import simplejson
from multiprocessing import Process, Queue
from sendMessages import do_send
from datetime import datetime

import pickle

def index(request):
    c = {}
    c.update(csrf(request))
    
    #html_template = open('static/templates/index.html','r')
    return render_to_response("index.html",c)

'''def send(request):
    
    queue = Queue()
    
    for data in ACCOUNTS :
        email = data
        password = ACCOUNTS[data]
        queue.put(do_send(email, password))
        
    for i in enumerate(ACCOUNTS) :
        task = Process(target=queue.get())
        task.start()
        
    return HttpResponse("OK!")'''

def add_message(request):
    
    _date = datetime.today()
    _date = _date.strftime('%y-%m-%d %H:%M:%S')
    
    try :
        messages = open("static/text/messages.pkl", "rb")
        title = request.REQUEST['title']
        body = request.REQUEST['body']
        
        index = pickle.load(messages)
        messages.close()
        
        if title and body :

            messages = open("static/text/messages.pkl", "wb")
            message = {"title":title, "body":body, "date":_date}
            index['all'].append(message)
            pickle.dump(index, messages)
            messages.close()
            
    except IOError:
        messages = open("static/text/messages.pkl", "wb")
        index = {'all':[]}
        pickle.dump(index, messages)
        messages.close()
        
        title = request.REQUEST['title']
        body = request.REQUEST['body']

        if title and body :

            messages = open("static/text/messages.pkl", "wb")
            message = {"title":title, "body":body, "date":_date}
            index['all'].append(message)
            pickle.dump(index, messages)
            messages.close()
    
    return HttpResponseRedirect("/index/")

def show_messages(request):
    
    file = open("static/text/messages.pkl", "rb")
    messages = pickle.load(file)
    
    file.close()
    
    return HttpResponse(simplejson.dumps(messages))

def add_account(request):
    
    try :
        accounts = open("static/text/accounts.pkl", "rb")
        email = str(request.REQUEST['acc_email'])
        password = str(request.REQUEST['acc_pass'])
        
        index = pickle.load(accounts)
        accounts.close()
        
        if email and password :

            accounts = open("static/text/accounts.pkl", "wb")
            id = len(index['all']) + 1
            account = {"email":email, "pass":password}
            index['all'][id] = account
            pickle.dump(index, accounts)
            accounts.close()
            
    except IOError:
        accounts = open("static/text/accounts.pkl", "wb")
        index = {'all':{}}
        pickle.dump(index, accounts)
        accounts.close()
        
        email = str(request.REQUEST['acc_email'])
        password = str(request.REQUEST['acc_pass'])
        id = len(index['all']) + 1

        if email and password :

            accounts = open("static/text/accounts.pkl", "wb")
            id = len(index['all']) + 1
            account = {"email":email, "pass":password}
            
            index['all'][id] = account
            pickle.dump(index, accounts)
            accounts.close()  
    
    return HttpResponseRedirect("/index/")

def show_accounts(request):
    
    file = open("static/text/accounts.pkl", "rb")
    accounts = pickle.load(file)
    
    file.close()
    
    return HttpResponse(simplejson.dumps(accounts))

def add_account_group(request):
    
    try :
        groups = open("static/text/groups.pkl", "rb")
    except IOError:
        groups = open("static/text/groups.pkl", "wb")
        group = request.REQUST['name']
        pickle.dump(group, groups)
        groups.close()
    
    return HttpResponseRedirect("/index/")