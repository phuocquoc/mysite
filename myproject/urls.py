from django.contrib import admin
from django.urls import path
from django.urls import path
from django.http import HttpResponse

# Tạo một view đơn giản cho trang chủ
def home(request):
    return HttpResponse("Welcome to the Django app on Heroku!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Đường dẫn cho trang chủ
]
