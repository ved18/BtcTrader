from decimal import Context
from django.http import request
from django.shortcuts import render
from login.models import DB
from .models import Client
from django.apps import apps
transaction = apps.get_model('transactions', 'Transaction')
# Create your views here.




def transactionHistoryView(request):
    st=transaction.objects.filter(traderid=request.session.get("userId"))
    return render(request, 'traderTransactionHistory.html',{"st":st})

def viewTransaction(request,tid):
    id=int(tid)
    print(request.session.get("tid"))
    st=transaction.objects.filter(traderid=request.session.get("userId"),tid=id)
    return render(request,"singleTransaction.html",{"st":st})


def viewClients(request):
    context = {
        "st" : ''
    }
    id = request.session.get('userId')
    # st = transaction.objects.values('clientid').filter(traderid=id, slug=clientid)
    test_ids = list(transaction.objects.values('clientid').filter(traderid=id).values_list('clientid', flat=True))
    context["st"]=Client.objects.filter(id__in=test_ids)
    return render(request, 'viewClients.html',context)

