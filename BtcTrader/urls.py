"""BtcTrader URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from login import views as loginViews
from signup import views as signupViews
from client import views as clientViews
from trader import views as traderViews
from manager import views as managerViews
from transactions import views as transactionsViews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', loginViews.loginView, name='login'),
    path('logout/', loginViews.logout, name='logout'),
    path('signup/', signupViews.signupView),
    
    #common
    path('editProfile/', clientViews.editProfileView, name='editProfile'),
    path('buy/', clientViews.buyView, name='buy'),
    path('sell/', clientViews.sellView, name='sell'),

    #client
    path('home/', clientViews.homeView, name='home'),
    
    path('wallet/', clientViews.walletView, name='wallet'),
    path('transactionHistory/', clientViews.transactionHistoryView, name='transactionHistory'),
    path('searchTrader/',clientViews.searchTraderView, name='searchTrader'),

    #trader

    path('traderTransactionHistory/', traderViews.transactionHistoryView, name='traderTransaction'),
    path('viewClients/', traderViews.viewClients),


    #manager
    path('managerlogin/', managerViews.managerloginView, name='manager'),
    path('managerhome/', managerViews.managerhomeView, name='manager'),
    path('managerTransactions/', managerViews.managertransactionView, name='manager'),

    #transactions
    path('transactions/', transactionsViews.viewtransaction, name='transactions'),
]
