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
        retVal = cancel(id,remarks)
        if retVal:
            return redirect('traderTransaction')
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
        orderType = row[0][6].lower()
        btcAmt = row[0][9]
        walletId = row[0][11]

        if orderType=="buy":
            db.beginTransaction()
            #Update Fiat in wallet
            updateQuery = "update wallet set accountBalance = accountBalance+(%s) where id=(%s)"
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
                    param=(tid,now,remarks)
                    row = db.insertPrepared(updateQuery,param,errorMsg)
                    if row:
                        #update transaction status
                        updateQuery = "update transaction set status='cancelled' where tid=(%s)"
                        errorMsg = "couldnt update transaction status"
                        param = (tid,)
                        row = db.insertPrepared(updateQuery, param, errorMsg)
                        if row:
                            #update metadata
                            updateQuery = "update metadata set totalBtc = totalBtc + (%s), totalCurrency = totalCurrency - (%s)"
                            errorMsg = "couldnt update metadata"
                            param = (btcAmt, totalAmt)
                            db.insertPrepared(updateQuery, param, errorMsg)
                            if row:
                                db.commit()
                                return True
            db.rollback()


