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

def send_msg_to_group(request):
    
    accounts = open("static/text/accounts.pkl", "rb")
    index = pickle.load(accounts)
    accounts.close()
    
    result = []
    group = request.REQUEST['group']
    message = request.REQUEST['message']
    
    for acc in index['all'] :
        if index['all'][acc]['group'] == group :
            email = index['all'][acc]['email']
            password = index['all'][acc]['pass']
            result.append({"email":email, "pass":password})
    
    send(result, message)

    return HttpResponseRedirect("/index/")

def send(accounts, message):

    queue = Queue()

    for data in accounts :
        email = data['email']
        password = data['pass']
        queue.put(do_send(email, password, message))
        
    for i in enumerate(accounts) :
        task = Process(target=queue.get())
        task.start()
        
    return(len(accounts))

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

def get_messages(request):
    
    file = open("static/text/messages.pkl", "rb")
    messages = pickle.load(file)
    
    file.close()
    
    return HttpResponse(simplejson.dumps(messages))

def get_accounts(request):
    
    file = open("static/text/accounts.pkl", "rb")
    accounts = pickle.load(file)
    
    file.close()
    
    return HttpResponse(simplejson.dumps(accounts))

def get_groups(request):
    
    file = open("static/text/groups.pkl", "rb")
    groups = pickle.load(file)
    file.close()    
    
    return HttpResponse(simplejson.dumps(groups))

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

def add_account_group(request):
    
    try :
        file = open("static/text/groups.pkl", "rb")
        groups = pickle.load(file)
        file.close()
        
        file = open("static/text/groups.pkl", "wb")
        
        group = str(request.REQUEST['acc_group_name'])
        groups.append(group)
        pickle.dump(groups, file)
        
        file.close()
        
    except IOError:
        file = open("static/text/groups.pkl", "wb")
        
        groups = []
        group = str(request.REQUEST['acc_group_name'])
        groups.append(group)
        pickle.dump(groups, file)
        
        file.close()
    
    return HttpResponseRedirect("/index/")

def add_account_to_group(request):
    
    accounts = open("static/text/accounts.pkl", "rb")
    index = pickle.load(accounts)
    accounts.close()
    
    accounts = open("static/text/accounts.pkl", "wb")
    
    id = int(request.REQUEST['id'])
    group = str(request.REQUEST['group'])
    
    index['all'][id]['group'] = group
    
    pickle.dump(index, accounts)    
    accounts.close()  
    
    return HttpResponseRedirect("/index/")

def delete_account(request):
    
    accounts = open("static/text/accounts.pkl", "rb")
    index = pickle.load(accounts)
    accounts.close()
    
    id = int(request.REQUEST['id'])
    
    del index['all'][id]
    
    new_index = {'all':{}}
    counter = 1
    for i in xrange(len(index['all'])) :
        count = i + 1 
        new_index['all'][count] = ""
    
    for _id in index['all'] :
        new_index['all'][counter] = index['all'][_id]
        counter = counter + 1
    
    accounts = open("static/text/accounts.pkl", "wb")
    pickle.dump(new_index, accounts)    
    accounts.close() 
    
    return HttpResponseRedirect("/index/")  