"""ansigger URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from ansigger import views
from django.urls import path, re_path

urlpatterns = [
    re_path(r"^ansible/([\w\d\-_]+)$", views.ansible, name="ansible"),
    re_path(r"^job/([\w\d\-_]+)$", views.job, name="log"),
    re_path(r"^job/([\w\d\-_]+)/html$", views.job_html, name="log-html"),
    path("", views.index),
]
