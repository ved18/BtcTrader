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
    updateQuery = "update login set password='" + newPassword + "' where id=" + id + ";"
    errorMsg = "could not update password"

    db = DB()
    row = db.insertOrUpdateOrDelete(updateQuery, errorMsg)
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
    }

    if request.POST.get("editProfileSubmit"):
        newPassword = str(request.get("newPassword"))
        confirmPassword = str(request.get("confirmPassword"))
        if(newPassword == confirmPassword):
            updateProfile(newPassword, id)
    
    selectQuery = "select firstName, lastName, phoneNumber from client where id =" + str(id) + ";"
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
    context["id"] = str(id)

    return render(request, 'editProfile.html', context)

#view for transaction history
def transactionHistoryView(request, id):
    context = {
        "id" : "",
    }
    context["id"] = str(id)
    return render(request, 'transactionHistory.html', context)
