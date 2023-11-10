"""
URL configuration for telemetr3 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('find_managers/<str:category_name>', views.find_managers, name='find_managers'),
    path('advertising_channels_test/', views.advertising_channels_test, name='advertising_channels_test'),
    path('get_channels/', views.get_channels, name='get_channels'),
    path('set_managers/', views.set_managers, name='set_managers'),
]
