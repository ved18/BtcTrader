from decimal import Context
from django.shortcuts import render
from login.models import DB
# Create your views here.



def transactionHistoryView(request, id):
    context = {
        "id" : "",
        "details" : [],
    }

    
    db = DB()

    selectQuery = "select tid, ordertype, totalAmount, btcAmount, commissionType, commissionAmount, date, status from transaction where  traderId= "+ str(id) +";"
    errorMsg = "could not find transactions"

    row = db.select(selectQuery, errorMsg)
    transactionInfo = []
    if row:
        for i in row:
            temp = {}
            temp["transactionId"] = i[0]
            temp["commissionType"] = i[1]
            temp["amount"] = i[2]
            temp["comissionAmount"]= i[3]
            temp["orderType"] = i[4]
            temp["date"] = i[5]
            temp["bitcoin"] = i[6]
            temp["rate"] = i[7]

            transactionInfo.append(temp)
    context["details"] = transactionInfo
    context["id"] = str(id)
    return render(request, 'traderTransactionHistory.html', context)

def buySellView(request):
    context = {

    }
    return render(request, 'buySell.html', context)
