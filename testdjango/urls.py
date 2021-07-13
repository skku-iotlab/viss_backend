"""testdjango URL Configuration

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
# work 1:
from viss.data_generator import *
getVehicleData()


# work 2: websocket integration 
import threading
from viss.websocket import *

loop = asyncio.get_event_loop()
start_server = websockets.serve(accept, "127.0.0.1", 3001)   

def Websocket_thread():
    print('websocket_thread_initialized')
    loop.run_until_complete(start_server)
    loop.run_forever()

# threading.Thread(target=Websocket_thread, args=()).start()


# work 3: urls
from django.urls import path,include, re_path
from rest_framework_simplejwt import views as jwt_views

from django.contrib import admin
from viss.views import Vehicle
from viss.views import Vehicle_AverageSpeed

app_name='viss'
urlpatterns = [
    path('admin', admin.site.urls),
    path('api/token', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('Vehicle/AverageSpeed',  Vehicle_AverageSpeed, name='Vehicle_AverageSpeed'),
    re_path(r'Vehicle*', Vehicle, name='Vehicle')
]

