from decimal import Context
from django.shortcuts import render
from login.models import DB
# Create your views here.



def transactionHistoryView(request,id):
    context = {
        "id" : ""
    }
    context["id"] = str(id)
    return render(request, 'traderTransactionHistory.html',context)

def buySellView(request):
    context = {

    }
    return render(request, 'buySell.html', context)
