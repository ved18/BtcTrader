from decimal import Context
from django.shortcuts import render
from login.models import DB
# Create your views here.



def transactionHistoryView(request):

    details = {
        "transactionId" : 0,
        "clientId":0,
        "transactiontype":"",
        "totalamount":0,
        "bitcoin" : 0,
        "commissionType" : "",
        "comissionAmount" : "",
        "date" : "",
        "status" : "",
    }
    context = {
        "id" : -1,
        "details" : [],
    }
    id = request.session.get('userId')
    db = DB()

    selectQuery = "select tid, clientId, ordertype, totalAmount, btcAmount, commissionType, commissionAmount, date, status from transaction where  traderId= " + str(id) + ";"
    errorMsg = "could not find transactions"

    row = db.select(selectQuery, errorMsg)
    if row:
        context["details"] = row

    context["id"] = str(id)

    return render(request, 'traderTransactionHistory.html', context)
