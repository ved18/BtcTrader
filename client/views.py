from django.db import connection
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
    context = {
        "id" : "",
        "verification" : True,
    }
    context["id"] = str(id)
    return render(request, 'buy.html', context)

#view for sell tab
def sellView(request, id):
    context = {
        "id" : "",
        "verification" : False,
        "btcCap" : False,
    }
    context["id"] = str(id)
    db = DB()

    if request.POST.get("sellSubmit"):
        username = request.POST.get("userName")
        sellBitcoins = request.POST.get("bitcoins")
        balance = request.POST.get("balance")
        commType = request.POST.get("btcFiat")

        #query to get id of user i.e. either user or trader
        selectQuery = "select id from users where username='" + username + "';"
        errorMsg = "couldnt find user"

        row = db.select(selectQuery, errorMsg)
        if row:
            userid = row[0][0]
        else:
            context["verification"] = False
            return render(request, 'transactionHistory.html', context)

        #query to check bitcoins in users wallet
        selectQuery = "select btcAmount from wallet where userId= " + userid + ";"
        errorMsg = "could not fetch number bitcoins from wallet"

        row = db.select(selectQuery, errorMsg)
        if row:
            totalBitcoins = row[0][0]
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
        selectTypeQuery = "select type from client where id=" + id + ";"
        errorMsg = "could not find type from client in sellView"

        row = db.select(selectTypeQuery, errorMsg)
        if row:
            userCategory = row[0][0]

        if userCategory == "silver":
            getRateQuery = "select commissionSilver from metada;"
        else:
            getRateQuery = "select commissionGold from metadata;"

        errorMsg = "cannot get the rate from metadata"

        row = db.select(getRateQuery, errorMsg)
        if row:
            commissionRate = row[0][0]
        
        #need to update bitcoin rate here from coindesk api
        currentBtcRate = 10
        totalAmount = sellBitcoins * currentBtcRate
        commissionAmount = totalAmount * (commissionRate/100)
        metaCurrency = totalAmount - commissionAmount
        #total amount obtained after selling bitcoin

        #update user wallet
        #add to transaction
        #add to metadata
        updateMetaQuery = "Update metadata set totalBtc=totalBtc +" + sellBitcoins + ", totalCurrency=totalCurrency-" + metaCurrency + ";" 
        errorMsg = "cannot update metadata"
        row = db.select(updateMetaQuery, errorMsg)


        if row:
            return render(request, 'transactionHistory.html', context)
    return render(request, 'sell.html', context)

