from django.urls import path

from pingdom.views import pingdom

urlpatterns = [
    path("pingdom/ping.xml", pingdom, name="pingdom"),
]
