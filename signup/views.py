from django.shortcuts import render
from login.models import DB

# Create your views here.

def signupView(request):
    db = DB()
    if request.POST.get("signupSubmit"):
        firstName = str(request.POST.get("firstName"))
        lastName = str(request.POST.get("lastName"))
        email = str(request.POST.get("email"))
        phoneNumber = str(request.POST.get("phoneNumber"))
        cellNumber = str(request.POST.get("cellNumber"))
        state = str(request.POST.get("state"))
        city = str(request.POST.get("city"))
        street = str(request.POST.get("street"))
        zip = str(request.POST.get("zip"))
        password = str(request.POST.get("password"))

        #inserting new user into users table
        insertEmailQuery = "Insert into users(username) values('" + email + "');"
        errorMsg = "Cannot insert user into db"        
        insertEmail = db.insertOrUpdateOrDelete(insertEmailQuery, errorMsg)

        #selecting id of user currently inserted
        selectQuery = "select id from users where username = '" + email + "';"
        tuple = (email)

        row = db.select(selectQuery, errorMsg, email)
        id = str(row[0][0])

        #insert password and client type in login table
        insertPasswordQuery = "Insert into login(id, password, type) values(" + id + ", '"+ password + "', 'client');"
        insertPassword = db.insertOrUpdateOrDelete(insertPasswordQuery, errorMsg)

        #insertClientQuery = "Insert into client values(" + id + ", '"
        if insertEmail and insertPassword:
            return render(request, 'login/login.html')
        
    return render(request, 'signup.html')
