from django.urls import path, include
from .views import *
from APP import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', Home.as_view(), name = 'home'),
    path('app/<str:pk>', App.as_view(), name = 'app'),
    path('register-app', Register_App.as_view(), name = 'register-app'),
    path('user-apps', User_Apps.as_view(), name = 'user-apps'),
    path('update-app/<str:pk>', Update_App.as_view(), name = 'update-app')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
