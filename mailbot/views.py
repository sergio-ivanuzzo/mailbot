# -*- coding: utf-8 -*-

from django.http import HttpResponse
from multiprocessing import Process, Queue
from sendMessages import do_send

ACCOUNTS = {'@gmail.com':'', '':''}

def index(request):
    queue = Queue()
    
    for data in ACCOUNTS :
        email = data
        password = ACCOUNTS[data]
        queue.put(do_send(email, password))
        
    for i in enumerate(ACCOUNTS) :
        task = Process(target=queue.get())
        task.start()

    return HttpResponse()