from django.shortcuts import render, redirect
from .models import DB
from django.template import context
from django.contrib.auth import authenticate, login, logout

# Create your views here.

def managerloginView(request):
    context = {
        "loginSubmit" : False,
        "success" : False,
    }
    logout(request)

    db = DB()
    if request.POST.get("Login"):
        context["loginSubmit"] = True
        username = str(request.POST.get('username'))
        password = str(request.POST.get('password'))
        # print(username, password)
        selectQuery = "select password from manager where username='" + username + "';"
        errorMsg = "No matching entry found"
        row = db.select(selectQuery,errorMsg)
        if row[0][0] == password:
            context["success"] = True
            response = redirect('/managerhome/')
            return response
    return render(request,'managerlogin.html',context)

def managerhomeView(request):
    context = {
        "clientCount" : 0,
        "traderCount" : 0,
        "totalCommission": 0

    }
    db = DB()
    selectQuery = "select count(*) from client;"
    errorMsg = "Unable to fetch data."
    row = db.select(selectQuery,errorMsg)
    context["clientCount"]=row[0][0]
    print(context["clientCount"])
    selectQuery = "select count(*) from trader;"
    row = db.select(selectQuery,errorMsg)
    context["traderCount"]=row[0][0]
    print(context["traderCount"])
    selectQuery = "select sum(commissionAmount) from transaction;"
    row = db.select(selectQuery,errorMsg)
    if(row[0][0]):
        context["totalCommission"]=row[0][0]
    print(context["totalCommission"])
    return render(request, 'managerhomePage.html',context)

def managertransactionView(request):
    db = DB()
    selectQuery = "SELECT * from transaction WHERE date >= DATE(NOW()) + INTERVAL -6 DAY AND date <  NOW() + INTERVAL  0 DAY"
    errorMsg = "Unable to fetch data."
    row = db.select(selectQuery,errorMsg)
    print(row)
    # if(row):
    #     context["totalCommission"]=row[0][0]
    # print(context["totalCommission"])
    return render(request, 'managerTransaction.html')