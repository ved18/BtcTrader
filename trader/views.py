from decimal import Context
from django.shortcuts import render
from login.models import DB
from .models import Client
from django.apps import apps
transaction = apps.get_model('transactions', 'Transaction')
# Create your views here.



def transactionHistoryView(request,id):
    context = {
        "id" : ""
    }
    context["id"] = str(id)
    return render(request, 'traderTransactionHistory.html',context)

def viewClients(request,id):
    context = {
        "id" : ""
        "st"
    }
    context["id"] = str(id)
    # st = transaction.objects.values('clientid').filter(traderid=id, slug=clientid)
    test_ids = list(transaction.objects.values('clientid').filter(traderid=id).values_list('clientid', flat=True))
    context["st"]=Client.objects.filter(id__in=test_ids)
    return render(request, 'viewClients.html',context)

def buySellView(request):
    context = {

    }
    return render(request, 'buySell.html', context)
