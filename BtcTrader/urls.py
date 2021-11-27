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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', loginViews.loginView, name='login'),
    path('signup/', signupViews.signupView),
    

    #client
    path('home/<int:id>/', clientViews.homeView, name='home'),
    path('editProfile/<int:id>', clientViews.editProfileView, name='editProfile'),
]
