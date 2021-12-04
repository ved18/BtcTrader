from django.contrib.auth import login
from django.db import connection
from django.shortcuts import redirect, render
from django.template import context
from login.models import DB
import requests
# Create your views here.

def homeView(request):
    context = {
        "firstName":"",
        "btcAmount":"",
        "accountBalance":"",
        "investmentAmount":"",
        "netgainloss":"",
        "t1":0,
        "t2":0,
        "ans":"",
    }

    # if(request.session.get('loggedIn') == False):
    #     return redirect('login')
    id = request.session.get('userId')
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

    selectTypeQuery = "select btcAmount, accountBalance from wallet where userId=(%s)"
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
    selectUsername = "select username from users where id="+ str(id) +";"
    errorMsg = "could not find Username"

    db = DB()
    row = db.select(selectUsername,errorMsg)

    if row[0][0] == newusername:
        return True
    return False

#function to check if user has sufficient balance
def verifyBalance(enteredfiat,id):
    selectBalance = "select accountBalance from wallet where userId="+ str(id) +";"
    errorMsg = "could not find Username"

    db = DB()
    row = db.select(selectBalance,errorMsg)

    if row[0][0]>=enteredfiat:
        return True
    return False

#function to update wallet after buy operation
def updatewallet(finalbitcoins,enteredfiat,newusername, updateWalletUserId):
    selectId = "select id from users where username='"+ newusername +"';"
    errorMsg = "could not find Id"

    db = DB()
    row = db.select(selectId,errorMsg)
    userId = row[0][0]

    if userId != updateWalletUserId:
        updateQuery = "update wallet set accountBalance=accountBalance-"+str(enteredfiat)+" where userId=" + str(updateWalletUserId) + ";"
        updateClientBtc = "update wallet set btcAmount=btcAmount+"+str(finalbitcoins)+" where userId=" + str(userId) + ";"
        errorMsg = "cannot update clients wallet for trader transaction"
        row = db.insertOrUpdateOrDelete(updateClientBtc, errorMsg)
    else:
        updateQuery = "update wallet set btcAmount=btcAmount+"+str(finalbitcoins)+",accountBalance=accountBalance-"+str(enteredfiat)+" where userId=" + str(updateWalletUserId) + ";"
    
    errorMsg = "could not update wallet"
    row = db.insertOrUpdateOrDelete(updateQuery, errorMsg)
    if row:
        return userId
    return False

#function for adding transactions in db table
def addtransaction(context,id,commtype,enteredfiat,commamount,buttontype,finalbitcoins,btcrate, userId):

    db = DB()

    selectType = "select type from login where id="+ str(id) +";"
    errorMsg = "could not find user type"

    row = db.select(selectType,errorMsg)
    context["type"] = row[0][0]

    selectWallet = "select id from wallet where userId="+ str(id) +";"
    errorMsg = "could not find wallet id"

    row = db.select(selectWallet,errorMsg)
    walletId = row[0][0]

    if context["type"] == "client":

        insertQuery = "Insert into transaction(clientId, traderId,  commissionType, totalAmount, commissionAmount, orderType, status, date, btcAmount, btcRate, walletId) values(" + str(id) + ", NULL, '"+ commtype + "', " + str(enteredfiat) + ", "+ str(commamount) + ",'"+ buttontype +"','success',2021,'"+ str(finalbitcoins) +"','"+ str(btcrate) +"','"+ str(walletId) +"');"
        errorMsg = "could not add transaction"

        row = db.insertOrUpdateOrDelete(insertQuery, errorMsg)   
        if row:
            return True
        return False

    elif context["type"] == "trader":

        insertQuery = "Insert into transaction(clientId, traderId,  commissionType, totalAmount, commissionAmount, orderType, status, date, btcAmount, btcRate, walletId) values(" + str(userId) + ", " + str(id) + ", '"+ commtype + "', " + str(enteredfiat) + ", "+ str(commamount) + ",'"+ buttontype +"','success',2021,'"+ str(finalbitcoins) +"','"+ str(btcrate) +"','"+ str(walletId) +"');"
        errorMsg = "could not add transaction"

        row = db.insertOrUpdateOrDelete(insertQuery, errorMsg)   
        if row:
            return True
        return False

def editProfileView(request):
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
    


#view for transaction history
def transactionHistoryView(request):
    

    context = {
        "id" : -1,
        "details" : [],
    }

    id = request.session.get('userId')
    db = DB()

    selectQuery = "select tid, ordertype, totalAmount, btcAmount, commissionType, commissionAmount, date, status from transaction where  clientId= "+ str(id) +" && traderId is NULL" ";"
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
    context["id"] = id
    return render(request, 'transactionHistory.html', context)

#view for transaction history
def transactionHistoryByTraderView(request):
    
    details = {
        "transactionId" : 0,
        "traderId":0,
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

    selectQuery = "select tid, traderId, ordertype, totalAmount, btcAmount, commissionType, commission, date, status from transaction where  clientId= "+ str(id) +" && trandeId is Not Null" ";"
    errorMsg = "could not find transactions"

    row = db.select(selectQuery, errorMsg)
    if row:
        context["details"] = row

    context["id"] = id
    return render(request, 'transactionHistory.html', context)

#view for buy tab
def buyView(request):
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
        "balanceverified" : False,
        "userType" : "client",
        "transactionadded" : False,
    }
    id = request.session.get('userId')
    context["id"] = id
    response = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
    btcRateJson = response.json()
    currentBtcRate = btcRateJson['bpi']['USD']['rate_float']
    context['btcrate'] = currentBtcRate
    #find user type
    selectUserType = "select type from login where id=" + str(id) + ";"
    errorMsg = "cannot find user type in buyview"

    row = db.select(selectUserType, errorMsg)
    if row:
        context["userType"] = row[0][0]

    selectUserCommType = "select type from client where id=" + str(id) + ";"
    errorMsg = "Could not find users commission type"

    commType = db.select(selectUserCommType, errorMsg)
    if commType:
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

    selectAccountBalance = "select accountBalance from wallet where userId=" + str(id) + ";"
    errorMsg = "Could not find accountBalance"

    accountBlance = db.select(selectAccountBalance, errorMsg)
    if accountBlance:
        context["accountbalance"] = accountBlance[0][0]

    if request.POST.get("buysubmit"):
        context["click"] = True

        newusername = str(request.POST.get("username"))
        enteredfiat = float(request.POST.get("fiatamt"))
        commtype = str(request.POST.get("btcfiat"))
        buttontype = str(request.POST.get("buysubmit"))
        
        #find clientID for whom to buy bitcoins
        selectId = "select id from users where username='"+ newusername +"';"
        errorMsg = "could not find Id"

        db = DB()
        row = db.select(selectId,errorMsg)
        if row:
            userId = row[0][0]

        #find commission rate for the user of trader
        selectUserCommType = "select type from client where id=" + str(userId) + ";"
        errorMsg = "Could not find users commission type"

        commType = db.select(selectUserCommType, errorMsg)
        if commType:
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
                    if addtransaction(context,id,commtype,enteredfiat,commamount,buttontype,finalbitcoins,btcrate, userId):
                        context["transactionadded"] = True

                        updateQuery = "update metadata set totalBtc=totalBtc-"+str(finalbitcoins)+", totalCurrency=totalCurrency+"+str(enteredfiat)+";"
                        errorMsg = "could not update metadata"
                        db = DB()
                        db.insertOrUpdateOrDelete(updateQuery, errorMsg)
                           
    return render(request, 'buy.html', context)


#view for sell tab
def sellView(request):
    context = {
        "id" : -1,
        "verification" : False,
        "btcCap" : False,
        "userType" : "",
        "btcRate" : -1,
        "btcAmount" : 0
    }
    id = request.session.get('userId')
    context["id"] = id
    
    response = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
    btcRateJson = response.json()
    currentBtcRate = btcRateJson['bpi']['USD']['rate_float']
    context['btcRate'] = currentBtcRate
    db = DB()
    #find user type
    selectUserType = "select type from login where id=" + str(id) + ";"
    errorMsg = "cannot find user type in buyview"

    row = db.select(selectUserType, errorMsg)
    if row:
        context["userType"] = row[0][0]
    if request.POST.get("sellSubmit"):
        username = str(request.POST.get("userName"))
        sellBitcoins = float(request.POST.get("bitcoins"))
        commType = request.POST.get("btcfiat")

        #query to get id of client
        selectQuery = "select id from users where username='" + username + "';"
        errorMsg = "couldnt find user"

        row = db.select(selectQuery, errorMsg)
        if row:
            clientId = row[0][0]
        else:
            context["verification"] = False
            return render(request, 'transactionHistory.html', context)

        #query to check bitcoins in users wallet
        selectQuery = "select id, btcAmount from wallet where userId= " + str(clientId) + ";"
        errorMsg = "could not fetch number bitcoins from wallet"
        row = db.select(selectQuery, errorMsg)
        if row:
            walletId = row[0][0]
            totalBitcoins = row[0][1]
            context["btcAmount"] = totalBitcoins
        else:
            context["verification"] = False
            return render(request, 'transactionHistory.html', context)

        if totalBitcoins < sellBitcoins:
            context["btcCap"] = True
            return render(request, 'transactionHistory.html', context)

        #calculate remaining btc to update user wallet and also update bank wallet
        updateBtcUser = totalBitcoins - sellBitcoins
        currentRate = 10

        #get rate of user depending on type
        selectTypeQuery = "select type from client where id=" + str(clientId) + ";"
        errorMsg = "could not find type from client in sellView"

        row = db.select(selectTypeQuery, errorMsg)
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
        updateBtcWalletQuery = "update wallet set btcAmount=" + str(updateBtcUser) + "where userId=" + str(clientId) + ";"
        errorMsg = "could not update client wallet after sell"

        row = db.insertOrUpdateOrDelete(updateBtcWalletQuery, errorMsg)

        updateWalletFiatQuery = "update wallet set accountBalance=accountBalance+" + str(metaCurrency) + " where userId=" + str(clientId) + ";"
        errorMsg = "could not update user wallet for amount"

        row = db.insertOrUpdateOrDelete(updateWalletFiatQuery, errorMsg)
        
        #add to transaction
        addtransaction(context, id, commType, totalAmount, commissionAmount, "sell", sellBitcoins, currentBtcRate, clientId)

        #add to metadata
        updateMetaQuery = "Update metadata set totalBtc=totalBtc +" + str(sellBitcoins) + ", totalCurrency=totalCurrency-" + str(metaCurrency) + ";" 
        errorMsg = "cannot update metadata"
        row = db.select(updateMetaQuery, errorMsg)

    return render(request, 'sell.html', context)

#view for wallet tab
def walletView(request):
    db = DB()
    context = {
        "fiatbalance" : "",
        "btcbalance" : "",
        "type" : ""
    }
    id = request.session.get('userId')
    context["id"] = id

    #check the user type
    selectUserType = "select type from login where id=" + str(id) + ";"
    errorMsg = "cannot find user type in buyview"

    row = db.select(selectUserType, errorMsg)
    if row:
        context["type"] = row[0][0]

    selectAccountBalance = "select btcAmount, accountBalance from wallet where userId=" + str(id) + ";"
    errorMsg = "Could not find accountBalance"

    accountBlance = db.select(selectAccountBalance, errorMsg)
    if accountBlance:
        context["btcbalance"] = accountBlance[0][0]
        context["fiatbalance"] = accountBlance[0][1]

    return render(request, 'wallet.html', context)