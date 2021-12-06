from django.contrib.auth import login
from django.db import connection
from django.shortcuts import redirect, render
from django.template import context
from login.models import DB
from datetime import datetime
import requests
# Create your views here.

def homeView(request):
    if(request.session.has_key('userId')):
        context = {
            "firstName":"",
            "btcAmount":"",
            "accountBalance":"",
            "investmentAmount":"",
            "netgainloss":"",
            "t1":0,
            "t2":0,
            "ans":"",
            "userType":""}

    # if(request.session.get('loggedIn') == False):
    #     return redirect('login')
        id = request.session.get('userId')
        context["userType"] = request.session.get('userType')
        db = DB()
        context["id"] = id
        selectUsername = "select firstName from client where id=(%s)"
        errorMsg = "could not select required values"
        param = (id,)
        clientRowUsername =db.selectPrepared(selectUsername, param, errorMsg)
        if clientRowUsername:
            context["firstName"]=clientRowUsername[0][0]

        selectInvestment = "select investmentAmount from portfolio where id=(%s)"
        errorMsg = "could not select required values"
        param = (id,)
        clientRowInv=db.selectPrepared(selectInvestment,param, errorMsg)
        if clientRowInv:
            context["investmentAmount"]=clientRowInv[0][0]

        selectTypeQuery = "select btcAmount, accountBalance from wallet where id=(%s)"
        errorMsg = "could not select required values"
        param = (id,)
        clientRow = db.selectPrepared(selectTypeQuery, param, errorMsg)
        if clientRow:
            context["btcAmount"] = clientRow[0][0]
            context["accountBalance"] = clientRow[0][1]
    

        resQuery="select totalBtc from portfolio where id=(%s)"
        param = (id,)
        errorMsg = "could not fetch total bitcoins homeview"
        clientRow1 = db.selectPrepared(resQuery, param, errorMsg)
        if clientRow1:
            context["t1"] = clientRow1[0][0]
    
        selectInvestment="select investmentAmount from portfolio where id=(%s)"
        param = (id,)
        clientRow2 = db.selectPrepared(selectInvestment, param, errorMsg)
        if clientRow2:
            context["t2"] = clientRow2[0][0]
    
        currentRate=10
        #assuming the currentRate value for the bitcoin as 10.
        ans=currentRate*(context["t1"])-(context["t2"])
        if(ans>0):
            context["ans"]="Profit "+str(ans)
        else:
            context["ans"]="Loss "+str(ans)

        return render(request, 'homePage.html', context)
    else:
        return redirect("/")



# update password for the user
def updateProfile(userType, firstName, lastName, phoneNumber, newPassword, id):
    
    db = DB()
    if userType == 'client':
        updateQuery = "update client set firstName=(%s), lastName=(%s), phoneNumber=(%s) where id=(%s)"
    else:
        updateQuery = "update trader set firstName=(%s), lastName=(%s), phoneNumber=(%s) where id=(%s)"
        
    params = (firstName, lastName, phoneNumber, id)
    errorMsg = "could not edit profile details"

    row1 = db.insertPrepared(updateQuery, params, errorMsg)

    updateQuery = "update login set password=(%s) where id=(%s)"
    errorMsg = "could not update password"
    params = (newPassword, id)

    row2 = db.insertPrepared(updateQuery, params, errorMsg)
    if row1 and row2:
        return True
    return False

#function to verify old password for editing
def verifyPassword(oldPassword, id):
    selectPassword = "select password from login where id=(%s)"
    errorMsg = "could not find old password"
    param = (id,)

    db = DB()
    row = db.selectPrepared(selectPassword, param, errorMsg)

    if row[0][0] == oldPassword:
        return True
    return False

#function to verify Username while buying
def verifyUsername(newusername,id):
    selectUsername = "select username from users where id=(%s)"
    errorMsg = "could not find Username"

    params = (id,)
    db = DB()
    row = db.selectPrepared(selectUsername,params,errorMsg)

    if row[0][0] == newusername:
        return True
    return False

#function to check if user has sufficient balance
def verifyBalance(enteredfiat,id):
    selectBalance = "select accountBalance from wallet where id=(%s)"
    errorMsg = "could not find Username"

    params = (id,)
    db = DB()
    row = db.selectPrepared(selectBalance,params,errorMsg)

    if row[0][0]>=enteredfiat:
        return True
    return False

#function to update wallet after buy operation
def updatewallet(finalbitcoins,enteredfiat,newusername, updateWalletUserId):
    selectId = "select id from users where username=(%s)"
    errorMsg = "could not find Id"
    params = (newusername,)
    db = DB()
    row = db.selectPrepared(selectId,params,errorMsg)
    userId = row[0][0]

    if str(userId) != updateWalletUserId:
        updateClientBtc = "update wallet set btcAmount=btcAmount+(%s) where id=(%s)"
        updateQuery = "update wallet set accountBalance=accountBalance-(%s) where id=(%s)"
        errorMsg = "cannot update clients wallet for trader transaction"
        params1 = (finalbitcoins,userId,)
        params2 = (enteredfiat,updateWalletUserId,)
        row = db.insertPrepared(updateClientBtc,params1,errorMsg)
    else:
        updateQuery = "update wallet set btcAmount=btcAmount+(%s),accountBalance=accountBalance-(%s) where id=(%s)"
        params2 = (finalbitcoins,enteredfiat,updateWalletUserId,)
    
    errorMsg = "could not update wallet"
    row = db.insertPrepared(updateQuery,params2,errorMsg)
    if row:
        return userId
    return False

#function for adding transactions in db table
def addtransaction(context,id,commtype,enteredfiat,commamount,buttontype,finalbitcoins,btcrate, userId):

    db = DB()

    selectWallet = "select id from wallet where id=(%s)"
    errorMsg = "could not find wallet id"
    params = (id,)
    row = db.selectPrepared(selectWallet,params,errorMsg)
    walletId = row[0][0]
    status="Success"
    now = datetime.now()

    if context["userType"]== "client":

        insertQuery = "Insert into transaction(clientId, traderId,  commissionType, totalAmount, commissionAmount, orderType, status, date, btcAmount, btcRate, walletId) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        errorMsg = "could not add transaction"
        tradertype = None
        params = (id,tradertype,commtype,enteredfiat,commamount,buttontype,status,now,finalbitcoins,btcrate,walletId)
        row = db.insertPrepared(insertQuery,params, errorMsg)   
        if row:
            return True
        return False

    elif context["userType"]== "trader":

        insertQuery = "Insert into transaction(clientId, traderId,  commissionType, totalAmount, commissionAmount, orderType, status, date, btcAmount, btcRate, walletId) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        errorMsg = "could not add transaction"

        params = (userId,id,commtype,enteredfiat,commamount,buttontype,status,now,finalbitcoins,btcrate,walletId)
        row = db.insertPrepared(insertQuery,params, errorMsg)   
        if row:
            return True
        return False

def editProfileView(request):
    if(request.session.has_key('userId')):
        db = DB()
        context = {
            "firstName" : "",
            "lastName" : "",
            "phoneNumber" : "",
            "email" : "",
            "id" : -1,
            "click" : False,
            "changed" : False,
            "type" : "client",
        }

        id = request.session.get('userId')
        userType = request.session.get('userType')
        context['id'] = id
        context["type"] = userType

        if request.POST.get("epSubmit"):
            context["click"] = True
            newPassword = str(request.POST.get("newPassword"))
            confirmPassword = str(request.POST.get("confirmPassword"))
            oldPassword = str(request.POST.get("oldPassword"))
            firstName = str(request.POST.get("firstName"))
            lastName = str(request.POST.get("lastName"))
            phoneNumber = str(request.POST.get("phoneNumber"))
            if verifyPassword(oldPassword, id):
                if(newPassword == confirmPassword):
                    if updateProfile(userType, firstName, lastName, phoneNumber, newPassword, id):
                        context["changed"] = True
                        if context["type"] == "trader":
                            return render(request, 'traderTransactionHistory.html', context)


        if userType == 'client':
            selectQuery = "select firstName, lastName, phoneNumber from client where id = (%s)"
        else:
            selectQuery = "select firstName, lastName, phoneNumber from trader where id = (%s)"
        errorMsg = "Could not find the particular user in edit profile"
        params = (id,)
        clientRow = db.selectPrepared(selectQuery, params, errorMsg)

        if clientRow:
            context["firstName"] = clientRow[0][0]
            context["lastName"] = clientRow[0][1]
            context["phoneNumber"] = clientRow[0][2]

    
        selectEmail = "select username from users where id = (%s)"
        param = (id,)
        emailRow = db.selectPrepared(selectEmail, param, errorMsg)
    
        if emailRow:
            context["email"] = emailRow[0][0]
    
        return render(request, 'editProfile.html', context)
    else:
        return redirect("/")
    


#view for transaction history

def transactionHistoryView(request):
    if(request.session.has_key('userId')):
        return render(request, 'transactionHistory.html')
    else:
        return redirect("/")


#view for transaction history
def transactionHistoryByTraderView(request):
    return render(request, 'transactionHistory.html')


#view for buy tab
def buyView(request):
    if(request.session.has_key('userId') == None):
        return redirect('/')
    db = DB()
    context = {
        "accountbalance" : "",
        "click" : False,
        "nameverified" : False,
        "balanceverified" : False,
        "btcrate" : -1,
        "commtype" : "",
        "commrate" : "",
        "updatedwallet" : False,
        "commissionverified" : False,
        "userType" : "client",
        "transactionadded" : False,
    }

    id = request.session.get('userId')
    context["id"] = id

    userType = request.session.get('userType')
    context["userType"]= userType
    response = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
    btcRateJson = response.json()
    currentBtcRate = btcRateJson['bpi']['USD']['rate_float']
    context['btcrate'] = currentBtcRate


    selectAccountBalance = "select accountBalance from wallet where id= (%s)"
    errorMsg = "Could not find accountBalance"

    params = (id,)
    accountBlance = db.selectPrepared(selectAccountBalance,params, errorMsg)
    if accountBlance:
        context["accountbalance"] = accountBlance[0][0]

    if request.POST.get("buysubmit"):
        context["click"] = True

        newusername = str(request.POST.get("username"))
        enteredfiat = float(request.POST.get("fiatamt"))
        commtype = str(request.POST.get("btcfiat"))
        buttontype = str(request.POST.get("buysubmit"))
        
        #find clientID for whom to buy bitcoins
        selectId = "select id from users where username=(%s)"
        errorMsg = "could not find Id"

        db = DB()
        params = (newusername,)
        row = db.selectPrepared(selectId,params,errorMsg)
        if row:
            userId = row[0][0]
        else:
            context["nameverified"] = False
            return render(request, 'buy.html', context)

        
        #find commission rate for the user of trader
        selectUserCommType = "select type from client where id=(%s)"
        errorMsg = "Could not find users commission type"

        params = (userId,)
        commType = db.selectPrepared(selectUserCommType,params, errorMsg)
        if commType:
            context["commissionverified"] = True
            context["commtype"] = commType[0][0]

            if context["commtype"] == "silver":
                selectUserCommRate = "select commissionSilver from metadata;"
                errorMsg = "Could not find users commission rate"

                commRate = db.select(selectUserCommRate, errorMsg)
                if commRate:
                    context["commrate"] = commRate[0][0]

            elif context["commtype"] == "gold":
                selectUserCommRate = "select commissionGold from metadata;"
                errorMsg = "Could not find users commission rate"

                commRate = db.select(selectUserCommRate, errorMsg)
                if commRate:
                    context["commrate"] = commRate[0][0]

            commrate = float(context["commrate"])
            btcrate = currentBtcRate
            finalbitcoins = 0.0

            if verifyUsername(newusername, userId):
                context["nameverified"] = True
                if verifyBalance(enteredfiat,id):
                    context["balanceverified"] = True

                    if commtype == "fiat":
                        finalbitcoins = (enteredfiat*(1-(commrate)/100))/btcrate
                    elif commtype == "bitcoin":
                        finalbitcoins = (enteredfiat*(1-(commrate)/100))/btcrate

                    commamount = (enteredfiat*commrate)/100
                    userId = updatewallet(finalbitcoins,enteredfiat,newusername, id)
                    if userId:
                        context["updatedwallet"] = True
                        selectAccountBalance = "select accountBalance from wallet where id=(%s)"
                        errorMsg = "Could not find accountBalance"
                        params = (id,)
                        accountBlance = db.selectPrepared(selectAccountBalance,params,errorMsg)

                        if accountBlance:
                            context["accountbalance"] = accountBlance[0][0]
                        if addtransaction(context,id,commtype,enteredfiat,commamount,buttontype,finalbitcoins,btcrate, userId):
                            context["transactionadded"] = True

                            updateQuery = "update metadata set totalBtc=totalBtc-(%s), totalCurrency=totalCurrency+(%s)"
                            errorMsg = "could not update metadata"
                            db = DB()
                            params = (finalbitcoins,enteredfiat,)
                            db.insertPrepared(updateQuery,params, errorMsg)
        else:
            return render(request, 'buy.html', context)
                           
    return render(request, 'buy.html', context)

#view for sell tab
def sellView(request):
    if(request.session.has_key('userId')==None):
        return redirect("/")
    context = {
        "id" : -1,
        "verification" : True,
        "btcCap" : False,
        "userType" : "",
        "btcRate" : -1,
        "btcAmount" : 0,
        "click" : False
    }
    id = request.session.get('userId')
    context["id"] = id
    response = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
    btcRateJson = response.json()
    currentBtcRate = btcRateJson['bpi']['USD']['rate_float']
    context['btcRate'] = currentBtcRate
    db = DB()
    userType = request.session.get('userType')
    context["userType"]= userType

    selectAccountBtc = "select btcAmount from wallet where id= (%s)"
    errorMsg = "Could not find accountBalance"

    params = (id,)
    accountBlance = db.selectPrepared(selectAccountBtc,params, errorMsg)
    if accountBlance:
        context["btcAmount"] = accountBlance[0][0]

    if request.POST.get("sellSubmit"):
        context["click"] = True
        username = str(request.POST.get("userName"))
        sellBitcoins = float(request.POST.get("bitcoins"))
        commType = request.POST.get("btcfiat")

        #query to get id of client
        selectQuery = "select id from users where username=(%s)"
        errorMsg = "couldnt find user"

        params = (username,)
        row = db.selectPrepared(selectQuery,params, errorMsg)
        if row:
            clientId = row[0][0]
        else:
            context["verification"] = False
            return render(request, 'sell.html', context)

        #query to check bitcoins in users wallet
        selectQuery = "select id, btcAmount from wallet where id= (%s)"
        errorMsg = "could not fetch number bitcoins from wallet"
        params = (clientId,)
        row = db.selectPrepared(selectQuery,params, errorMsg)
        if row:
            walletId = row[0][0]
            totalBitcoins = row[0][1]
            context["btcAmount"] = totalBitcoins
        else:
            context["verification"] = False
            return render(request, 'sell.html', context)

        if totalBitcoins < sellBitcoins:
            context["btcCap"] = True
            return render(request, 'sell.html', context)

        #calculate remaining btc to update user wallet and also update bank wallet
        updateBtcUser = totalBitcoins - sellBitcoins
        currentRate = 10

        #get rate of user depending on type
        selectTypeQuery = "select type from client where id=(%s)"
        errorMsg = "could not find type from client in sellView"

        params = (clientId,)
        row = db.selectPrepared(selectTypeQuery,params, errorMsg)
        if row:
            userCategory = row[0][0]

        if userCategory == "silver":
            getRateQuery = "select commissionSilver from metadata;"
        else:
            getRateQuery = "select commissionGold from metadata;"

        errorMsg = "cannot get the rate from metadata"

        row = db.select(getRateQuery, errorMsg)
        if row:
            commissionRate = row[0][0]
        
        #need to update bitcoin rate here from coindesk api
        totalAmount = sellBitcoins * currentBtcRate
        commissionAmount = totalAmount * (commissionRate/100)
        metaCurrency = totalAmount - commissionAmount
        #total amount obtained after selling bitcoin

        #update user wallet
        updateBtcWalletQuery = "update wallet set btcAmount=(%s) where id=(%s)"
        errorMsg = "could not update client wallet after sell"

        params = (updateBtcUser,clientId,)
        row = db.insertPrepared(updateBtcWalletQuery,params, errorMsg)

        updateWalletFiatQuery = "update wallet set accountBalance=accountBalance+(%s) where id=(%s)"
        errorMsg = "could not update user wallet for amount"

        params = (metaCurrency,clientId,)
        row = db.insertPrepared(updateWalletFiatQuery,params, errorMsg)
        
            #add to transaction
        addtransaction(context, id, commType, totalAmount, commissionAmount, "sell", sellBitcoins, currentBtcRate, clientId)

        #add to metadata
        updateMetaQuery = "Update metadata set totalBtc=totalBtc +(%s), totalCurrency=totalCurrency-(%s)" 
        errorMsg = "cannot update metadata"
        params = (sellBitcoins,metaCurrency,)
        row = db.selectPrepared(updateMetaQuery,params, errorMsg)

        selectAccountBtc = "select btcAmount from wallet where id= (%s)"
        errorMsg = "Could not find accountBalance"

        params = (id,)
        accountBlance = db.selectPrepared(selectAccountBtc,params, errorMsg)
        if accountBlance:
          context["btcAmount"] = accountBlance[0][0]

    return render(request, 'sell.html', context)

#view for wallet tab
def walletView(request):
    if(request.session.has_key('userId')==None):
        return redirect("/")
    db = DB()
    context = {
        "fiatbalance" : "",
        "btcbalance" : "",
        "type" : "",
        "addedMoney" : False,
    }

    balance = request.POST.get("addamt")
    id = request.session.get('userId')
    context["id"] = id
    userType = request.session.get('userType')
    context["type"] = userType

    selectAccountBalance = "select btcAmount, accountBalance from wallet where id=(%s)"
    errorMsg = "Could not find accountBalance"

    params = (id,)
    accountBlance = db.selectPrepared(selectAccountBalance,params, errorMsg)
    if accountBlance:
        context["btcbalance"] = accountBlance[0][0]
        context["fiatbalance"] = accountBlance[0][1]

    if request.POST.get("addamount"):
        updateQuery = "update wallet set accountBalance=accountBalance+(%s) where id=(%s)"
        errorMsg = "could not update balance"
        db = DB()
        db.beginTransaction()
        params =(balance,id,)
        row1 = db.insertPrepared(updateQuery,params, errorMsg)
        if row1:
            context["addedMoney"] = True
            now = datetime.now()
            #adding to wallet transactions
            insertQuery = "Insert into walletTransactions(walletId, amount, date) values((%s),(%s),(%s))"
            params = (id, balance, now,)
            errorMsg = "cannot add into wallet history"
            row2 = db.insertPrepared(insertQuery, params, errorMsg)
            if row2:
                db.commit()
        if not (row1 and row2):
                db.rollback()
        selectAccountBalance = "select btcAmount, accountBalance from wallet where id=(%s)"
        errorMsg = "Could not find accountBalance"
        params = (id,)
        accountBlance = db.selectPrepared(selectAccountBalance,params, errorMsg)
        if accountBlance:
            context["btcbalance"] = accountBlance[0][0]
            context["fiatbalance"] = accountBlance[0][1]

    return render(request, 'wallet.html', context)

def searchTraderView(request):
    context = {
        "dict":[],
        "type" : "",
        "type" : "client",
        "click" : False,
        "id":"",
        "first":"",
        "last":"",
        "phone":"",
        "cell":"",
        "state":"",
        "city":"",
        "foundrec": False,
    }

    if request.POST.get("searchtrader"):
        context["click"] = True
        name = str(request.POST.get("name"))
        option = str(request.POST.get("dropdownoption"))


        db=DB()
        if option=="id":
            selectName = "select id,firstName,lastName,state,city,phoneNumber,cellNumber from trader where id=(%s)"
            errorMsg = "Could not find trader"
            params = (name,)

        elif option=="firstName":
            selectName = "select id,firstName,lastName,state,city,phoneNumber,cellNumber from trader where firstName=(%s)"
            errorMsg = "Could not find trader"
            params = (name,)

        elif option=="state":
            selectName = "select id,firstName,lastName,state,city,phoneNumber,cellNumber from trader where state=(%s)"
            errorMsg = "Could not find trader"
            params = (name,)

        elif option=="city":
            selectName = "select id,firstName,lastName,state,city,phoneNumber,cellNumber from trader where city=(%s)"
            errorMsg = "Could not find trader"
            params = (name,)

        
        traderdetails = db.selectPrepared(selectName,params, errorMsg)

        searchDetails = []
        if traderdetails:
            context["foundrec"] = True
            for i in traderdetails:
                temp={}
                temp["id"] = i[0]
                temp["first"] = i[1]
                temp["last"] = i[2]
                temp["state"] = i[3]
                temp["city"] = i[4]
                temp["phone"] = i[5]
                temp["cell"] = i[6]
                searchDetails.append(temp)

        context["dict"] = searchDetails

    return render(request, 'searchTrader.html', context)

