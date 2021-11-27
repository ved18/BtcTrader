from django.shortcuts import render
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
        selectQuery = "select password from login where id = (select id from users where username = '" + username + "');"
        errorMsg = "No user found for the given username"

        row = db.select(selectQuery, errorMsg)

        if row[0][0] == password:
            context["success"] = True
            return render(request, 'login.html', context)

    return render(request, 'login.html', context)