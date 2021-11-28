from django.shortcuts import render, redirect
from .models import DB
from django.template import context
from django.contrib.auth import authenticate, login, logout

# Create your views here.

def loginView(request):
    context = {
        "loginSubmit" : False,
        "success" : False,
        "id" : "",
        "type" : "",
    }
    logout(request)

    db = DB()


    if request.POST.get("Login"):
        context["loginSubmit"] = True
        username = str(request.POST.get('username'))
        password = str(request.POST.get('password'))

        print(username, password)

        #find id first
        selectIdQuery = "select id from users where username= '" + username + "';"
        errorMsg = "No id found for the given username"
        rowId = db.select(selectIdQuery, errorMsg)
 
        if rowId:
            id = rowId[0][0]
            context["id"] = str(id)
            selectQuery = "select password from login where id=" + str(id) + ";"
            row = db.select(selectQuery, errorMsg)
            if row[0][0] == password:
                context["success"] = True
                selectTypeQuery = "select type from login where id=" + str(id) +";"
                errorMsg = "could not select type"

                row = db.select(selectTypeQuery, errorMsg)
    
                if row:
                    context["type"] = row[0][0]
                
                if context["type"] == 'client':
                    return render(request, 'homePage.html', context)
                else:
                    return render(request, 'traderTransactionHistory.html', context)

    return render(request, 'login.html', context)