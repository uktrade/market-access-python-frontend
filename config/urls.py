"""market_access_python_frontend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from pingdom.urls import urlpatterns as pingdom_urlpatterns

urlpatterns = []

if settings.DEBUG and settings.DJANGO_ENV == "local":
    urlpatterns += [
        path("admin/", admin.site.urls),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    path("", include("users.urls", namespace="users")),
    path("", include("barriers.urls", namespace="barriers")),
    path("", include("reports.urls", namespace="reports")),
    path("", include("core.urls", namespace="core")),
    path("", include("healthcheck.urls", namespace="healthcheck")),
] + pingdom_urlpatterns
