from django.shortcuts import redirect, render
from login.models import DB

# Create your views here.

def signupView(request):
    db = DB()

    context = {
        "dataInserted" : False,
        "signUpClicked" : True,

    }
    
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
        usertype = str(request.POST.get("usertype"))
        #inserting new user into users table
        insertEmailQuery = "Insert into users(username) values('" + email + "');"
        errorMsg = "Cannot insert user into db"        
        insertEmail = db.insertOrUpdateOrDelete(insertEmailQuery, errorMsg)

        #selecting id of user currently inserted
        selectQuery = "select id from users where username = '" + email + "';"
        tuple = (email)

        row = db.select(selectQuery, errorMsg)
        id = str(row[0][0])

        #insert password and client type in login table
        insertPasswordQuery = "Insert into login(id, password, type) values(" + id + ", '"+ password + "', '" + usertype + "');"
        insertPassword = db.insertOrUpdateOrDelete(insertPasswordQuery, errorMsg)

        insertClientQuery = "Insert into client values(" + id + ", '"+ firstName +"', '"+ lastName +"', '"+ state +"', '"+ city +"', '"+ street +"', " + zip + ", " + phoneNumber + ", " + cellNumber + ", 'silver');"
        insertTraderQuery = "Insert into trader values(" + id + ", '"+ firstName +"', '"+ lastName +"', '"+ state +"', '"+ city +"', '"+ street +"', " + zip + ", " + phoneNumber + ", " + cellNumber + ");"
        
        if usertype == "client":
            insertClient = db.insertOrUpdateOrDelete(insertClientQuery, errorMsg)
        elif usertype == "trader":
            insertTrader = db.insertOrUpdateOrDelete(insertTraderQuery, errorMsg)

        if insertEmail and insertPassword and (insertTrader or insertClient):
            return redirect('login')
        
    return render(request, 'signup.html', context)
