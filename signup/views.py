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
        
        insertEmailQuery = "Insert into users(username) values(%s)"
        errorMsg = "Cannot insert user into db"
        param = (email,)
        insertEmail = db.insertPrepared(insertEmailQuery, param, errorMsg)

        #selecting id of user currently inserted
        selectQuery = "select id from users where username = (%s)"
        param = (email,)
        row = db.selectPrepared(selectQuery, param, errorMsg)
        id = str(row[0][0])

        #insert password and client type in login table
        insertPasswordQuery = "Insert into login(id, password, type) values((%s), (%s), (%s))"
        param = (id,password, usertype)
        insertPassword = db.insertPrepared(insertPasswordQuery, param, errorMsg)

        insertClientQuery = "Insert into client values((%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s))"
        insertTraderQuery = "Insert into trader values((%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s))"
        userType = "silver"
        insertClient = insertTrader = False
        if usertype == "client":
            param = (id, firstName, lastName, state, city, street, zip, phoneNumber, cellNumber, userType)
            insertClient = db.insertPrepared(insertClientQuery, param, errorMsg)
            insertQuery = "Insert into portfolio values((%s),(%s), (%s))"
            btcAmount=0
            totalAmount=0
            btcBalance=0
            param = (id, btcAmount, totalAmount)
            errorMsg = "could not add portfolio"
            insertPortfolio = db.insertPrepared(insertQuery, param, errorMsg)
        elif usertype == "trader":
            param = param = (id, firstName, lastName, state, city, street, zip, phoneNumber, cellNumber)
            insertTrader = db.insertPrepared(insertTraderQuery, param, errorMsg)
        
        

        
        
        insertWalletQuery = "Insert into wallet values((%s),(%s), (%s))"
        btcAmount=0
        btcBalance=0
        param = (id, btcAmount, btcBalance)
        errorMsg = "could not add wallet"

        insertWallet = db.insertPrepared(insertWalletQuery, param, errorMsg)

        if  insertWalletQuery and insertEmail and insertPassword and (insertTrader or insertClient):
            return redirect('login')
        
    return render(request, 'signup.html', context)
