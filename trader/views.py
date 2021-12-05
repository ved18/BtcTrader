from decimal import Context
from django.http import request
from django.shortcuts import redirect, render
from login.models import DB
from .models import Client
from django.apps import apps
from login.models import DB
transaction = apps.get_model('transactions', 'Transaction')
from datetime import datetime
# Create your views here.




def transactionHistoryView(request):
    context = {
        "st": '',
        "tid": ""
    }
    print(request.POST.get("remarks"))
    if(request.POST.get("remarks")):
        id = int(request.POST.get("tid"))
        remarks = request.POST.get("remarks")
        cancel(id,remarks)
    if(request.POST.get("tid")):
        context["tid"]=int(request.POST.get('tid'))
        context["st"]=transaction.objects.filter(traderid=request.session.get("userId"),tid=context["tid"])
        return render(request,"singleTransaction.html",context)
    else:
        print("nthing")
    st=transaction.objects.filter(traderid=request.session.get("userId"))
    return render(request,'traderTransactionHistory.html',{"st":st})


def viewClients(request):
    context = {
        "st" : ''
    }
    id = request.session.get('userId')
    # st = transaction.objects.values('clientid').filter(traderid=id, slug=clientid)
    test_ids = list(transaction.objects.values('clientid').filter(traderid=id).values_list('clientid', flat=True))
    context["st"]=Client.objects.filter(id__in=test_ids)
    return render(request, 'viewClients.html',context)

def cancel(id, remarks):
    tid = int(id)
    remarks = str(remarks)
    db = DB()
    selectQuery = "select * from transaction where tid=(%s)"
    errorMsg = "could not fetch transaction"
    param=(id,)
    row = db.selectPrepared(selectQuery,param,errorMsg)
    if row:
        clientId = row[0][1]
        traderId = row[0][2]
        totalAmt = row[0][4]
        commAmt = row[0][5]
        orderType = row[0][6]
        btcAmt = row[0][9]
        walletId = row[0][11]

        if orderType=="buy":
            db.beginTransaction()
            #Update Fiat in wallet
            updateQuery = "update wallet w set w.accountBalance = w.accountBalance+(%s) where id=(%s)"
            errorMsg = "could not update wallet"
            param=(totalAmt,walletId,)
            row = db.insertPrepared(updateQuery,param,errorMsg)

            if row:
                #Update BTC in metadata
                updateQuery = "update wallet w set w.btcAmount = w.btcAmount -(%s) where id=(%s)"
                errorMsg = "could not update wallet"
                param=(btcAmt,clientId,)
                row = db.insertPrepared(updateQuery,param,errorMsg)

                if row:
                    now = datetime.now()
                    print(tid, remarks,now)
                    updateQuery = "insert into cancelLogs values ((%s),(%s),(%s))"
                    errorMsg = "could not insert into logs"
                    param=(tid,remarks,now,)
                    row = db.insertPrepared(updateQuery,param,errorMsg)
                    if row:
                        db.commit()
                        return redirect(request,"/viewClients")

            db.rollback()


