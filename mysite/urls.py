"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.http import HttpResponse
from bot import run_bot
import threading 

def home(request):

    

    return HttpResponse("<h1>Chào mừng bạn đến với trang web của tôi!</h1>")

def admin_urls():
    threading.Thread(target=run_bot).start()
    return admin.site.urls

urlpatterns = [
    path('admin/', admin_urls()),
]
