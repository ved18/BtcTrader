from django.shortcuts import render
from django.template import context
from login.models import DB
# Create your views here.

def homeView(request, id):
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
    db = DB()
    context["id"] = str(id)
    selectUsername="select firstName from client where id=" + str(id) +";"
    errorMsg = "could not select required values"
    clientRowUsername=db.select(selectUsername,errorMsg)
    if clientRowUsername:
        context["firstName"]=clientRowUsername[0][0]

    selectInvestment="select investmentAmount  from portfolio where id=" + str(id) +";"
    errorMsg = "could not select required values"
    clientRowInv=db.select(selectInvestment,errorMsg)
    if clientRowInv:
        context["investmentAmount"]=clientRowInv[0][0]

    selectTypeQuery = "select btcAmount, accountBalance from wallet where userId=" + str(id) +";"
    errorMsg = "could not select required values"
    clientRow = db.select(selectTypeQuery, errorMsg)
    if clientRow:
        context["btcAmount"] = clientRow[0][0]
        context["accountBalance"] = clientRow[0][1]
    

    resQuery="select totalBtc from portfolio where id=" + str(id) +";"
    clientRow1 = db.select(resQuery, errorMsg)
    if clientRow1:
        context["t1"] = clientRow1[0][0]
    
    selectInvestment="select investmentAmount from portfolio where id=" + str(id) +";"
    clientRow2 = db.select(selectInvestment, errorMsg)
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
    }
    context["id"] = str(id)
    return render(request, 'buy.html', context)

#view for sell tab
def sellView(request, id):
    context = {
        "id" : "",
    }
    context["id"] = str(id)
    return render(request, 'sell.html', context)

