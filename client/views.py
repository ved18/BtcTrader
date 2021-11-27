from django.shortcuts import render
import client
from login.models import DB
# Create your views here.

def homeView(request):
    return render(request, 'homePage.html')

def editProfileView(request):
    db = DB()

    context = {
        "firstName" : "",
        "lastName" : "",
        "phoneNumber" : "",
        "email" : "",
    }

    
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
    

    return render(request, 'editProfile.html', context)