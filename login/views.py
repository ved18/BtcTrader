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
    request.session['loggedIn'] = False

    db = DB()
    if request.POST.get("Login"):
        context["loginSubmit"] = True
        username = str(request.POST.get('username'))
        password = str(request.POST.get('password'))

        print(username, password)

        #find id first

        selectIdQuery = "select id from users where username=(%s)"
        param = (username,)
        errorMsg = "No id found for the given username"

        rowId = db.selectPrepared(selectIdQuery, param, errorMsg)
        if rowId:
            id = rowId[0][0]
            context["id"] = str(id)


            selectQuery = "select password from login where id=(%s)"
            param = (id,)
            row = db.selectPrepared(selectQuery, param, errorMsg)
            if row:
                if row[0][0] == password:
                    context["success"] = True
                    selectTypeQuery = "select type from login where id=(%s)"
                    param = (id,)
                    errorMsg = "could not select type"

                    row = db.selectPrepared(selectTypeQuery, param, errorMsg)

                    if row:
                        context["type"] = row[0][0]
                        #add session variables here
                        request.session['userType'] = context["type"]
                        request.session["userId"] = context["id"]
                        request.session["loggedIn"] = True

                    if context["type"] == 'client':
                        return redirect('home/')
                    else:
                        return redirect('traderTransaction')

    return render(request, 'login.html', context)

def logout(request):
    try:
        del request.session['userId']
        return render(request,'logout.html')
    except:
        print("There was an error logging you out")