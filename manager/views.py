from django.shortcuts import render, redirect
from login.models import DB
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
        selectQuery = "select password from manager where username=(%s)"
        param = (username,)
        errorMsg = "No matching entry found"
        row = db.selectPrepared(selectQuery, param, errorMsg)
        if row:
            if row[0][0] == password:
                context["success"] = True
                request.session['userId'] = "manager"
                request.session['userType'] = "manager"
                response = redirect('/managerhome/')
                return response
    return render(request,'managerlogin.html',context)

def managerhomeView(request):
    if request.session.get("userType"):
        context = {
            "clientCount" : -1,
            "traderCount" : 0,
            "totalCommission": 0
            }
        db = DB()
        selectQuery = "select count(*) from client;"
        errorMsg = "Unable to fetch data."
        row = db.select(selectQuery,errorMsg)
        context["clientCount"]=row[0][0]
        selectQuery = "select count(*) from trader;"
        row = db.select(selectQuery,errorMsg)
        context["traderCount"]=row[0][0]
        selectQuery = "select sum(commissionAmount) from transaction;"
        row = db.select(selectQuery,errorMsg)
        if(row[0][0]):
            context["totalCommission"]=row[0][0]
        return render(request, 'managerhomePage.html',context)
    else:
        return render(request, "managerlogin.html")

def managertransactionView(request):
    if request.session.get("userType"):
        return render(request, 'managerTransaction.html')
    else:
        return redirect("/")
