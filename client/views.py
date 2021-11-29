from django.shortcuts import render
from django.template import context
from login.models import DB
# Create your views here.

def homeView(request, id):
    context = {
        "id" : "",
    }

    context["id"] = id
    return render(request, 'homePage.html', context)

# update password for the user
def updateProfile(newPassword, id):
    updateQuery = "update login set password='" + newPassword + "' where id=" + str(id) + ";"
    errorMsg = "could not update password"

    db = DB()
    row = db.insertOrUpdateOrDelete(updateQuery, errorMsg)
    if row:
        return True
    return False

#function to verify old password for editing
def verifyPassword(oldPassword, id):
    selectPassword = "select password from login where id=" + str(id) +";"
    errorMsg = "could not find old password"

    db = DB()
    row = db.select(selectPassword, errorMsg)

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

def editProfileView(request, id):
    db = DB()
    context = {
        "firstName" : "",
        "lastName" : "",
        "phoneNumber" : "",
        "email" : "",
        "id" : "",
        "click" : False,
        "changed" : False,
        "type" : "client",
    }

    context["id"] = str(id)

    selectTypeQuery = "select type from login where id=" + str(id) +";"
    errorMsg = "could not select type"

    row = db.select(selectTypeQuery, errorMsg)
    
    if row:
        context["type"] = row[0][0]

    if request.POST.get("epSubmit"):
        context["click"] = True
        newPassword = str(request.POST.get("newPassword"))
        confirmPassword = str(request.POST.get("confirmPassword"))
        oldPassword = str(request.POST.get("oldPassword"))
        if verifyPassword(oldPassword, id):
            if(newPassword == confirmPassword):
                if updateProfile(newPassword, id):
                    context["changed"] = True
                    if context["type"] == "trader":
                        return render(request, 'traderTransactionHistory.html', context)


    selectQuery = "select firstName, lastName, phoneNumber from " + context["type"] + " where id =" + str(id) + ";"
    errorMsg = "Could not find the particular user in edit profile"
    clientRow = db.select(selectQuery, errorMsg)

    if clientRow:
        context["firstName"] = clientRow[0][0]
        context["lastName"] = clientRow[0][1]
        context["phoneNumber"] = clientRow[0][2]

    
    selectEmail = "select username from users where id=" + str(id) + ";"
    emailRow = db.select(selectEmail, errorMsg)
    
    if emailRow:
        context["email"] = emailRow[0][0]
    
    return render(request, 'editProfile.html', context)
    


#view for transaction history
def transactionHistoryView(request, id):
    context = {
        "id" : "",
    }
    context["id"] = str(id)
    return render(request, 'transactionHistory.html', context)

#view for buy tab
def buyView(request, id):
    db = DB()
    context = {
        "accountbalance" : "",
        "click" : False,
        "nameverified" : False,
        "balanceverified" : False,
        "btcrate" : 10,
        "commtype" : "",
        "commrate" : "",
        "updatedwallet" : False,
        "balanceverified" : False,
        "userType" : "client",
        "transactionadded" : False,
    }
    context["id"] = str(id)
    
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
        btcrate = float(context["btcrate"])
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
def sellView(request, id):
    context = {
        "id" : "",
    }
    context["id"] = str(id)
    return render(request, 'sell.html', context)

#view for wallet tab
def walletView(request, id):
    db = DB()
    context = {
        "fiatbalance" : "",
        "btcbalance" : "",
    }
    context["id"] = str(id)

    selectAccountBalance = "select btcAmount, accountBalance from wallet where userId=" + str(id) + ";"
    errorMsg = "Could not find accountBalance"

    accountBlance = db.select(selectAccountBalance, errorMsg)
    if accountBlance:
        context["btcbalance"] = accountBlance[0][0]
        context["fiatbalance"] = accountBlance[0][1]

    return render(request, 'wallet.html', context)




