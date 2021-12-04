from django.shortcuts import render, redirect
from .models import DB
from django.template import context
from django.contrib.auth import authenticate, login, logout
from .models import Transaction

# Create your views here.

def viewtransaction(request):
    idType = "manager"
    id = request.session.get('userId')
    if(idType=="manager"):
    	st=Transaction.objects.all()
    else:
    	if(idType=="client"):
    		st=Transaction.objects.filter(clientid=id)
    	else:
    		if(idType=="trader"):
    			st=Transaction.objects.filter(traderid=id)
    return render(request, 'transactions.html',{'st':st})