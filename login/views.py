from django.shortcuts import render, redirect
from .models import DB
from django.template import context

# Create your views here.

def loginView(request):
    context = {
        "loginSubmit" : False,
        "success" : False,
    }

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
            selectQuery = "select password from login where id=" + str(id) + ";"
            row = db.select(selectQuery, errorMsg)
            if row[0][0] == password:
                context["success"] = True
                return redirect('home')

    return render(request, 'login.html', context)

